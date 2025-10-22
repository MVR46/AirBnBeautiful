# AirBnBeautiful Backend

FastAPI backend for the Airbnb ML Demo featuring NLP search, RAG chat, computer vision amenity detection, and price optimization.

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   # Option 1: Using the startup script (recommended - same as production)
   bash start.sh
   
   # Option 2: Direct Python
   python main.py
   
   # Option 3: Using uvicorn
   uvicorn main:app --reload
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health check: http://localhost:8000

### First Run

On first run, the application will automatically:
1. ✅ Download the Madrid Airbnb dataset (~16MB)
2. ✅ Clean and process the data
3. ✅ Create `data/airbnb.db` with ~1000 listings
4. ✅ Start the server

**This takes 2-3 minutes on first run, then < 1 minute on subsequent runs.**

## 📦 Features

- **🔍 NLP Search** - Semantic search using sentence transformers
- **💬 RAG Chat** - OpenAI-powered neighborhood Q&A
- **📸 CV Detection** - YOLOv8 + OWL-ViT amenity detection
- **💰 Price Optimization** - Random Forest price predictions
- **🗄️ Data Service** - SQLite database with Madrid listings

## 🗂️ Project Structure

```
backend/
├── main.py                 # FastAPI app and endpoints
├── data_service.py         # Database service
├── nlp_service.py          # NLP search engine
├── rag_service.py          # RAG chat with OpenAI
├── cv_service.py           # Computer vision amenity detection
├── price_service.py        # Price optimization
├── models.py               # Pydantic models
├── prepare_data.py         # Data preparation script
├── start.sh                # Production startup script
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── Procfile                # Railway/Heroku start command
├── nixpacks.toml           # System dependencies for Railway
├── runtime.txt             # Python version
└── data/                   # Generated data directory
    ├── airbnb.db           # SQLite database (auto-generated)
    ├── listings_1000.csv   # Raw data (auto-generated)
    └── listing_embeddings.npy  # Cached embeddings (auto-generated)
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | No | - | OpenAI API key for RAG chat |
| `PORT` | No | 8000 | Server port |

### Set Environment Variables

Create a `.env` file in the backend directory:

```bash
# Optional: For RAG neighborhood chat feature
OPENAI_API_KEY=sk-your-openai-api-key

# Optional: Custom port
PORT=8000
```

**Note:** The app works without `OPENAI_API_KEY`, but the neighborhood chat feature will be disabled.

## 🌐 API Endpoints

### Core Endpoints

- `GET /` - Health check and endpoint list
- `GET /listings/featured` - Get featured listings
- `POST /search` - NLP semantic search
- `GET /listings/{id}` - Get listing details
- `POST /neighborhood-chat` - RAG-powered Q&A

### Landlord Endpoints

- `GET /landlord/prefill` - Get prefilled listing data
- `POST /landlord/amenities-from-images` - CV amenity detection
- `POST /landlord/price-suggestions` - Price optimization

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🚂 Deployment

### Railway Deployment

**✨ Automatic data preparation included!** No manual setup required.

See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for detailed instructions.

**Quick steps:**
1. Push to GitHub
2. Connect Railway to your repo
3. Set root directory to `backend`
4. Add `OPENAI_API_KEY` environment variable (optional)
5. Deploy!

The `start.sh` script automatically handles data preparation on first deployment.

### Docker Deployment

```bash
# Build
docker build -t airbnb-backend .

# Run
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-your-key airbnb-backend
```

### Manual Deployment

If you need to run data preparation manually:

```bash
cd backend
python prepare_data.py
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🧪 Testing

### Test API Connection

```bash
# Health check
curl http://localhost:8000/

# Get featured listings
curl http://localhost:8000/listings/featured

# Search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "2 bedroom apartment in Centro under 100 euros"}'
```

### Run Test Script

```bash
python test_api.py
```

## 📊 Data

### Dataset Source

