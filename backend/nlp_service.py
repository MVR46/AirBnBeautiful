"""
NLP Search Service: Semantic search with amenity clustering and hybrid ranking.
Based on Feature 1 notebook (cells 14-26).
"""

import numpy as np
import pandas as pd
import re
import unicodedata
import dateparser
from typing import List, Tuple, Optional, Dict, Any
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import spacy
import torch
import os


# Global models (loaded at startup)
nlp = None
embed_model = None
tfidf_vec = None
X_tfidf = None

# Global amenity data structures
ALL_AMEN_TOKENS = []
E_ALL_AMEN = None
AMEN_CLUSTER_ID = {}
CLUSTER_CANON = {}
AMEN_CANON = {}
CANON_LIST = []
E_CANON = None
CANON_MEMBERS = {}
CANON_TOKENS = {}
CANON_MERGE = {}

# Label pools for neighborhoods, groups, types
neigh_vals = []
group_vals = []
room_vals = []
prop_vals = []
neigh_norm = []
group_norm = []
room_norm = []
prop_norm = []
E_NEIGH = None
E_GROUP = None
E_ROOM = None
E_PROP = None
group_to_neigh = {}
neigh_to_group = {}
ROOM_CONTENT_TOKENS = {}
PROP_CONTENT_TOKENS = {}


def init_nlp_models():
    """Initialize NLP models at startup."""
    global nlp, embed_model
    
    # Set environment for faster CPU inference
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["OMP_NUM_THREADS"] = "1"
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"NLP Device: {device}")
    
    # Load spaCy
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        print("Downloading spaCy model...")
        from spacy.cli import download
        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    
    # Load sentence transformer
    embed_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
    print(f"Loaded sentence-transformers (dim={embed_model.get_sentence_embedding_dimension()})")


def strip_accents(s: str) -> str:
    """Remove accents from string."""
    if not isinstance(s, str):
        return ''
    return ''.join(ch for ch in unicodedata.normalize('NFD', s) 
                   if unicodedata.category(ch) != 'Mn')


def norm_txt(s: str) -> str:
    """Normalize text: lowercase, strip accents, collapse whitespace."""
    s = strip_accents(str(s)).lower().strip()
    return re.sub(r'\s+', ' ', s)


def content_tokens(s: str):
    """Extract content tokens from text (no stopwords or generic terms)."""
    toks = re.findall(r"[a-zA-Z0-9]+", norm_txt(s))
    STOP = nlp.Defaults.stop_words
    GENERIC = {"city", "center", "centre", "view", "area", "place", "space", 
               "access", "daily", "day", "night", "room"}
    return {t for t in toks if len(t) >= 3 and t not in STOP and t not in GENERIC}


def enc_norm_list(xs: list) -> np.ndarray:
    """Encode list of strings to normalized embeddings."""
    if not xs:
        return np.zeros((0, embed_model.get_sentence_embedding_dimension()), dtype=np.float32)
    v = embed_model.encode(xs, show_progress_bar=False, normalize_embeddings=True)
    return np.asarray(v, dtype=np.float32)


