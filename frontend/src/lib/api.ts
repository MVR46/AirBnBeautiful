// API client with error handling
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://airbnbeautiful-production.up.railway.app';

interface ApiError {
  message: string;
  status?: number;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error: ApiError = {
      message: `API error: ${response.statusText}`,
      status: response.status,
    };
    throw error;
  }
  return response.json();
}

// Guest Mode APIs
export interface SearchFilters {
  location?: string;
  dates?: { check_in: string; check_out: string };
  guests?: number;
  price_range?: [number, number];
  amenities?: string[];
}

export interface Listing {
  id: string;
  title: string;
  price_per_night: number;
  rating: number;
  reviews_count: number;
  thumbnail: string;
  beds: number;
  baths: number;
  guests: number;
  neighborhood: string;
  amenities: string[];
  lat: number;
  lng: number;
}

export interface SearchResponse {
  parsed_filters: SearchFilters;
  listings: Listing[];
}

export async function searchListings(query: string): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  return handleResponse<SearchResponse>(response);
}

export async function getFeaturedListings(): Promise<{ listings: Listing[] }> {
  const response = await fetch(`${API_BASE_URL}/listings/featured`);
  return handleResponse(response);
}

export async function getListingById(id: string): Promise<Listing & { description?: string; images?: string[]; house_rules?: string[] }> {
  const response = await fetch(`${API_BASE_URL}/listings/${id}`);
  return handleResponse(response);
}

export async function chatWithNeighborhood(listingId: string, message: string): Promise<{ reply: string }> {
  const response = await fetch(`${API_BASE_URL}/neighborhood-chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ listingId, message }),
  });
  return handleResponse(response);
}

// Landlord Mode APIs
export interface Photo {
  id: string;
  url: string;
}

export interface PrefillData {
  title: string;
  type: string;
  guests: number;
  beds: number;
  baths: number;
  bedrooms: number;
  address: string;
  neighborhood: string;
  price_per_night: number;
  amenities: string[];
  photos: Photo[];
  all_ready_photos: Photo[];
}

export async function getLandlordPrefill(): Promise<PrefillData> {
  const response = await fetch(`${API_BASE_URL}/landlord/prefill`);
  return handleResponse(response);
}

export async function detectAmenitiesFromImages(photoIds: string[]): Promise<{ detected: string[] }> {
  const response = await fetch(`${API_BASE_URL}/landlord/amenities-from-images`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ photoIds }),
  });
  return handleResponse(response);
}

export interface PriceSuggestion {
  currentPriceEstimate: number;
  targetPrice: number;
  featureImportance: Array<{ feature: string; importance: number }>;
  recommendedAdditions: Array<{ amenity: string; estimatedLift: number }>;
  notes?: string;
}

export async function getPriceSuggestions(
  currentAmenities: string[],
  targetPrice: number,
  listingMeta: Record<string, any>
): Promise<PriceSuggestion> {
  const response = await fetch(`${API_BASE_URL}/landlord/price-suggestions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ currentAmenities, targetPrice, listingMeta }),
  });
  return handleResponse(response);
}