Madrid Airbnb data from [MVR46/airbnb-data-madrid](https://github.com/MVR46/airbnb-data-madrid)

### Data Preparation

The `prepare_data.py` script:
1. Downloads the Madrid listings CSV (~16MB)
2. Cleans and validates the data
3. Selects 1000 representative listings
4. Creates SQLite database at `data/airbnb.db`
5. Saves CSV backup at `data/listings_1000.csv`

**This runs automatically on first startup!**

### Manual Data Preparation

If you need to regenerate the data:

```bash
python prepare_data.py
```

## 🔍 ML Models

### NLP Models

- **Sentence Transformer**: `sentence-transformers/all-MiniLM-L6-v2`
  - Used for semantic search and embeddings
  - Automatically downloaded on first run
  - ~90MB download

- **TF-IDF Vectorizer**: Built from listings data
  - Used for keyword matching
  - Generated at startup

### Computer Vision Models

- **YOLOv8**: `yolov8n.pt`
  - Object detection for initial amenity candidates
  - Automatically downloaded on first run
  - ~6MB download

- **OWL-ViT**: `google/owlvit-base-patch32`
  - Zero-shot object detection for refinement
  - Automatically downloaded from Hugging Face
  - ~600MB download

### Price Prediction Model

- **Random Forest Regressor**
  - Trained on listing features at startup
  - No pre-trained weights needed
  - In-memory model

## 🐛 Troubleshooting

### Database not found error

**This should no longer happen!** The app automatically creates the database.

If you still see this error:
1. Check that `start.sh` exists and is executable
2. Verify the `Procfile` is configured correctly
3. Check logs for data preparation errors
4. Try deleting `data/` folder and restarting

### OpenCV/libGL errors

These are system dependency issues. Make sure you have:
- For Railway: `nixpacks.toml` is present
- For Docker: System packages in `Dockerfile`
- For local: Install OpenCV dependencies for your OS

### Out of memory errors

The ML models need ~1.5GB RAM. If you encounter memory issues:
- For Railway: Upgrade to a paid plan
- For Docker: Increase container memory limit
- For local: Close other applications

### Slow first startup

First startup takes 5-10 minutes because:
1. ML models are downloaded (~700MB total)
2. Dataset is downloaded and processed (~16MB)
3. Embeddings are computed (~1000 listings)

Subsequent startups are much faster (~1 minute) as models and data are cached.

## 📝 Development

### Adding New Features

1. Create new service file (e.g., `new_service.py`)
2. Add endpoint in `main.py`
3. Add Pydantic models in `models.py`
4. Test locally
5. Update API documentation

### Database Schema

The SQLite database has a single `listings` table with columns:
- `id` - Unique listing ID
- `name` - Listing title
- `price` - Price per night
- `neighbourhood_group_cleansed` - District
- `neighbourhood_cleansed` - Neighborhood
- `room_type` - Room type (Entire home/Private room/etc)
- `property_type` - Property type
- `accommodates` - Max guests
- `bedrooms`, `beds`, `bathrooms` - Room counts
- `amenities` - List of amenities (as string)
- `latitude`, `longitude` - Coordinates
- Plus many more fields...

See `prepare_data.py` for full schema.

## 🔗 Related Documentation

- [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) - Railway deployment guide
- [DEPLOYMENT_FIX_SUMMARY.md](./DEPLOYMENT_FIX_SUMMARY.md) - Database auto-preparation fix
- [../DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [../docs/API_REFERENCE.md](../docs/API_REFERENCE.md) - API reference

## 📄 License

See [LICENSE](../LICENSE) file.

## 🆘 Support

- Check logs: `backend.log`
- Railway logs: Railway Dashboard → Deployments → View Logs
- API docs: http://localhost:8000/docs

---

**Built with:** FastAPI, PyTorch, Transformers, Sentence Transformers, OpenAI, YOLOv8, Ultralytics, scikit-learn

