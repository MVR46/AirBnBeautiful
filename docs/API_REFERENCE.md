# API Reference - Madrid Airbnb ML Demo

Complete API documentation for the FastAPI backend.

## Base URL

**Development:** `http://localhost:8000`

**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI)

## Authentication

No authentication required for demo. All endpoints are publicly accessible.

## API Endpoints

### Health Check

#### `GET /`

Check if the API is running.

**Response:**
```json
{
  "status": "running",
  "endpoints": [...]
}
```

---

## Guest Mode Endpoints

### Get Featured Listings

#### `GET /listings/featured`

Get curated featured listings for the home page. Returns 8 high-quality listings with good ratings.

**Response:**
```json
{
  "listings": [
    {
      "id": "12345",
      "title": "Cozy apartment in Salamanca",
      "price_per_night": 85.0,
      "rating": 4.8,
      "reviews_count": 42,
      "thumbnail": "https://...",
      "beds": 1,
      "baths": 1.0,
      "guests": 2,
      "neighborhood": "Salamanca",
      "amenities": ["WiFi", "Kitchen", ...],
      "lat": 40.4168,
      "lng": -3.7038,
      "description": "Beautiful apartment...",
      "bedrooms": 1,
      "property_type": "Entire apartment",
      "room_type": "Entire home/apt"
    }
  ]
}
```

**Selection Criteria:**
- Rating ≥ 4.5/5.0
- At least 5 reviews
- Random sample for variety

**Example cURL:**
```bash
curl http://localhost:8000/listings/featured
```

---

### Search Listings

#### `POST /search`

Natural language semantic search for listings.

**Request Body:**
```json
{
  "query": "2 guests in Salamanca under €100 with wifi and kitchen"
}
```

**Response:**
```json
{
  "parsed_filters": {
    "neighbourhoods": ["salamanca"],
    "guests": 2,
    "price_max": 100,
    "amenities_all": ["wifi", "kitchen"]
  },
  "listings": [
    {
      "id": "12345",
      "title": "Cozy apartment in Salamanca",
      "price_per_night": 85.0,
      "rating": 4.8,
      "reviews_count": 42,
      "thumbnail": "https://...",
      "beds": 1,
      "baths": 1.0,
      "guests": 2,
      "neighborhood": "Salamanca",
      "amenities": ["WiFi", "Kitchen", "Heating", ...],
      "lat": 40.4168,
      "lng": -3.7038,
      "description": "Beautiful apartment...",
      "bedrooms": 1,
      "property_type": "Entire apartment",
      "room_type": "Entire home/apt"
    }
  ]
}
```

**Query Parsing Features:**
- Extracts guests count
- Parses price ranges ("under 100", "between 50 and 100")
- Identifies neighborhoods
- Extracts amenities
- Hybrid ranking: 55% semantic + 20% lexical + 15% rating + 10% price

**Example cURL:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "2 guests in Salamanca with WiFi and kitchen under 100 euros"
  }'
```

**Example Queries:**
- "spacious apartment near center with parking"
- "pet friendly place in Retiro neighborhood"
- "modern studio under 80 with air conditioning"
- "3 guests need 2 bedrooms in Chamberí"

---

### Get Listing Details

#### `GET /listings/{listing_id}`

Get detailed information about a specific listing.

**Parameters:**
- `listing_id` (path) - Listing ID

**Response:**
```json
{
  "id": "12345",
  "title": "Cozy apartment in Salamanca",
  "price_per_night": 85.0,
  "rating": 4.8,
  "reviews_count": 42,
  "thumbnail": "https://...",
  "beds": 1,
  "baths": 1.0,
  "guests": 2,
  "neighborhood": "Salamanca",
  "amenities": ["WiFi", "Kitchen", ...],
  "lat": 40.4168,
  "lng": -3.7038,
  "description": "Full description...",
  "images": ["https://...", ...],
  "house_rules": null,
  "bedrooms": 1,
  "property_type": "Entire apartment",
  "room_type": "Entire home/apt"
}
```

**Error Responses:**
- `404 Not Found` - Listing not found

**Example cURL:**
```bash
curl http://localhost:8000/listings/12345
```

---

### Neighborhood Chat

#### `POST /neighborhood-chat`

RAG-powered Q&A about neighborhoods.

**Request Body:**
```json
{
  "listingId": "12345",
  "message": "Is this neighborhood safe at night?"
}
```

**Response:**
```json
{
  "reply": "Salamanca is one of Madrid's safest neighborhoods, known for its upscale residential character and well-lit streets. The area has a strong police presence and is popular among families and professionals. Walking at night is generally very safe, though as with any city, it's wise to stay aware of your surroundings..."
}
```

**Requirements:**
- Requires `OPENAI_API_KEY` in backend environment
- Uses GPT-4o-mini for generation
- Retrieves top-3 relevant context chunks

**Error Responses:**
- `404 Not Found` - Listing not found
- `500 Internal Server Error` - OpenAI API error (check API key)

**Example cURL:**
```bash
curl -X POST http://localhost:8000/neighborhood-chat \
  -H "Content-Type: application/json" \
  -d '{
    "listingId": "12345",
    "message": "What are the best restaurants in this neighborhood?"
  }'
