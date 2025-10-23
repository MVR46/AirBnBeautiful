"""
FastAPI backend for Airbnb ML Demo (Madrid).
Integrates NLP search, RAG chat, CV amenity detection, and price optimization.
"""

# CRITICAL: Load .env FIRST before any other imports that might read environment variables
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pandas as pd
import numpy as np
import os
import asyncio
import time
import gc
import psutil
from functools import lru_cache
from typing import Tuple

# Import models
from models import (
    SearchRequest, SearchResponse, Listing,
    NeighborhoodChatRequest, NeighborhoodChatResponse,
    PrefillListing, Photo,
    AmenitiesFromImagesRequest, AmenitiesFromImagesResponse,
    PriceSuggestionsRequest, PriceSuggestionsResponse
)

# Import services
from data_service import DataService, NEIGHBORHOOD_DATA
import nlp_service
import rag_service
import cv_service
import price_service


# Global state
data_service = None
df_listings = None
listing_texts = None
listing_embeddings = None

# Query cache for performance
@lru_cache(maxsize=50)
def cached_parse_query(query: str) -> Tuple:
    """Cache parsed queries to avoid recomputation."""
    spec = nlp_service.parse_user_query_ml(query)
    # Convert to tuple for caching (dict not hashable)
    return (
        tuple(spec.get('amenities_all', [])),
        tuple(spec.get('neighbourhoods', [])),
        tuple(spec.get('neigh_groups', [])),
        spec.get('room_type'),
        spec.get('property_type'),
        spec.get('guests'),
        spec.get('price_min'),
        spec.get('price_max'),
        spec
    )

def get_memory_usage() -> dict:
    """Get current memory usage statistics."""
    process = psutil.Process()
    mem_info = process.memory_info()
    return {
        "rss_mb": mem_info.rss / 1024 / 1024,
        "vms_mb": mem_info.vms / 1024 / 1024,
        "percent": process.memory_percent()
    }


