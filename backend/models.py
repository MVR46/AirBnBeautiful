"""Pydantic models for API request/response validation."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ===== Search Models =====

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")


class SearchFilters(BaseModel):
    location: Optional[str] = None
    dates: Optional[Dict[str, str]] = None
    guests: Optional[int] = None
    price_range: Optional[List[int]] = None
    amenities: Optional[List[str]] = None


class Listing(BaseModel):
    id: str
    title: str
    price_per_night: float
    rating: Optional[float] = None
    reviews_count: int = 0
    thumbnail: str
    beds: int
    baths: float
    guests: int
    neighborhood: str
    amenities: List[str]
    lat: float
    lng: float
    description: Optional[str] = None
    images: Optional[List[str]] = None
    house_rules: Optional[List[str]] = None
    bedrooms: Optional[int] = None
    property_type: Optional[str] = None
    room_type: Optional[str] = None


class SearchResponse(BaseModel):
    parsed_filters: Dict[str, Any]
    listings: List[Listing]


# ===== Listing Detail Models =====

class ListingDetailResponse(Listing):
    """Extended listing details with full information."""
    pass


# ===== Neighborhood Chat Models =====

class NeighborhoodChatRequest(BaseModel):
    listingId: str
    message: str = Field(..., min_length=1)


class NeighborhoodChatResponse(BaseModel):
    reply: str


# ===== Landlord Models =====

class Photo(BaseModel):
    id: str
    url: str


class PrefillListing(BaseModel):
    title: str
    type: str
    guests: int
    beds: int
    baths: float
    bedrooms: int
    address: str
    neighborhood: str
    price_per_night: float
    amenities: List[str]
    photos: List[Photo]
    all_ready_photos: List[Photo]


class AmenitiesFromImagesRequest(BaseModel):
    photoIds: List[str]


class AmenitiesFromImagesResponse(BaseModel):
    detected: List[str]


class ListingMeta(BaseModel):
    guests: int
    beds: int
    neighborhood: str
    bedrooms: Optional[int] = 1
    baths: Optional[float] = 1.0


class PriceSuggestionsRequest(BaseModel):
    currentAmenities: List[str]
    targetPrice: float
    listingMeta: ListingMeta


class FeatureImportance(BaseModel):
    feature: str
    importance: float


class RecommendedAddition(BaseModel):
    amenity: str
    estimatedLift: float


class PriceSuggestionsResponse(BaseModel):
    currentPriceEstimate: float
    targetPrice: float
    featureImportance: List[FeatureImportance]
    recommendedAdditions: List[RecommendedAddition]
    notes: str