```

**Tips:**
- Works best with specific, focused questions
- Can ask about safety, transportation, dining, culture, etc.
- Responses are context-aware and include listing information

---

## Landlord Mode Endpoints

### Get Prefill Data

#### `GET /landlord/prefill`

Get pre-filled sample listing data for demo.

**Response:**
```json
{
  "title": "Bright 1BR in Lavapiés",
  "type": "Entire apartment",
  "guests": 2,
  "beds": 1,
  "baths": 1.0,
  "bedrooms": 1,
  "address": "Calle de Embajadores, Madrid",
  "neighborhood": "Centro",
  "price_per_night": 85.0,
  "amenities": ["WiFi", "Kitchen"],
  "photos": [
    {"id": "p1", "url": "https://..."},
    {"id": "p2", "url": "https://..."}
  ],
  "all_ready_photos": [...]
}
```

---

### Detect Amenities from Images

#### `POST /landlord/amenities-from-images`

Computer vision-based amenity detection from property photos.

**Request Body:**
```json
{
  "photoIds": ["p1", "p2", "p3"]
}
```

**Response:**
```json
{
  "detected": [
    "Kitchen",
    "Dishwasher",
    "Oven",
    "Microwave",
    "WiFi",
    "TV",
    "Sofa"
  ]
}
```

**How it works:**
1. Downloads images from URLs
2. Runs YOLOv8n for fast object detection
3. Runs OWL-ViT for amenity-specific detection
4. Merges and normalizes results

**Performance:**
- ~2-3 seconds per image on CPU
- ~0.5-1 second per image on GPU

**Error Responses:**
- `400 Bad Request` - No photo IDs provided or invalid IDs
- `500 Internal Server Error` - CV model error

**Example cURL:**
```bash
curl -X POST http://localhost:8000/landlord/amenities-from-images \
  -H "Content-Type: application/json" \
  -d '{
    "photoIds": ["p1", "p2", "p3"]
  }'
```

**Detected Amenities Include:**
- Kitchen appliances (oven, microwave, dishwasher, refrigerator)
- Electronics (TV, WiFi)
- Furniture (sofa, bed, desk)
- Bathroom fixtures
- Laundry (washer, dryer)
- And more...

---

### Get Price Suggestions

#### `POST /landlord/price-suggestions`

Price optimization with feature importance and amenity recommendations.

**Request Body:**
```json
{
  "currentAmenities": ["WiFi", "Kitchen"],
  "targetPrice": 120,
  "listingMeta": {
    "guests": 2,
    "beds": 1,
    "baths": 1.0,
    "neighborhood": "Centro"
  }
}
```

**Response:**
```json
{
  "currentPriceEstimate": 85.5,
  "targetPrice": 120,
  "featureImportance": [
    {"feature": "neighborhood_Centro", "importance": 0.25},
    {"feature": "WiFi", "importance": 0.18},
    {"feature": "beds", "importance": 0.15},
    {"feature": "guests", "importance": 0.12}
  ],
  "recommendedAdditions": [
    {"amenity": "Air conditioning", "estimatedLift": 12.5},
    {"amenity": "Washer", "estimatedLift": 8.3},
    {"amenity": "Dishwasher", "estimatedLift": 6.7},
    {"amenity": "Dryer", "estimatedLift": 5.2}
  ],
  "notes": "To reach €120/night from current estimate of €85.5, consider adding high-impact amenities. Air conditioning and washer would add approximately €20.8/night combined. Focus on amenities that are valued in the Centro neighborhood."
}
```

**How it works:**
1. Predicts current price based on existing features
2. Identifies missing high-value amenities
3. Estimates price lift for each recommended amenity
4. Ranks by estimated ROI

**Example cURL:**
```bash
curl -X POST http://localhost:8000/landlord/price-suggestions \
  -H "Content-Type: application/json" \
  -d '{
    "currentAmenities": ["WiFi", "Kitchen"],
    "targetPrice": 120,
    "listingMeta": {
      "guests": 2,
      "beds": 1,
      "baths": 1.0,
      "neighborhood": "Centro"
    }
  }'