# Sample photos for landlord prefill (using Unsplash images with visible amenities)
SAMPLE_PHOTOS = [
    {"id": "p1", "url": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=800&q=80"},  # Modern kitchen with appliances, oven, dishwasher visible
    {"id": "p2", "url": "https://images.unsplash.com/photo-1556912172-45b7abe8b7e1?w=800&q=80"},  # Kitchen with coffee maker, microwave, stove
    {"id": "p3", "url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80"},  # Living room with TV
    {"id": "p4", "url": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800&q=80"},  # Bathroom with fixtures
    {"id": "p5", "url": "https://images.unsplash.com/photo-1600210491892-03d54c0aaf87?w=800&q=80"},  # Laundry room with washer
    {"id": "p6", "url": "https://images.unsplash.com/photo-1556020685-ae41abfc9365?w=800&q=80"},  # Bedroom with workspace
    {"id": "p7", "url": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&q=80"},  # Balcony view
    {"id": "p8", "url": "https://images.unsplash.com/photo-1560448204-603b3fc33ddc?w=800&q=80"},  # Kitchen with refrigerator and dishwasher
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global data_service, df_listings, listing_texts, listing_embeddings
    
    import sys
    sys.stdout.flush()  # Force flush to see logs immediately
    
    print("\n" + "="*60, flush=True)
    print("Starting Airbnb ML Backend", flush=True)
    print("="*60, flush=True)
    
    # Initialize data service
    print("\n1. Loading listings database...", flush=True)
    data_service = DataService()
    df_listings = data_service.get_all_listings()
    print(f"   Loaded {len(df_listings)} listings", flush=True)
    
    # Initialize NLP models
    print("\n2. Initializing NLP models...", flush=True)
    nlp_service.init_nlp_models()
    print("   ✓ NLP models loaded", flush=True)
    
    # Prepare amenities for NLP
    print("\n3. Preparing amenity normalization...", flush=True)
    df_listings = nlp_service.prepare_amenities_norm(df_listings)
    print("   ✓ Amenities normalized", flush=True)
    
    # Build amenity clusters and label pools
    print("\n4. Building amenity clusters...", flush=True)
    nlp_service.build_amenity_clusters(df_listings)
    print("   ✓ Clusters built", flush=True)
    
    print("\n5. Building label pools (neighborhoods, types)...", flush=True)
    nlp_service.build_label_pools(df_listings)
    print("   ✓ Label pools ready", flush=True)
    
    # Prepare listing texts and embeddings
    print("\n6. Preparing listing embeddings...", flush=True)
    
    def _concat_text(row: pd.Series) -> str:
        name = str(row.get('name', '') or '').strip()
        desc = str(row.get('description', '') or '').strip()
        if not desc and 'neighborhood_overview' in row:
            desc = str(row.get('neighborhood_overview', '') or '').strip()
        txt = f"{name}. {desc}".strip()
        return txt if txt else name
    
    listing_texts = df_listings.apply(_concat_text, axis=1).tolist()
    print(f"   ✓ Prepared {len(listing_texts)} listing texts", flush=True)
    
    # Check for cached embeddings - use memory mapping for lower RAM usage
    emb_path = Path('data/listing_embeddings.npy')
    if emb_path.exists():
        try:
            # Memory-map the embeddings instead of loading fully into RAM
            listing_embeddings = np.load(emb_path, mmap_mode='r')
            print(f"   ✓ Memory-mapped cached embeddings: {listing_embeddings.shape}", flush=True)
            # Convert to writable array only when needed
            listing_embeddings = np.array(listing_embeddings, dtype='float32')
            print(f"   ✓ Loaded embeddings into memory: {listing_embeddings.nbytes / 1024 / 1024:.1f}MB", flush=True)
        except Exception as e:
            print(f"   ⚠ Failed to load cached embeddings: {e}", flush=True)
            listing_embeddings = None
    else:
        listing_embeddings = None
    
    if listing_embeddings is None:
        print("   Computing listing embeddings (this may take 2-3 minutes)...", flush=True)
        listing_embeddings = nlp_service.embed_model.encode(
            listing_texts,
            batch_size=32,  # Reduced batch size for memory efficiency
            show_progress_bar=True,
            normalize_embeddings=True
        ).astype('float32')
        
        # Cache for next time
        os.makedirs('data', exist_ok=True)
        np.save(emb_path, listing_embeddings)
        print(f"   ✓ Saved embeddings to {emb_path}", flush=True)
        
    # Force garbage collection after heavy initialization
    gc.collect()
    
    # Build TF-IDF index
    print("\n7. Building TF-IDF index...", flush=True)
    nlp_service.build_tfidf_index(df_listings, listing_texts)
    print("   ✓ TF-IDF index ready", flush=True)
    
    # Build amenities_canon column for filtering
    print("\n8. Building canonical amenities for filtering...", flush=True)
    df_listings['amenities_canon'] = df_listings['amenities_norm'].apply(
        lambda xs: sorted({nlp_service.AMEN_CANON.get(nlp_service.norm_txt(x))
                          for x in (xs or [])
                          if nlp_service.AMEN_CANON.get(nlp_service.norm_txt(x))})
    )
    print("   ✓ Canonical amenities ready", flush=True)
    
    # Initialize RAG service
    print("\n9. Initializing RAG service...", flush=True)
    rag_service.init_rag_service(nlp_service.embed_model, NEIGHBORHOOD_DATA)
    print("   ✓ RAG service ready", flush=True)
    
    # Train price model
    print("\n10. Training price optimization model...", flush=True)
    price_service.train_price_model(df_listings)
    print("   ✓ Price model trained", flush=True)
    
    # Final memory report
    final_mem = get_memory_usage()
    print("\n" + "="*60, flush=True)
    print("✅ Backend ready! All services initialized.", flush=True)
    print(f"📊 Memory usage: {final_mem['rss_mb']:.1f}MB ({final_mem['percent']:.1f}%)", flush=True)
    print("="*60 + "\n", flush=True)
    sys.stdout.flush()
    
    yield
    
    # Shutdown
    print("\nShutting down...")
    data_service.close()


app = FastAPI(
    title="Airbnb ML Backend",
    description="Machine Learning backend for Madrid Airbnb demo",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
# Get allowed origins from environment variable or use defaults
allowed_origins_str = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8080,http://localhost:5173,https://rbnbeautiful.casa,https://www.rbnbeautiful.casa"
)
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

# Add wildcard support for Vercel preview deployments
allow_origin_regex = os.getenv(
    "ALLOWED_ORIGINS_REGEX",
    r"https://.*\.vercel\.app"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Helper Functions =====

def df_row_to_listing(row: pd.Series) -> Listing:
    """Convert DataFrame row to Listing model."""
    # Handle amenities
    amenities = row.get('amenities', [])
    if not isinstance(amenities, list):
        amenities = []
    
    # Handle nullable integers
    def safe_int(val, default=0):
        if pd.isna(val):
            return default
        return int(val)
    
    def safe_float(val, default=0.0):
        if pd.isna(val):
            return default
        return float(val)
    
    return Listing(
        id=str(row['id']),
        title=str(row.get('name', 'Untitled')),
        price_per_night=safe_float(row.get('price', 0)),
        rating=safe_float(row.get('review_scores_rating', 0)) if pd.notna(row.get('review_scores_rating')) else None,
        reviews_count=safe_int(row.get('number_of_reviews', 0)),
        thumbnail=str(row.get('picture_url', '')),
        beds=safe_int(row.get('beds', 1)),
        baths=safe_float(row.get('bathrooms', 1.0)),
        guests=safe_int(row.get('accommodates', 2)),
        neighborhood=str(row.get('neighbourhood_cleansed', 'Unknown')),
        amenities=amenities[:10],  # Return first 10 for frontend
        lat=safe_float(row.get('latitude', 40.4168)),
        lng=safe_float(row.get('longitude', -3.7038)),
        description=str(row.get('description', ''))[:500] if pd.notna(row.get('description')) else None,
        images=[str(row.get('picture_url', ''))] if pd.notna(row.get('picture_url')) else [],
        house_rules=None,
        bedrooms=safe_int(row.get('bedrooms', 1)),
        property_type=str(row.get('property_type', 'Apartment')),
        room_type=str(row.get('room_type', 'Entire home/apt'))
    )


# ===== API Endpoints =====

@app.get("/")
async def root():
    """Health check."""
    return {
        "status": "running",
        "message": "AirBnBeautiful ML Backend is ready",
        "endpoints": [
            "POST /search",
            "GET /listings/featured",
            "GET /listings/{id}",
            "POST /neighborhood-chat",
            "GET /landlord/prefill",
            "POST /landlord/amenities-from-images",
            "POST /landlord/price-suggestions"
        ]
    }


@app.get("/health")
async def health_check():
    """Simple health check that responds immediately."""
    return {"status": "healthy"}


@app.get("/memory")
async def memory_check():
    """Check memory usage for debugging."""
    mem = get_memory_usage()
    return {
        "memory_mb": round(mem["rss_mb"], 2),
        "memory_percent": round(mem["percent"], 2),
        "status": "warning" if mem["percent"] > 80 else "ok"
    }


@app.get("/listings/featured")
async def get_featured_listings():
    """
    Get featured listings for home page.
    Returns 8 high-rated listings with good reviews.
    """
    try:
        # Filter for quality listings
        featured = df_listings[
            (df_listings['review_scores_rating'] >= 4.5) &
            (df_listings['number_of_reviews'] >= 5)
        ].copy()
        
        # If not enough, relax the criteria
        if len(featured) < 8:
            featured = df_listings[df_listings['review_scores_rating'] >= 4.0].copy()
        
        # Sample randomly
        if len(featured) > 8:
            featured = featured.sample(n=8, random_state=None)
        
        # Convert to response format
        listings = [df_row_to_listing(row) for _, row in featured.iterrows()]
        
        return {"listings": listings}
    
    except Exception as e:
        print(f"Featured listings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    NLP-based semantic search with timeout and memory optimization.
    Parses natural language query and returns ranked listings.
    """
    start_time = time.time()
    mem_before = get_memory_usage()
    
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        print(f"[SEARCH] Query: '{query}' | Memory: {mem_before['rss_mb']:.1f}MB", flush=True)
        
        # Wrap in timeout to prevent Railway proxy timeout (30s limit)
        async def search_with_timeout():
            # Use cached query parsing
            try:
                cached_result = cached_parse_query(query)
                spec = cached_result[8]  # Full spec dict
                print(f"[SEARCH] Using cached parse for query", flush=True)
            except Exception as parse_error:
                print(f"[SEARCH] Cache miss or parse error, parsing fresh: {parse_error}", flush=True)
                spec = nlp_service.parse_user_query_ml(query)
            
            # Apply filters
            filtered = nlp_service.apply_filters_ml(df_listings, spec)
            
            if filtered.empty:
                return SearchResponse(
                    parsed_filters=spec,
                    listings=[]
                )
            
            print(f"[SEARCH] Filtered to {len(filtered)} candidates", flush=True)
            
            # Check memory before ranking
            mem_current = get_memory_usage()
            if mem_current['percent'] > 85:
                print(f"[SEARCH] High memory ({mem_current['percent']:.1f}%), limiting results", flush=True)
                # Return top results by rating without semantic ranking
                filtered = filtered.nlargest(50, 'review_scores_rating', keep='first')
                listings = [df_row_to_listing(row) for _, row in filtered.iterrows()]
                return SearchResponse(
                    parsed_filters=spec,
                    listings=listings
                )
            
            # Rerank with hybrid scoring
            ranked = nlp_service.rerank_semantic_with_lex(
                filtered, query, listing_embeddings
            )
            
            # Convert to response format
            listings = [df_row_to_listing(row) for _, row in ranked.head(50).iterrows()]
            
            # Force garbage collection
            gc.collect()
            
            return SearchResponse(
                parsed_filters=spec,
                listings=listings
            )
        
        # Execute with 25-second timeout (under Railway's 30s limit)
        result = await asyncio.wait_for(search_with_timeout(), timeout=25.0)
        
        elapsed = time.time() - start_time
        mem_after = get_memory_usage()
        print(f"[SEARCH] Complete in {elapsed:.2f}s | Memory: {mem_after['rss_mb']:.1f}MB "
              f"(+{mem_after['rss_mb'] - mem_before['rss_mb']:.1f}MB)", flush=True)
        
        return result
    
    except asyncio.TimeoutError:
        print(f"[SEARCH] Timeout after 25s for query: '{query}'", flush=True)
        raise HTTPException(
            status_code=504,
            detail="Search took too long. Try a more specific query or fewer filters."
        )
    
    except MemoryError as e:
        print(f"[SEARCH] Memory error: {e}", flush=True)
        gc.collect()
        raise HTTPException(
            status_code=503,
            detail="Server memory full. Please try again in a moment."
        )
    
    except Exception as e:
        print(f"[SEARCH] Error: {type(e).__name__}: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/listings/{listing_id}")
async def get_listing(listing_id: str):
    """Get detailed listing information."""
    try:
        listing_dict = data_service.get_listing_by_id(listing_id)
        
        if listing_dict is None:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        # Convert to Listing model
        row = pd.Series(listing_dict)
        listing = df_row_to_listing(row)
        
        return listing
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get listing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/neighborhood-chat", response_model=NeighborhoodChatResponse)
async def neighborhood_chat(request: NeighborhoodChatRequest):
    """
    RAG-powered neighborhood Q&A.
    Retrieves context and generates conversational responses.
    """
    try:
        # Get listing to find neighborhood
        listing_dict = data_service.get_listing_by_id(request.listingId)
        
        if listing_dict is None:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        neighborhood = listing_dict.get('neighbourhood_group_cleansed', 'Centro')
        
        # Generate answer with listing context
        reply = rag_service.answer_neighborhood_question(
            request.message,
            neighborhood,
            listing_info=listing_dict
        )
        
        return NeighborhoodChatResponse(reply=reply)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Neighborhood chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.get("/landlord/prefill", response_model=PrefillListing)
async def landlord_prefill():
    """
    Return pre-filled listing data for demo.
    """
    # Use first listing from DB as template
    sample_row = df_listings.iloc[0]
    
    def safe_int(val, default=0):
        if pd.isna(val):
            return default
        return int(val)
    
    def safe_float(val, default=0.0):
        if pd.isna(val):
            return default
        return float(val)
    
    return PrefillListing(
        title=str(sample_row.get('name', 'Bright 1BR in Lavapiés')),
        type=str(sample_row.get('property_type', 'Entire apartment')),
        guests=safe_int(sample_row.get('accommodates', 2)),
        beds=safe_int(sample_row.get('beds', 1)),
        baths=safe_float(sample_row.get('bathrooms', 1.0)),
        bedrooms=safe_int(sample_row.get('bedrooms', 1)),
        address=f"Calle de Embajadores, {sample_row.get('neighbourhood_cleansed', 'Madrid')}",
        neighborhood=str(sample_row.get('neighbourhood_group_cleansed', 'Centro')),
        price_per_night=safe_float(sample_row.get('price', 85)),
        amenities=["WiFi", "Kitchen"],
        photos=SAMPLE_PHOTOS[:2],
        all_ready_photos=SAMPLE_PHOTOS
    )


@app.post("/landlord/amenities-from-images", response_model=AmenitiesFromImagesResponse)
async def amenities_from_images(request: AmenitiesFromImagesRequest):
    """
    Computer vision amenity detection from photos.
    Uses YOLOv8 + OWL-ViT two-stage detection.
    """
    try:
        if not request.photoIds:
            raise HTTPException(status_code=400, detail="No photo IDs provided")
        
        # Map photo IDs to URLs
        photo_map = {p["id"]: p["url"] for p in SAMPLE_PHOTOS}
        photo_urls = [photo_map[pid] for pid in request.photoIds if pid in photo_map]
        
        if not photo_urls:
            raise HTTPException(status_code=400, detail="No valid photo IDs")
        
        # Detect amenities
        detected = cv_service.detect_amenities_from_photos(photo_urls)
        
        return AmenitiesFromImagesResponse(detected=detected)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"CV detection error: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.post("/landlord/price-suggestions", response_model=PriceSuggestionsResponse)
async def price_suggestions(request: PriceSuggestionsRequest):
    """
    Price optimization with feature importance analysis.
    Returns personalized amenity recommendations to reach target price.
    """
    try:
        # Get unique neighborhoods for encoding
        neighborhoods = df_listings['neighbourhood_group_cleansed'].unique().tolist()
        
        # Get suggestions
        result = price_service.get_price_suggestions(
            current_amenities=request.currentAmenities,
            target_price=request.targetPrice,
            listing_meta={
                'guests': request.listingMeta.guests,
                'beds': request.listingMeta.beds,
                'baths': request.listingMeta.baths,
                'neighborhood': request.listingMeta.neighborhood
            },
            neighborhoods=neighborhoods
        )
        
        return PriceSuggestionsResponse(**result)
    
    except Exception as e:
        print(f"Price suggestions error: {e}")
        raise HTTPException(status_code=500, detail=f"Price optimization failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

