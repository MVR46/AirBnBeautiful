# Madrid Airbnb ML Demo

A full-stack machine learning application showcasing advanced ML techniques for Airbnb property search and management. Features NLP-powered semantic search, RAG-based conversational AI, computer vision amenity detection, and price optimization.

![Project Banner](https://img.shields.io/badge/ML-Demo-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green) ![React](https://img.shields.io/badge/React-18-61DAFB) ![Python](https://img.shields.io/badge/Python-3.9+-blue) ![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)

## ✨ Features

### For Guests
- **🔍 Semantic Search**: Natural language search using sentence transformers and hybrid ranking (semantic + lexical + rating + price)
- **💬 Neighborhood Chat**: RAG-powered Q&A about neighborhoods using OpenAI GPT-4o-mini
- **📍 Interactive Map**: Explore listings with geolocation and filtering

### For Landlords
- **📸 CV Amenity Detection**: Automatically detect amenities from property photos using YOLOv8 and OWL-ViT
- **💰 Price Optimization**: ML-powered price suggestions with feature importance analysis
- **📊 Smart Recommendations**: Get personalized amenity recommendations to reach target prices

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PyTorch** - Deep learning framework
- **Sentence Transformers** - Semantic embeddings (all-MiniLM-L6-v2)
- **spaCy** - NLP and entity extraction
- **Scikit-learn** - ML models (RandomForest, TF-IDF)
- **YOLOv8** - Object detection
- **Transformers** - OWL-ViT zero-shot detection
- **OpenAI API** - GPT-4o-mini for conversational AI

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - Beautiful component library
- **React Router** - Navigation
- **TanStack Query** - Data fetching

### Data & ML
- **SQLite** - Listings database
- **NumPy** - Numerical computing
- **Pandas** - Data manipulation
- **1000+ Madrid Airbnb listings** with real data

## 📋 Prerequisites

- **Python 3.9 or higher**
- **Node.js 18 or higher**
- **4GB RAM minimum** (8GB recommended for CV features)
- **OpenAI API Key** (optional, only for RAG chat feature)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AirBnBeautiful.git
cd AirBnBeautiful
```

### 2. Run Setup (First Time Only)

```bash
./scripts/setup.sh
```

This will:
- Create Python virtual environment
- Install all Python dependencies
- Download spaCy language model
- Initialize the database
- Install frontend dependencies
- Create environment files

### 3. Configure Environment (Optional)

For the RAG neighborhood chat feature, add your OpenAI API key:

```bash
# Edit backend/.env
OPENAI_API_KEY=sk-your-actual-key-here
```

**Note**: All other features work without an API key!

### 4. Start the Application

You have two options:

**Option A: Start Everything Together**
```bash
./scripts/start-all.sh
```

**Option B: Start Services Separately**
```bash
# Terminal 1 - Backend
./scripts/start-backend.sh

# Terminal 2 - Frontend
./scripts/start-frontend.sh
```

### 5. Access the Application

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
AirBnBeautiful/
├── backend/                  # FastAPI backend
│   ├── main.py              # Main application entry point
│   ├── models.py            # Pydantic models
│   ├── data_service.py      # Database operations
│   ├── nlp_service.py       # NLP search & parsing
│   ├── rag_service.py       # RAG neighborhood chat
│   ├── cv_service.py        # Computer vision detection
│   ├── price_service.py     # Price optimization
│   ├── prepare_data.py      # Database initialization
│   ├── requirements.txt     # Python dependencies
│   ├── data/                # SQLite DB and embeddings
│   └── venv/                # Virtual environment (created by setup)
│
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── pages/           # Main pages (GuestSearch, Landlord, etc.)
│   │   ├── components/      # Reusable components
│   │   ├── lib/             # API client and utilities
│   │   └── main.tsx         # Application entry point
│   ├── package.json         # Node.js dependencies
│   └── vite.config.ts       # Vite configuration
│
├── docs/                     # Documentation
│   ├── API_REFERENCE.md     # Complete API documentation
│   └── SETUP_GUIDE.md       # Detailed setup instructions
│
├── notebooks/                # Jupyter research notebooks
│   ├── Feature 1 AirBnB NLP.ipynb
│   ├── Amenity Recognition AirBNB.ipynb
│   └── AI Project Airbnb Feature 3.ipynb
│
├── scripts/                  # Utility scripts
│   ├── setup.sh             # Initial setup script
│   ├── start-all.sh         # Start both services
│   ├── start-backend.sh     # Start backend only
│   ├── start-frontend.sh    # Start frontend only
│   └── test-api-connection.sh
│
└── README.md                 # This file
```

## 💡 Usage Guide

### Guest Mode

1. **Search for Listings**: Use natural language queries like:
   - "2 guests in Salamanca with WiFi under €100"
   - "spacious apartment near center with kitchen"
   - "pet friendly place in Retiro"

2. **View Listing Details**: Click any listing to see full details, photos, and amenities

3. **Chat About Neighborhoods**: Ask questions like:
   - "Is this neighborhood safe at night?"
   - "What restaurants are nearby?"
   - "How's the public transportation?"

### Landlord Mode

1. **Fill Property Details**: Add basic information about your listing

2. **Upload Photos**: Add property photos (or use sample photos)

3. **Detect Amenities**: Use AI to automatically detect amenities from photos

4. **Optimize Price**: Get ML-powered price suggestions and amenity recommendations

## 🧪 Testing the API

### Using the Interactive Docs

Visit http://localhost:8000/docs for Swagger UI with interactive API testing.

### Using curl

```bash
# Health check
curl http://localhost:8000/

# Search listings
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "2 guests with WiFi under 100"}'

# Get featured listings
curl http://localhost:8000/listings/featured

# Get listing details
curl http://localhost:8000/listings/{listing_id}
```

### Using the Test Script

```bash
./scripts/test-api-connection.sh
```

## 🔧 Development

### Project Architecture

The application follows a service-oriented architecture:

- **Data Service**: Handles all database operations
- **NLP Service**: Query parsing, semantic search, entity extraction
- **RAG Service**: Retrieval-augmented generation for chat
- **CV Service**: Computer vision amenity detection
- **Price Service**: Price prediction and optimization

### Adding New Features

1. **Backend**: Add endpoint in `main.py`, implement logic in appropriate service file
2. **Frontend**: Create components in `src/components/`, add pages in `src/pages/`
3. **API Client**: Update `src/lib/api.ts` with new API calls

### Running in Development Mode

Both servers run with hot reload enabled:
- Backend: Changes to `.py` files automatically reload the server
- Frontend: Changes to `.tsx` files trigger instant HMR updates

For detailed development instructions, see [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)

## 📚 Documentation

- **[API Reference](docs/API_REFERENCE.md)** - Complete API endpoint documentation
- **[Setup Guide](docs/SETUP_GUIDE.md)** - Detailed installation and configuration
- **[Interactive API Docs](http://localhost:8000/docs)** - Swagger UI (when server is running)

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check if virtual environment exists
ls backend/venv/

# Check if database exists
ls backend/data/airbnb.db

# Re-run setup if missing
./scripts/setup.sh
```

### Frontend won't start

```bash
# Check if node_modules exists
ls frontend/node_modules/

# Reinstall dependencies
cd frontend && npm install
```

### RAG chat not working

Ensure you have a valid OpenAI API key in `backend/.env`:
```bash
cat backend/.env | grep OPENAI_API_KEY
```

### Import errors or missing modules

```bash
# Activate venv and reinstall dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code:
- Follows existing code style
- Includes appropriate comments
- Updates documentation as needed
- Works with both backend and frontend

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Academic Context

Built for **IE University** as a demonstration of practical machine learning applications in real-world scenarios.

## 🙏 Acknowledgments

- Dataset: Madrid Airbnb listings from Inside Airbnb
- ML Models: HuggingFace Transformers, spaCy, Ultralytics YOLOv8
- UI Components: shadcn/ui
- Icons: Lucide React

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the [Setup Guide](docs/SETUP_GUIDE.md) for common problems
- Review [API Reference](docs/API_REFERENCE.md) for endpoint details

---

**⭐ If you find this project useful, please consider giving it a star!**
