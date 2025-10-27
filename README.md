# AirBnBeautiful

A production-ready full-stack machine learning application showcasing advanced ML techniques for Airbnb property search and management.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com) [![React](https://img.shields.io/badge/React-18-61DAFB)](https://react.dev) [![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://python.org) [![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org) [![Railway](https://img.shields.io/badge/Deploy-Railway-blueviolet)](https://railway.app) [![Vercel](https://img.shields.io/badge/Deploy-Vercel-black)](https://vercel.com)

---

## ✨ Features

### For Guests
- **🔍 Semantic Search**: Natural language search using sentence transformers and hybrid ranking
- **💬 Neighborhood Chat**: RAG-powered Q&A about neighborhoods using OpenAI GPT-4o-mini
- **📍 Interactive Listings**: Explore properties with detailed information and filtering

### For Landlords
- **📸 CV Amenity Detection**: Automatically detect amenities from property photos using YOLOv8 and OWL-ViT
- **💰 Price Optimization**: ML-powered price suggestions with feature importance analysis
- **📊 Smart Recommendations**: Get personalized amenity recommendations to reach target prices

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **PyTorch** - Deep learning framework
- **Sentence Transformers** - Semantic embeddings (all-MiniLM-L6-v2)
- **spaCy** - NLP and entity extraction
- **Scikit-learn** - ML models (RandomForest, TF-IDF)
- **YOLOv8** - Object detection
- **Transformers (OWL-ViT)** - Zero-shot detection
- **OpenAI API** - GPT-4o-mini for conversational AI
- **SQLite** - Listings database

### Frontend
- **React 18** + **TypeScript** - Type-safe UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** + **shadcn/ui** - Modern component library
- **React Router** - Client-side navigation

### ML & Data
- **1000+ Madrid Airbnb listings** with real data
- **Automatic data preparation** on first deployment
- **Cached embeddings** for fast subsequent deployments

---

## 🚀 Quick Start

The full application is accessible on the domain: **[rbnbeatiful.casa](rbnbeatiful.casa)** / **[www.rbnbeatiful.casa ](www.rbnbeatiful.casa )**

### Run Locally

For local development and testing:

👉 **See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** for local setup instructions

**Quick setup:**
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend (in new terminal)
cd frontend
npm install
npm run dev
```

---

## 📁 Project Structure

```
AirBnBeautiful/
├── backend/                     # FastAPI backend
│   ├── main.py                 # Application entry point
│   ├── models.py               # Pydantic models
│   ├── data_service.py         # Database operations
│   ├── nlp_service.py          # NLP search & parsing
│   ├── rag_service.py          # RAG neighborhood chat
│   ├── cv_service.py           # Computer vision detection
│   ├── price_service.py        # Price optimization
│   ├── prepare_data.py         # Database initialization
│   ├── start.sh                # Startup script with auto data prep
│   ├── requirements.txt        # Python dependencies
│   ├── Procfile                # Railway start command
│   ├── railway.json            # Railway configuration
│   ├── nixpacks.toml           # System dependencies
│   ├── Dockerfile              # Container configuration
│   └── data/                   # SQLite DB (generated on deployment)
│
├── frontend/                    # React TypeScript frontend
│   ├── src/
│   │   ├── pages/              # Main pages (GuestSearch, Landlord, etc.)
│   │   ├── components/         # Reusable components
│   │   ├── lib/                # API client and utilities
│   │   └── main.tsx            # Application entry point
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.ts          # Vite configuration
│   └── .env.production         # Production environment config
│
├── docs/                        # Documentation
│   ├── DEPLOYMENT.md           # Railway + Vercel deployment guide
│   ├── CUSTOM_DOMAIN.md        # Namecheap domain setup
│   ├── API_REFERENCE.md        # Complete API documentation
│   └── SETUP_GUIDE.md          # Local development setup
│
├── LICENSE                      # MIT License
└── README.md                    # This file
```

---

## 💡 How It Works

### NLP Search Pipeline
1. User enters natural language query (e.g., "2 guests in centro with WiFi under €100")
2. spaCy extracts entities (guests, location, amenities, price)
3. Listings are filtered by extracted criteria
4. Semantic search ranks results using sentence transformers
5. Hybrid scoring combines semantic similarity, lexical match, rating, and price

### RAG Neighborhood Chat
1. User asks question about a neighborhood
2. Relevant context is retrieved from knowledge base
3. OpenAI GPT-4o-mini generates contextual answer
4. Response includes specific information about the listing's neighborhood

### CV Amenity Detection
1. User uploads property photos
2. YOLOv8 performs object detection
3. OWL-ViT provides zero-shot classification
4. Detected objects are mapped to Airbnb amenities
5. Results are displayed with confidence scores

### Price Optimization
1. Current listing features are analyzed
2. Random Forest model predicts expected price
3. Feature importance identifies key price drivers
4. System recommends amenities to reach target price
5. Estimated price lift is calculated for each suggestion

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and endpoint list |
| `/health` | GET | Quick health check |
| `/search` | POST | NLP-powered semantic search |
| `/listings/featured` | GET | Get 8 featured high-rated listings |
| `/listings/{id}` | GET | Get detailed listing information |
| `/neighborhood-chat` | POST | RAG-powered Q&A about neighborhoods |
| `/landlord/prefill` | GET | Get prefilled demo listing data |
| `/landlord/amenities-from-images` | POST | Detect amenities from photos |
| `/landlord/price-suggestions` | POST | Get price optimization recommendations |

**Interactive API docs:** Visit `https://your-backend-url/docs` when running

👉 **See [docs/API_REFERENCE.md](docs/API_REFERENCE.md)** for detailed API documentation

---

## 🔧 Configuration

### Backend Environment Variables

Required for deployment (Railway):
```bash
OPENAI_API_KEY=sk-...                          # For RAG chat feature
ALLOWED_ORIGINS=https://your-frontend-url.com  # For CORS
```

### Frontend Environment Variables

Required for deployment (Vercel):
```bash
VITE_API_BASE_URL=https://your-backend-url.com  # Backend API URL
```

👉 **See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for step-by-step configuration

---

## 🌐 Deployment

### Production Deployment

The application is designed for easy deployment:

- **Backend → Railway**: Automatic data preparation, ML model loading, health checks
- **Frontend → Vercel**: Optimized builds, global CDN, automatic HTTPS

**Deployment features:**
- ✅ Automatic data download and preparation
- ✅ Cached ML embeddings for fast subsequent deployments  
- ✅ Health checks with extended timeouts for ML initialization
- ✅ Real-time startup logs with progress indicators
- ✅ Auto-scaling and monitoring

**First deployment:** 10-15 minutes (downloads data, computes embeddings)  
**Subsequent deployments:** 2-3 minutes (uses cached embeddings)

👉 **See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for complete deployment guide

### Custom Domain

Configure a custom domain from Namecheap:
- Frontend: `yourdomain.com`
- Backend API: `api.yourdomain.com`

👉 **See [docs/CUSTOM_DOMAIN.md](docs/CUSTOM_DOMAIN.md)** for domain setup guide

---

## 📚 Documentation

- **[Deployment Guide](docs/DEPLOYMENT.md)** - Deploy to Railway + Vercel
- **[Custom Domain Setup](docs/CUSTOM_DOMAIN.md)** - Configure Namecheap domain
- **[Local Setup Guide](docs/SETUP_GUIDE.md)** - Run locally for development
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation

---

## 🧪 Testing

### Test Backend

```bash
# Health check
curl https://your-backend.up.railway.app/health

# Search
curl -X POST https://your-backend.up.railway.app/search \
  -H "Content-Type: application/json" \
  -d '{"query": "2 guests with WiFi under 100"}'

# Featured listings
curl https://your-backend.up.railway.app/listings/featured
```

### Test Frontend

1. Visit your local host URL
2. Try searching: "cheap apartment in centro with WiFi"
3. Open a listing and view details
4. Test neighborhood chat (requires OpenAI API key)
5. Try landlord mode features

---

## 🎓 Academic Context

Built for **IE University** as a demonstration of practical machine learning applications in real-world scenarios.

### Key Learning Outcomes
- Production ML deployment with Railway + Vercel
- NLP-powered semantic search implementation
- RAG-based conversational AI
- Computer vision for practical applications
- ML-driven price optimization
- Full-stack application architecture

---

## 🙏 Acknowledgments

- **Dataset:** Madrid Airbnb listings from [Inside Airbnb](http://insideairbnb.com)
- **ML Models:** HuggingFace Transformers, spaCy, Ultralytics YOLOv8
- **UI Components:** [shadcn/ui](https://ui.shadcn.com)
- **Icons:** [Lucide React](https://lucide.dev)

---

## 📞 Support

For issues, questions, or suggestions:
- 📖 Check the [documentation](docs/)
- 🐛 Open an issue on GitHub
- 📧 Contact mttmainetti@gmail.com

---

## 🌟 Features Roadmap

- [ ] Multi-city support (Barcelona, Lisbon, etc.)
- [ ] Advanced filtering (pet-friendly, accessibility features)
- [ ] Booking simulation
- [ ] Host analytics dashboard
- [ ] Multi-language support

---

**⭐ If you find this project useful, please consider giving it a star!**
