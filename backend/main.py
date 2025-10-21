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
    
    print("\n" + "="*60)
    print("Starting Airbnb ML Backend")
    print("="*60)
    
    # Initialize data service
    print("\n1. Loading listings database...")
    data_service = DataService()
    df_listings = data_service.get_all_listings()
    print(f"   Loaded {len(df_listings)} listings")
    
    # Initialize NLP models
    print("\n2. Initializing NLP models...")
    nlp_service.init_nlp_models()
    
    # Prepare amenities for NLP
    print("\n3. Preparing amenity normalization...")
    df_listings = nlp_service.prepare_amenities_norm(df_listings)
    
    # Build amenity clusters and label pools
    print("\n4. Building amenity clusters...")
    nlp_service.build_amenity_clusters(df_listings)
    
    print("\n5. Building label pools (neighborhoods, types)...")
    nlp_service.build_label_pools(df_listings)
    
    # Prepare listing texts and embeddings
    print("\n6. Preparing listing embeddings...")
    
    def _concat_text(row: pd.Series) -> str:
        name = str(row.get('name', '') or '').strip()
        desc = str(row.get('description', '') or '').strip()
        if not desc and 'neighborhood_overview' in row:
            desc = str(row.get('neighborhood_overview', '') or '').strip()
        txt = f"{name}. {desc}".strip()
        return txt if txt else name
    
    listing_texts = df_listings.apply(_concat_text, axis=1).tolist()
    
    # Check for cached embeddings
    emb_path = Path('data/listing_embeddings.npy')
    if emb_path.exists():
        try:
            listing_embeddings = np.load(emb_path)
            print(f"   Loaded cached embeddings: {listing_embeddings.shape}")
        except:
            listing_embeddings = None
    
    if listing_embeddings is None:
        print("   Computing listing embeddings...")
        listing_embeddings = nlp_service.embed_model.encode(
            listing_texts,
            batch_size=64,
            show_progress_bar=True,
            normalize_embeddings=True
        ).astype('float32')
        
        # Cache for next time
        os.makedirs('data', exist_ok=True)
        np.save(emb_path, listing_embeddings)
        print(f"   Saved embeddings to {emb_path}")
    
    # Build TF-IDF index
    print("\n7. Building TF-IDF index...")
    nlp_service.build_tfidf_index(df_listings, listing_texts)
    
    # Build amenities_canon column for filtering
    print("\n8. Building canonical amenities for filtering...")
    df_listings['amenities_canon'] = df_listings['amenities_norm'].apply(
        lambda xs: sorted({nlp_service.AMEN_CANON.get(nlp_service.norm_txt(x))
                          for x in (xs or [])
                          if nlp_service.AMEN_CANON.get(nlp_service.norm_txt(x))})
    )
    
    # Initialize RAG service
    print("\n9. Initializing RAG service...")
    rag_service.init_rag_service(nlp_service.embed_model, NEIGHBORHOOD_DATA)
    
    # Train price model
    print("\n10. Training price optimization model...")
    price_service.train_price_model(df_listings)
    
    print("\n" + "="*60)
    print("Backend ready! All services initialized.")
    print("="*60 + "\n")
    
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
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
    NLP-based semantic search.
    Parses natural language query and returns ranked listings.
    """
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Parse query
        spec = nlp_service.parse_user_query_ml(query)
        
        # Apply filters
        filtered = nlp_service.apply_filters_ml(df_listings, spec)
        
        if filtered.empty:
            return SearchResponse(
                parsed_filters=spec,
                listings=[]
            )
        
        # Rerank with hybrid scoring
        ranked = nlp_service.rerank_semantic_with_lex(
            filtered, query, listing_embeddings
        )
        
        # Convert to response format
        listings = [df_row_to_listing(row) for _, row in ranked.head(50).iterrows()]
        
        return SearchResponse(
            parsed_filters=spec,
            listings=listings
        )
    
    except Exception as e:
        print(f"Search error: {e}")
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