```

**Note:** The model is trained on Madrid Airbnb data and considers neighborhood-specific pricing patterns.

---

## Data Models

### Listing

```typescript
{
  id: string
  title: string
  price_per_night: number
  rating?: number
  reviews_count: number
  thumbnail: string
  beds: number
  baths: number
  guests: number
  neighborhood: string
  amenities: string[]
  lat: number
  lng: number
  description?: string
  images?: string[]
  house_rules?: string[]
  bedrooms?: number
  property_type?: string
  room_type?: string
}
```

### SearchFilters

```typescript
{
  location?: string
  dates?: {check_in: string, check_out: string}
  guests?: number
  price_range?: [number, number]
  amenities?: string[]
}
```

### Photo

```typescript
{
  id: string
  url: string
}
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Success
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "detail": "Error message"
}
```

---

## Rate Limiting

No rate limiting in development mode.

For production, consider implementing:
- Rate limiting per IP
- API key authentication
- Request throttling

---

## CORS

Currently configured to allow all origins (`*`) for development.

**Production:** Update `main.py` to specify allowed origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ML Models Used

### NLP Search
- **Sentence Transformer**: `all-MiniLM-L6-v2` (384 dimensions)
- **spaCy**: `en_core_web_sm` for entity extraction
- **TF-IDF**: Scikit-learn for lexical matching

### RAG Chat
- **Embeddings**: Same as NLP search
- **LLM**: OpenAI GPT-4o-mini

### Computer Vision
- **YOLOv8**: `yolov8n` (nano model)
- **OWL-ViT**: Zero-shot object detection

### Price Optimization
- **Model**: RandomForestRegressor with 100 estimators
- **Features**: 15 amenity flags + beds/baths/guests + neighborhood encoding

---

## Performance Tips

1. **First request is slow** (~10-15s) - Models load on-demand
2. **Subsequent requests are fast** - Models stay in memory
3. **Use cached embeddings** - Stored in `backend/data/listing_embeddings.npy`
4. **GPU acceleration** - Speeds up CV detection 5-10x
5. **Batch processing** - Process multiple listings together when possible

---

## Development

### Adding New Endpoints

1. Define request/response models in `models.py`
2. Create handler in `main.py`
3. Add business logic to appropriate service
4. Update this documentation

### Testing Endpoints

```bash
# Use the automated test script
./scripts/test-api-connection.sh

# Or use interactive docs
open http://localhost:8000/docs
```

---

## Troubleshooting

### Common Issues

**Problem: RAG chat returns 500 error**
- **Cause**: Missing or invalid OpenAI API key
- **Solution**: Check `backend/.env` has valid `OPENAI_API_KEY`
- **Verification**: 
  ```bash
  grep OPENAI_API_KEY backend/.env
  ```

**Problem: Slow first request**
- **Cause**: Models loading into memory (YOLOv8, embeddings, etc.)
- **Solution**: This is normal. First request takes 10-15s, subsequent requests are fast
- **Tip**: Keep the server running during development

**Problem: CV detection not finding amenities**
- **Cause**: Poor image quality or amenities not visible
- **Solution**: Use clear, well-lit photos showing amenities prominently
- **Note**: Model accuracy ~70-80% depending on image quality

**Problem: Search returns no results**
- **Cause**: Filters too restrictive or database not initialized
- **Solution**: 
  1. Check database exists: `ls backend/data/airbnb.db`
  2. Try broader search query
  3. Check parsed filters in response

**Problem: CORS errors from frontend**
- **Cause**: Frontend trying to access API from different origin
- **Solution**: Backend CORS is set to allow all origins in development
- **Check**: Verify backend is running on port 8000

### Performance Optimization

**Enable GPU acceleration** (if available):
```bash
# Check if CUDA is available
python -c "import torch; print(torch.cuda.is_available())"
```

**Adjust worker threads** for uvicorn:
```bash
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

**Pre-cache embeddings**:
Embeddings are automatically cached in `backend/data/listing_embeddings.npy` after first computation.

---

## Rate Limiting & Production Considerations

### Current Setup (Development)
- No authentication required
- No rate limiting
- CORS allows all origins
- Single worker process

### Production Recommendations

1. **Add Authentication**:
   ```python
   from fastapi.security import HTTPBearer
   security = HTTPBearer()
   ```

2. **Enable Rate Limiting**:
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

3. **Restrict CORS**:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

4. **Use Multiple Workers**:
   ```bash
   uvicorn main:app --workers 4
   ```

5. **Add Logging & Monitoring**:
   - Integrate with Sentry for error tracking
   - Use Prometheus for metrics
   - Add structured logging

6. **Environment Variables**:
   - Never commit `.env` files
   - Use secrets management (AWS Secrets Manager, etc.)
   - Validate all environment variables at startup

---

For detailed setup instructions, see [Setup Guide](./SETUP_GUIDE.md)

