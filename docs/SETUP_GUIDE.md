# Setup Guide - Madrid Airbnb ML Demo

Complete installation and configuration guide for the Madrid Airbnb ML application.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Steps](#installation-steps)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Starting the Application](#starting-the-application)
- [Troubleshooting](#troubleshooting)
- [Development vs Production](#development-vs-production)

## System Requirements

### Minimum Requirements

- **Operating System**: macOS, Linux, or Windows (with WSL recommended)
- **Python**: 3.9 or higher
- **Node.js**: 18.0 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 3GB free space
- **Internet**: Required for initial setup (downloading models and dependencies)

### Optional Requirements

- **GPU**: CUDA-capable GPU for faster computer vision processing
- **OpenAI API Key**: Required only for RAG neighborhood chat feature

### Verify Prerequisites

```bash
# Check Python version
python3 --version  # Should be 3.9 or higher

# Check Node.js version
node --version     # Should be v18.0 or higher

# Check npm version
npm --version      # Should be 8.0 or higher
```

## Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/AirBnBeautiful.git
cd AirBnBeautiful
```

### Step 2: Run the Setup Script

The setup script automates the entire installation process:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This script will:
1. ✅ Verify Python and Node.js installations
2. ✅ Create Python virtual environment in `backend/venv/`
3. ✅ Install Python dependencies (PyTorch, FastAPI, etc.)
4. ✅ Download spaCy language model (`en_core_web_sm`)
5. ✅ Initialize SQLite database with Madrid Airbnb data
6. ✅ Install Node.js dependencies in `frontend/`
7. ✅ Create environment configuration files

**Expected Duration**: 5-10 minutes (depending on internet speed)

### Step 3: Manual Installation (Alternative)

If the setup script fails, you can install manually:

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Initialize database
python prepare_data.py

# Create environment file
cp .env.example .env
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
```

## Environment Configuration

### Backend Environment Variables

Create or edit `backend/.env`:

```bash
# Required for RAG chat feature
OPENAI_API_KEY=sk-your-actual-api-key-here

# Optional settings
VERBOSE=true
```

**Getting an OpenAI API Key:**

1. Visit https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key and paste it into `backend/.env`

**Note**: The RAG neighborhood chat feature requires an OpenAI API key. All other features (search, CV detection, price optimization) work without it.

### Frontend Environment Variables

Create or edit `frontend/.env`:

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000
```

**For production**, change this to your deployed backend URL:
```bash
VITE_API_URL=https://api.yourdomain.com
```

## Database Setup

### Understanding the Database

The application uses SQLite with Madrid Airbnb listings data:

- **Location**: `backend/data/airbnb.db`
- **Source**: `backend/data/listings_1000.csv` (1000 Madrid listings)
- **Tables**: `listings` table with all property information

### Initializing the Database

The database is automatically created during setup. To reinitialize:

```bash
cd backend
source venv/bin/activate
python prepare_data.py
```

This script:
1. Reads CSV data from `data/listings_1000.csv`
2. Cleans and processes the data
3. Creates SQLite database at `data/airbnb.db`
4. Inserts all listings

### Database Schema

Key fields in the `listings` table:

- `id`: Unique listing identifier
- `name`: Listing title
- `description`: Property description
- `neighbourhood_cleansed`: Neighborhood name
- `neighbourhood_group_cleansed`: District name
- `property_type`: Type of property (apartment, house, etc.)
- `room_type`: Entire place, private room, etc.
- `accommodates`: Number of guests
- `bedrooms`, `beds`, `bathrooms`: Room counts
- `amenities`: JSON array of amenities
- `price`: Price per night (EUR)
- `review_scores_rating`: Average rating
- `number_of_reviews`: Review count
- `latitude`, `longitude`: Geolocation

### Verifying the Database

```bash
# Check if database exists
ls -lh backend/data/airbnb.db

# Count listings (should be ~1000)
sqlite3 backend/data/airbnb.db "SELECT COUNT(*) FROM listings;"

# View sample listing
sqlite3 backend/data/airbnb.db "SELECT id, name, price FROM listings LIMIT 1;"
```

## Starting the Application

### Option 1: Start Both Services Together

```bash
./scripts/start-all.sh
```

This starts both backend and frontend in a single terminal. Press `Ctrl+C` to stop both.

### Option 2: Start Services Separately (Recommended for Development)

**Terminal 1 - Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start-frontend.sh
```

This approach is better for development as you can see logs from each service separately.

### Accessing the Application

After starting the servers:

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

### Verifying Everything Works

1. **Open Frontend**: Visit http://localhost:8080
2. **Test Search**: Try searching for "apartment in Centro with WiFi"
3. **Check API**: Visit http://localhost:8000/docs
4. **Test Featured Listings**: Click "Try it out" on `/listings/featured` endpoint

## Troubleshooting

### Common Setup Issues

#### Issue: Python version too old

**Error**: `Python 3.9 or higher required`

**Solution**:
```bash
# Install Python 3.9+ using pyenv (recommended)
curl https://pyenv.run | bash
pyenv install 3.9.18
pyenv global 3.9.18
```

Or download from https://www.python.org/downloads/

#### Issue: Node.js version too old

**Error**: `Node.js 18 or higher required`

**Solution**:
```bash
# Install Node.js 18 using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

Or download from https://nodejs.org/

#### Issue: Virtual environment creation fails

**Error**: `The virtual environment was not created successfully`

**Solution**:
```bash
# Install python3-venv package
sudo apt-get install python3-venv  # Ubuntu/Debian
brew install python@3.9            # macOS
```

#### Issue: pip install fails with compilation errors

**Error**: `error: command 'gcc' failed` or similar

**Solution**:
```bash
# Install build tools
sudo apt-get install build-essential python3-dev  # Ubuntu/Debian
xcode-select --install                             # macOS
```

#### Issue: spaCy model download fails

**Error**: `Can't find model 'en_core_web_sm'`

**Solution**:
```bash
cd backend
source venv/bin/activate
python -m spacy download en_core_web_sm --force
```

#### Issue: Database initialization fails

**Error**: `prepare_data.py fails` or `data not found`

**Solution**:
```bash
# Check CSV file exists
ls backend/data/listings_1000.csv

# Run preparation with verbose output
cd backend
source venv/bin/activate
python prepare_data.py --verbose
```

#### Issue: npm install fails

**Error**: `EACCES: permission denied` or similar

**Solution**:
```bash
# Fix npm permissions (don't use sudo with npm)
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Then try again
cd frontend
npm install
```

### Runtime Issues

#### Issue: Backend won't start

**Symptoms**: `uvicorn: command not found` or `ModuleNotFoundError`

**Solution**:
```bash
# Ensure virtual environment is activated
cd backend
source venv/bin/activate
which python  # Should point to backend/venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt

# Try starting manually
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Issue: Port already in use

**Error**: `Address already in use: 8000` or `8080`

**Solution**:
```bash
# Find and kill process using the port
lsof -ti:8000 | xargs kill -9  # For backend port 8000
lsof -ti:8080 | xargs kill -9  # For frontend port 8080

# Or use different ports
uvicorn main:app --port 8001  # Backend on 8001
npm run dev -- --port 8081     # Frontend on 8081
```

#### Issue: RAG chat returns 500 error

**Symptoms**: Chat feature doesn't work, API returns error

**Solution**:
```bash
# Check if API key is set
cat backend/.env | grep OPENAI_API_KEY

# Verify API key is valid (should start with sk-)
# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# Update .env with correct key
nano backend/.env
```

#### Issue: CV detection is very slow

**Symptoms**: Amenity detection takes 10+ seconds per image

**Solution**:
```bash
# Check if GPU is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# If GPU available, PyTorch should use it automatically
# If not, consider:
# 1. Using fewer images at once
# 2. Using smaller image resolutions
# 3. Installing CUDA toolkit for GPU acceleration
```

#### Issue: Frontend can't connect to backend

**Symptoms**: Network errors, CORS errors

**Solution**:
```bash
# Verify backend is running
curl http://localhost:8000/

# Check frontend .env
cat frontend/.env

# Ensure VITE_API_URL matches backend URL
echo "VITE_API_URL=http://localhost:8000" > frontend/.env

# Restart frontend
# (Stop with Ctrl+C and run ./start-frontend.sh again)
```

### Performance Issues

#### Issue: First request is very slow

**Explanation**: This is normal! The first request loads all ML models into memory:
- Sentence transformer embeddings (~100MB)
- spaCy language model (~40MB)
- YOLOv8 model (~6MB)
- TF-IDF vectorizer

**Expected**: 10-15 seconds for first request
**Subsequent requests**: <1 second

**No action needed** - this is expected behavior.

#### Issue: Out of memory errors

**Symptoms**: `Killed` or `MemoryError`

**Solution**:
```bash
# Reduce batch size for embeddings
# Edit backend/main.py, line ~111
batch_size=32  # Reduce from 64

# Use smaller dataset
# Copy listings_50.csv instead of listings_1000.csv
cp backend/data/listings_50.csv backend/data/listings_1000.csv
python backend/prepare_data.py
```

## Development vs Production

### Development Setup (Current)

✅ Hot reload enabled (automatic restart on code changes)
✅ Detailed error messages and stack traces
✅ CORS allows all origins
✅ No authentication or rate limiting
✅ SQLite database (simple, local)

### Production Setup (Recommendations)

For deploying to production:

#### Backend

```bash
# Use production ASGI server
pip install gunicorn

# Start with multiple workers
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or use Docker
docker build -t airbnb-backend .
docker run -p 8000:8000 airbnb-backend
```

#### Frontend

```bash
# Build for production
cd frontend
npm run build

# Serve static files with nginx or similar
# Or deploy to Vercel, Netlify, etc.
```

#### Environment

- ✅ Use environment secrets management (not .env files)
- ✅ Enable HTTPS
- ✅ Add authentication and authorization
- ✅ Implement rate limiting
- ✅ Use PostgreSQL instead of SQLite
- ✅ Add logging and monitoring
- ✅ Enable CORS only for specific domains
- ✅ Use CDN for static assets

#### Security Checklist

- [ ] Change all default secrets
- [ ] Validate all user inputs
- [ ] Use HTTPS only
- [ ] Implement API rate limiting
- [ ] Add request logging
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Regular dependency updates
- [ ] Security headers configured
- [ ] Database backups automated
- [ ] API key rotation policy

## Next Steps

Once setup is complete:

1. **Explore the Application**: Try the guest and landlord modes
2. **Read API Documentation**: Visit http://localhost:8000/docs
3. **Review the Code**: Start with `backend/main.py` and `frontend/src/App.tsx`
4. **Experiment**: Try modifying queries, adding features
5. **Contribute**: See the main README for contribution guidelines

## Getting Help

If you encounter issues not covered here:

1. Check the [API Reference](./API_REFERENCE.md)
2. Review the main [README](../README.md)
3. Search existing GitHub issues
4. Open a new issue with:
   - Operating system and versions
   - Error messages (full stack trace)
   - Steps to reproduce
   - What you've tried so far

---

**Ready to start?** Run `./scripts/setup.sh` and you'll be up and running in 10 minutes!