def build_amenity_clusters(df: pd.DataFrame):
    """Build amenity canonical labels using clustering (notebook cell 16)."""
    global ALL_AMEN_TOKENS, E_ALL_AMEN, AMEN_CLUSTER_ID, CLUSTER_CANON
    global AMEN_CANON, CANON_LIST, E_CANON, CANON_MEMBERS, CANON_TOKENS, CANON_MERGE
    
    # Extract all amenity tokens
    all_tokens = set()
    for row in df['amenities_norm']:
        if row:
            all_tokens.update([norm_txt(x) for x in row if x])
    
    ALL_AMEN_TOKENS = sorted(all_tokens)
    print(f"Found {len(ALL_AMEN_TOKENS)} unique amenity tokens")
    
    if len(ALL_AMEN_TOKENS) == 0:
        return
    
    # Embed amenities
    E_ALL_AMEN = enc_norm_list(ALL_AMEN_TOKENS)
    
    # Cluster into families
    M = len(ALL_AMEN_TOKENS)
    K = min(300, max(60, M // 8))
    print(f"Clustering into {K} families...")
    
    kmeans = KMeans(n_clusters=K, n_init=10, random_state=42)
    amen_labels = kmeans.fit_predict(E_ALL_AMEN)
    centroids = kmeans.cluster_centers_
    centroids = (centroids / np.linalg.norm(centroids, axis=1, keepdims=True)).astype(np.float32)
    
    AMEN_CLUSTER_ID = {tok: int(cid) for tok, cid in zip(ALL_AMEN_TOKENS, amen_labels)}
    
    # Frequency count for selecting canonical names
    tok_freq = Counter()
    for row in df['amenities_norm']:
        if row:
            tok_freq.update([norm_txt(x) for x in row if x])
    
    # Group by cluster and pick most frequent as canonical
    cluster_members = {}
    for tok, cid in AMEN_CLUSTER_ID.items():
        cluster_members.setdefault(cid, []).append(tok)
    
    CLUSTER_CANON = {}
    AMEN_CANON = {}
    for cid, toks in cluster_members.items():
        toks_sorted = sorted(toks, key=lambda t: (-tok_freq.get(t, 0), len(t)))
        canon = toks_sorted[0]
        CLUSTER_CANON[cid] = canon
        for t in toks:
            AMEN_CANON[t] = canon
    
    CANON_LIST = [CLUSTER_CANON[cid] for cid in sorted(CLUSTER_CANON.keys())]
    E_CANON = centroids[np.array(sorted(CLUSTER_CANON.keys()))].astype(np.float32)
    
    # Canon members
    for tok, canon in AMEN_CANON.items():
        CANON_MEMBERS.setdefault(canon, set()).add(tok)
    
    # Token bags for lexical gates
    CANON_TOKENS = {c: content_tokens(c) for c in CANON_LIST}
    
    # Build merge dict for near-duplicates
    GENERIC_MODIFIERS = {"standard", "estandar", "basic", "regular", "general"}
    
    def label_merge_key(label: str):
        toks = content_tokens(label)
        toks = {t for t in toks if t not in GENERIC_MODIFIERS}
        return tuple(sorted(toks)) if toks else (norm_txt(label),)
    
    def is_weird_unicode(label: str) -> bool:
        return bool(re.search(r'\\u[0-9a-fA-F]{4}', label))
    
    def _prefer_label(lbls):
        def sort_key(lbl):
            ascii_ok = all(ord(ch) < 128 for ch in lbl)
            freq = tok_freq.get(lbl, 0)
            return (
                0 if not is_weird_unicode(lbl) else 1,
                0 if ascii_ok else 1,
                -freq,
                len(lbl),
                norm_txt(lbl),
            )
        return sorted(lbls, key=sort_key)[0]
    
    _groups = {}
    for c in CANON_LIST:
        _groups.setdefault(label_merge_key(c), []).append(c)
    
    CANON_MERGE = {}
    for _, lbls in _groups.items():
        rep = _prefer_label(lbls)
        for l in lbls:
            CANON_MERGE[l] = rep
    
    print(f"Built {len(CANON_LIST)} canonical amenity families")


def build_label_pools(df: pd.DataFrame):
    """Build label pools and embeddings for neighborhoods, types (notebook cell 16)."""
    global neigh_vals, group_vals, room_vals, prop_vals
    global neigh_norm, group_norm, room_norm, prop_norm
    global E_NEIGH, E_GROUP, E_ROOM, E_PROP
    global group_to_neigh, neigh_to_group
    global ROOM_CONTENT_TOKENS, PROP_CONTENT_TOKENS
    
    neigh_vals = sorted(set(df['neighbourhood_cleansed'].dropna().astype(str)))
    group_vals = sorted(set(df['neighbourhood_group_cleansed'].dropna().astype(str)))
    room_vals = sorted(set(df['room_type'].dropna().astype(str)))
    prop_vals = sorted(set(df['property_type'].dropna().astype(str)))
    
    neigh_norm = [norm_txt(x) for x in neigh_vals]
    group_norm = [norm_txt(x) for x in group_vals]
    room_norm = [norm_txt(x) for x in room_vals]
    prop_norm = [norm_txt(x) for x in prop_vals]
    
    print(f"Label pools: {len(neigh_vals)} neighborhoods, {len(group_vals)} groups, "
          f"{len(room_vals)} room types, {len(prop_vals)} property types")
    
    # Encode
    E_NEIGH = enc_norm_list(neigh_norm)
    E_GROUP = enc_norm_list(group_norm)
    E_ROOM = enc_norm_list(room_norm)
    E_PROP = enc_norm_list(prop_norm)
    
    # Geography mapping
    df_geo = df[['neighbourhood_group_cleansed', 'neighbourhood_cleansed']].dropna().drop_duplicates()
    df_geo['g_norm'] = df_geo['neighbourhood_group_cleansed'].map(norm_txt)
    df_geo['n_norm'] = df_geo['neighbourhood_cleansed'].map(norm_txt)
    
    group_to_neigh = df_geo.groupby('g_norm')['n_norm'].apply(set).to_dict()
    neigh_to_group = {row.n_norm: row.g_norm for _, row in df_geo.iterrows()}
    
    # Content tokens for types
    ROOM_CONTENT_TOKENS = {lbl: content_tokens(lbl) for lbl in room_norm}
    PROP_CONTENT_TOKENS = {lbl: content_tokens(lbl) for lbl in prop_norm}


def build_tfidf_index(df: pd.DataFrame, texts: List[str]):
    """Build TF-IDF index for lexical ranking (notebook cell 24)."""
    global tfidf_vec, X_tfidf
    
    def simple_tokenize(s: str):
        s = norm_txt(s)
        return re.findall(r"[a-zA-Z0-9_]+", s)
    
    tfidf_vec = TfidfVectorizer(
        tokenizer=simple_tokenize,
        preprocessor=None,
        token_pattern=None,
        lowercase=False,
        min_df=2,
        max_features=200000
    )
    
    X_tfidf = tfidf_vec.fit_transform(texts)
    X_tfidf = normalize(X_tfidf, norm="l2", copy=False)
    print(f"Built TF-IDF index: {X_tfidf.shape}")


def prepare_amenities_norm(df: pd.DataFrame) -> pd.DataFrame:
    """Parse and normalize amenities column (notebook cell 11)."""
    def parse_amenities_to_list(a):
        # Handle None/NaN
        if a is None or (isinstance(a, float) and pd.isna(a)):
            return []
        # If already a list, use it directly
        if isinstance(a, list):
            return [str(x).strip().lower() for x in a if x]
        # Otherwise parse as string
        s = str(a).strip()
        s = s.replace('[', '').replace(']', '').replace('{', '').replace('}', '')
        parts = [p.strip().strip('"').strip("'").lower() for p in s.split(',') if p.strip() != '']
        # Deduplicate
        seen, out = set(), []
        for p in parts:
            if p not in seen:
                seen.add(p)
                out.append(p)
        return out
    
    df = df.copy()
    df['amenities_norm'] = df['amenities'].apply(parse_amenities_to_list)
    return df


# ===== Query Parsing (notebook cells 18-20) =====

def extract_price_range_en(text: str) -> Tuple[Optional[float], Optional[float]]:
    """Extract price range from English text."""
    t = norm_txt(text)
    CUR = r"(?:€|\$|eur|usd|euros?|dollars?)"
    
    # Between X and Y
    m = re.search(rf"(?:between|from)\s*{CUR}?\s*(\d{{2,6}})\s*(?:and|to|-)\s*{CUR}?\s*(\d{{2,6}})", t)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        return (min(lo, hi), max(lo, hi))
    
    # Up to / under / max / less than
    m = re.search(rf"(?:up to|under|below|less than|max(?:imum)?|cheaper than)\s*{CUR}?\s*(\d{{2,6}})", t)
    if m:
        return (None, float(m.group(1)))
    
    # Minimum / at least / more than
    m = re.search(rf"(?:at least|min(?:imum)?|more than|above|over)\s*{CUR}?\s*(\d{{2,6}})", t)
    if m:
        return (float(m.group(1)), None)
    
    # Per night or budget X
    m = re.search(rf"(?:{CUR}?\s*(\d{{2,6}})\s*(?:per\s*night|/night)|budget\s*{CUR}?\s*(\d{{2,6}}))", t)
    if m:
        price = float(m.group(1) or m.group(2))
        return (None, price)
    
    # Just currency amount (e.g., "€100" or "100 euros")
    m = re.search(rf"(?:{CUR}\s*(\d{{2,6}})|(\d{{2,6}})\s*{CUR})", t)
    if m:
        price = float(m.group(1) or m.group(2))
        return (None, price)
    
    return (None, None)


def extract_guests_nights_en(text: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract guests and nights from text."""
    t = norm_txt(text)
    g = re.search(r"(\d{1,3})\s*(?:guests?|people|adults|persons?)", t)
    n = re.search(r"(\d{1,3})\s*(?:nights?)", t)
    return (int(g.group(1)) if g else None, int(n.group(1)) if n else None)


def maybe_parse_dates_en(text: str) -> Tuple[Optional[pd.Timestamp], Optional[pd.Timestamp], Optional[int]]:
    """Parse date ranges."""
    m = re.search(r"from\s+([^\n,;]+?)\s+to\s+([^\n,;]+)", text, flags=re.IGNORECASE)
    if m:
        d1 = dateparser.parse(m.group(1), languages=['en'])
        d2 = dateparser.parse(m.group(2), languages=['en'])
        if d1 and d2:
            d1 = pd.to_datetime(d1).normalize()
            d2 = pd.to_datetime(d2).normalize()
            if d2 <= d1:
                d2 = d1 + pd.Timedelta(days=1)
            return d1, d2, int((d2 - d1).days)
    return None, None, None


def noun_phrases_and_ngrams(text: str) -> List[str]:
    """Extract noun phrases and n-grams using spaCy."""
    doc = nlp(text)
    chunks = [nc.text for nc in doc.noun_chunks]
    toks = [t.text for t in doc if t.pos_ in {"NOUN", "PROPN"} and not t.is_stop]
    bigrams = [' '.join([toks[i], toks[i+1]]) for i in range(len(toks)-1)]
    cands = list(dict.fromkeys(chunks + toks + bigrams))
    return [c for c in cands if c.strip()]


def best_two(a: np.ndarray) -> Tuple[int, float, float]:
    """Get index and values of top 2 elements."""
    if a.size == 0:
        return -1, -1.0, -1.0
    j = int(np.argmax(a))
    m1 = float(a[j])
    if a.size == 1:
        return j, m1, -1.0
    b = a.copy()
    b[j] = -np.inf
    m2 = float(b.max())
    return j, m1, m2


def canonical_amenities_from_query(query: str, th_abs: float = 0.60, 
                                   th_margin: float = 0.06) -> List[str]:
    """Extract canonical amenities from query (notebook cell 18)."""
    if not CANON_LIST:
        return []
    
    phrases = noun_phrases_and_ngrams(query)
    if not phrases:
        return []
    
    phrases_norm = [norm_txt(p) for p in phrases]
    Q = embed_model.encode(phrases_norm, normalize_embeddings=True)
    sims = Q @ E_CANON.T
    
    q_tokens = content_tokens(query)
    hits = set()
    
    for i, p in enumerate(phrases):
        j, m1, m2 = best_two(sims[i])
        if j < 0:
            continue
        
        canon = CANON_LIST[j]
        canon_tokens = CANON_TOKENS.get(canon, set())
        phrase_tokens = content_tokens(p)
        
        # Semantic + lexical gate on phrase
        if m1 >= th_abs and (m2 < 0 or m1 - m2 >= th_margin):
            if phrase_tokens & canon_tokens:
                hits.add(canon)
                continue
        
        # Fallback: lexical gate on full query
        if q_tokens & canon_tokens:
            hits.add(canon)
    
    if not hits:
        return []
    
    # Merge near-duplicates
    merged = {CANON_MERGE.get(h, h) for h in hits}
    
    # Clean up
    key_to_lbls = {}
    for h in merged:
        def label_merge_key(label: str):
            toks = content_tokens(label)
            GENERIC_MODIFIERS = {"standard", "estandar", "basic", "regular", "general"}
            toks = {t for t in toks if t not in GENERIC_MODIFIERS}
            return tuple(sorted(toks)) if toks else (norm_txt(label),)
        key_to_lbls.setdefault(label_merge_key(h), []).append(h)
    
    cleaned = set()
    for key, lbls in key_to_lbls.items():
        if len(lbls) == 1:
            cleaned.add(lbls[0])
        else:
            # Pick cleanest
            def _prefer(lbl):
                ascii_ok = all(ord(ch) < 128 for ch in lbl)
                return (0 if ascii_ok else 1, len(lbl), norm_txt(lbl))
            cleaned.add(sorted(lbls, key=_prefer)[0])
    
    ordered = sorted(cleaned, key=lambda lbl: (
        0 if all(ord(ch) < 128 for ch in lbl) else 1,
        len(lbl),
        norm_txt(lbl)
    ))
    
    return ordered


def neighborhoods_groups_from_query(query: str, thr_neigh: float = 0.68,
                                   thr_group: float = 0.60) -> Tuple[List[str], List[str]]:
    """Extract neighborhoods and groups from query (notebook cell 18)."""
    phrases = noun_phrases_and_ngrams(query) + [query]
    phrases_norm = [norm_txt(p) for p in phrases]
    Q = embed_model.encode(phrases_norm, normalize_embeddings=True)
    
    neighs, groups = set(), set()
    
    for v, raw in zip(Q, phrases):
        # Groups
        s_g = v @ E_GROUP.T
        jg, g1, g2 = best_two(s_g)
        if g1 >= thr_group:
            groups.add(group_norm[jg])
        
        # Neighborhoods
        s_n = v @ E_NEIGH.T
        jn, n1, n2 = best_two(s_n)
        if n1 >= thr_neigh and (n2 < 0 or n1 - n2 >= 0.06):
            if content_tokens(raw) & set(re.findall(r"[a-z0-9]+", neigh_norm[jn])):
                neighs.add(neigh_norm[jn])
    
    # Lexical fallback
    qn = norm_txt(query)
    for g in group_norm:
        if g in qn:
            groups.add(g)
    for n in neigh_norm:
        if n in qn:
            neighs.add(n)
    
    # Filter neighborhoods by groups
    if groups:
        allowed = set().union(*[group_to_neigh.get(g, set()) for g in groups])
        neighs = {n for n in neighs if n in allowed}
    
    return list(neighs), list(groups)


def type_from_query_by_centroid(query: str, labels_norm: List[str], E: np.ndarray,
                                TOKENS_MAP: Dict[str, set], th_abs: float = 0.60,
                                th_margin: float = 0.05) -> Optional[str]:
    """Detect room/property type from query (notebook cell 18)."""
    phrases = noun_phrases_and_ngrams(query) + [query]
    if not phrases:
        return None
    
    P_norm = [norm_txt(p) for p in phrases]
    Q = embed_model.encode(P_norm, normalize_embeddings=True)
    qtok = content_tokens(query)
    
    best_label, best_score = None, -1.0
    
    for i, raw in enumerate(phrases):
        sims = Q[i] @ E.T
        j, m1, m2 = best_two(sims)
        if j < 0:
            continue
        
        lbl = labels_norm[j]
        gate_tokens = TOKENS_MAP.get(lbl, set())
        
        if (m1 >= th_abs) and (m2 < 0 or m1 - m2 >= th_margin):
            if content_tokens(raw) & gate_tokens or qtok & gate_tokens:
                if m1 > best_score:
                    best_label, best_score = lbl, m1
    
    return best_label


def parse_user_query_ml(query: str) -> Dict[str, Any]:
    """Full query parser combining all extractors (notebook cell 18)."""
    amenities_canon = canonical_amenities_from_query(query)
    neighbourhoods, neigh_groups = neighborhoods_groups_from_query(query)
    
    room_type = type_from_query_by_centroid(
        query, room_norm, E_ROOM, ROOM_CONTENT_TOKENS, th_abs=0.58, th_margin=0.05
    )
    property_type = type_from_query_by_centroid(
        query, prop_norm, E_PROP, PROP_CONTENT_TOKENS, th_abs=0.58, th_margin=0.05
    )
    
    guests, nights = extract_guests_nights_en(query)
    price_min, price_max = extract_price_range_en(query)
    checkin, checkout, nights_dates = maybe_parse_dates_en(query)
    
    if nights is None and nights_dates is not None:
        nights = nights_dates
    
    # Determine location string for frontend
    location_str = None
    if neigh_groups:
        location_str = neigh_groups[0].title()  # e.g., "Centro"
    elif neighbourhoods:
        location_str = neighbourhoods[0].title()  # e.g., "Salamanca"
    
    # Build price_range tuple for frontend
    price_range = None
    if price_min is not None and price_max is not None:
        price_range = [price_min, price_max]
    elif price_max is not None:
        price_range = [0, price_max]
    elif price_min is not None:
        price_range = [price_min, 9999]
    
    return {
        "raw_query": query,
        # Backend internal fields (for filtering)
        "amenities_all": amenities_canon,
        "neighbourhoods": neighbourhoods,
        "neigh_groups": neigh_groups,
        "room_type": room_type,
        "property_type": property_type,
        "guests": guests,
        "nights": nights,
        "price_min": price_min,
        "price_max": price_max,
        "checkin": str(checkin) if checkin else None,
        "checkout": str(checkout) if checkout else None,
        # Frontend display fields (for UI)
        "location": location_str,
        "amenities": amenities_canon,
        "price_range": price_range,
    }


# ===== Filtering and Ranking (notebook cells 20, 24) =====

def amenities_family_satisfied(list_canon: List[str], required_canon: List[str]) -> bool:
    """Check if listing has required amenities."""
    if not required_canon:
        return True
    if not list_canon:
        return False
    aset = set(list_canon)
    return all(rc in aset for rc in required_canon)


def apply_filters_ml(df: pd.DataFrame, spec: Dict[str, Any]) -> pd.DataFrame:
    """Apply filters to DataFrame (notebook cell 20)."""
    m = pd.Series(True, index=df.index)
    
    if spec.get('neigh_groups'):
        m &= df['neighbourhood_group_cleansed'].astype(str).map(norm_txt).isin(spec['neigh_groups'])
    
    if spec.get('neighbourhoods'):
        m &= df['neighbourhood_cleansed'].astype(str).map(norm_txt).isin(spec['neighbourhoods'])
    
    if spec.get('guests') is not None:
        m &= df['accommodates'] >= spec['guests']
    
    if spec.get('nights') is not None:
        if {'minimum_nights', 'maximum_nights'}.issubset(df.columns):
            m &= (df['minimum_nights'] <= spec['nights']) & (df['maximum_nights'] >= spec['nights'])
    
    if spec.get('price_min') is not None:
        m &= df['price'] >= spec['price_min']
    if spec.get('price_max') is not None:
        m &= df['price'] <= spec['price_max']
    
    if spec.get('room_type') is not None:
        m &= df['room_type'].astype(str).map(norm_txt) == norm_txt(spec['room_type'])
    
    if spec.get('property_type') is not None:
        m &= df['property_type'].astype(str).map(norm_txt).str.contains(
            norm_txt(spec['property_type']), regex=False
        )
    
    if spec.get('amenities_all'):
        if 'amenities_canon' not in df.columns:
            raise ValueError("amenities_canon column missing")
        m &= df['amenities_canon'].apply(
            lambda xs: amenities_family_satisfied(xs or [], spec['amenities_all'])
        )
    
    if 'has_availability' in df.columns:
        m &= df['has_availability'] == True
    
    return df.loc[m].copy()


def lexical_similarities(query: str) -> np.ndarray:
    """Compute TF-IDF lexical similarities."""
    qv = tfidf_vec.transform([query])
    qv = normalize(qv, norm="l2", copy=False)
    sims = (X_tfidf @ qv.T).toarray().ravel()
    if sims.size and sims.max() > sims.min():
        sims = (sims - sims.min()) / (sims.max() - sims.min())
    return sims.astype(np.float32)


def rerank_semantic_with_lex(candidates: pd.DataFrame, query: str, 
                             listing_embeddings: np.ndarray,
                             w_sem=0.55, w_lex=0.20, w_rating=0.15, 
                             w_price=0.10) -> pd.DataFrame:
    """Hybrid reranking: semantic + lexical + rating + price (notebook cell 24)."""
    if candidates.empty:
        return candidates
    
    # Semantic similarity
    qv = embed_model.encode([norm_txt(query)], normalize_embeddings=True)[0].astype('float32')
    sem = (listing_embeddings[candidates.index.values] @ qv)
    sem = np.clip((sem + 1) / 2, 0, 1)
    
    # Lexical similarity
    lex_all = lexical_similarities(query)
    lex = lex_all[candidates.index.values]
    
    # Rating (normalize to 0-1)
    rating = candidates.get('review_scores_rating', pd.Series(0.0, index=candidates.index)).fillna(0.0) / 100.0
    
    # Price (inverse, prefer cheaper)
    ppg = candidates.get('price_per_guest', pd.Series(np.nan, index=candidates.index))
    ppg = ppg.fillna(candidates['price'] / candidates['accommodates'].replace(0, np.nan))
    pmin, pmax = ppg.min(), ppg.max()
    price = ((ppg - pmin) / (pmax - pmin + 1e-9)).clip(0, 1)
    
    # Combined score
    score = w_sem * sem + w_lex * lex + w_rating * rating + w_price * (1.0 - price)
    
    out = candidates.copy()
    out['__score'] = score
    out = out.sort_values(['__score', 'review_scores_rating', 'price'],
                         ascending=[False, False, True], kind='mergesort')
    return out.drop(columns=['__score'])

