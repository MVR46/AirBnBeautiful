# AirBnBeautiful Deployment Guide

Complete guide to deploy your Airbnb ML application to production with Railway (backend) and Vercel (frontend).

---

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] GitHub account with your code pushed to a repository
- [ ] Railway account (sign up at [railway.app](https://railway.app))
- [ ] Vercel account (sign up at [vercel.com](https://vercel.com))
- [ ] OpenAI API key (for RAG chat functionality)

**Optional:**
- [ ] Custom domain from Namecheap (see [CUSTOM_DOMAIN.md](./CUSTOM_DOMAIN.md))

---

## Part 1: Deploy Backend to Railway

### Step 1.1: Prepare Your Repository

The repository is already configured for deployment with:
- `backend/Procfile` - Railway start command
- `backend/runtime.txt` - Python version specification
- `backend/nixpacks.toml` - System dependencies for OpenCV/YOLO
- `backend/railway.json` - Health check configuration
- `backend/start.sh` - Startup script with automatic data preparation

### Step 1.2: Deploy on Railway

> **Note:** The backend automatically downloads and prepares the Airbnb dataset on first deployment. No manual data setup required!

1. **Go to [railway.app](https://railway.app)** and sign in with GitHub

2. **Click "New Project"** → **"Deploy from GitHub repo"**

3. **Select your `AirBnBeautiful` repository**

4. **Configure the service:**
   - Click on the deployed service
   - Go to **Settings** → **Root Directory**
   - Set root directory to: `backend`

5. **Add Environment Variables:**
   - Go to **Variables** tab
   - Add:
     ```
     OPENAI_API_KEY=your-actual-openai-key
     ```
   - **Note:** `PORT` is automatically set by Railway

6. **Deploy!**
   - Railway will automatically start the deployment
   - **First deployment takes up to 10 minutes** because:
     - ML dependencies are installed (~2-3 min)
     - Airbnb dataset is downloaded and processed (~2-3 min)
     - ML models are loaded (~2-3 min)
     - Embeddings are computed (~2-3 min)
   - Subsequent deployments are faster (~2-3 min with cached embeddings)

7. **Monitor the deployment:**
   - Click on the **Deployments** tab
   - Click **"View Logs"**
   - You should see progress through 10 initialization steps:
     ```
     ============================================================
     Starting Airbnb ML Backend
     ============================================================

     1. Loading listings database...
        Loaded 1000 listings

     2. Initializing NLP models...
        ✓ NLP models loaded

     3. Preparing amenity normalization...
        ✓ Amenities normalized

     4. Building amenity clusters...
        ✓ Clusters built

     5. Building label pools (neighborhoods, types)...
        ✓ Label pools ready

     6. Preparing listing embeddings...
        ✓ Prepared 1000 listing texts
        ✓ Loaded cached embeddings: (1000, 384)

     7. Building TF-IDF index...
        ✓ TF-IDF index ready

     8. Building canonical amenities for filtering...
        ✓ Canonical amenities ready

     9. Initializing RAG service...
        ✓ RAG service ready

     10. Training price optimization model...
        ✓ Price model trained

     ============================================================
     ✅ Backend ready! All services initialized.
     ============================================================

     INFO:     Application startup complete.
     INFO:     Uvicorn running on http://0.0.0.0:8000
     ```

8. **Get your Railway URL:**
   - Go to **Settings** → **Networking**
   - Copy the public URL (e.g., `https://your-app.up.railway.app`)
   - Test it by visiting: `https://your-app.up.railway.app/`
   - You should see: `{"status": "running", "message": "AirBnBeautiful ML Backend is ready", ...}`

> **💡 Pro Tip:** The startup script automatically checks if the database exists. If not, it downloads the Madrid Airbnb dataset from GitHub and prepares it. This means you can deploy directly without any manual data setup!

---

## Part 2: Deploy Frontend to Vercel

### Step 2.1: Prepare Frontend Configuration

The repository includes `frontend/.env.production` with the default Railway URL. You'll update this with your actual Railway URL via Vercel environment variables.

### Step 2.2: Deploy on Vercel

1. **Go to [vercel.com](https://vercel.com)** and sign in with GitHub

2. **Click "Add New..." → "Project"**

3. **Import your `AirBnBeautiful` repository**

4. **Configure Project:**
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

5. **Add Environment Variables:**
   - Click **Environment Variables**
   - Add:
     ```
     Name: VITE_API_BASE_URL
     Value: https://your-app.up.railway.app
     ```
     (Replace with your actual Railway URL from Step 1.2.8)
   - Apply to: **Production, Preview, and Development**

6. **Click "Deploy"**

7. **Wait for deployment** (usually 2-3 minutes)

8. **Get your Vercel URL:**
   - Copy the deployment URL (e.g., `https://airbnbeautiful.vercel.app`)
   - Visit it to test your frontend

---

## Part 3: Connect Frontend and Backend

### Step 3.1: Update Backend CORS

1. **Go back to Railway** → Your backend service → **Variables**

2. **Add environment variable:**
   ```
   ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,https://your-vercel-app-git-deployment-vercel-railway.vercel.app
   ```
   
   Replace with your actual Vercel URLs (include both production and preview URL patterns)

3. **Save** - Railway will auto-redeploy (~2-3 minutes)

### Step 3.2: Verify the Connection

Once Railway redeploys, test the full application:

1. **Visit your Vercel URL**
2. **Open browser DevTools** (F12) → **Console** tab
3. **Try searching for listings** (e.g., "2 guests in centro under 100")
4. **Check for**:
   - ✅ No CORS errors in console
   - ✅ Listings appear on the page
   - ✅ API calls succeed (check Network tab)

---

## Part 4: Verification & Testing

### Test Backend Endpoints

```bash
# Health check (responds immediately)
curl https://your-app.up.railway.app/health

# Root endpoint
curl https://your-app.up.railway.app/

# Featured listings
curl https://your-app.up.railway.app/listings/featured
```

**Expected responses:**
- `/health` → `{"status":"healthy"}`
- `/` → `{"status":"running","message":"AirBnBeautiful ML Backend is ready",...}`
- `/listings/featured` → `{"listings":[...]}`

### Test Frontend Features

1. **Search functionality:**
   - Try queries like "cheap apartment in centro with WiFi"
   - Verify results appear

2. **Listing details:**
   - Click on a listing
   - Check that details load correctly

3. **Neighborhood chat:**
   - Ask questions about the neighborhood
   - Verify RAG responses (requires OpenAI API key)

4. **Landlord mode:**
   - Test amenity detection from photos
   - Try price optimization features

---

## Part 5: Troubleshooting

### Issue 1: Railway Shows 502 Bad Gateway

**Symptoms:** Backend returns 502 error

**Common Causes:**
1. **Still starting up** - First deployment takes up to 10 minutes
   - Check logs for progress through initialization steps
   - Wait for "✅ Backend ready!" message

2. **Stuck during initialization** - Look at Railway logs to see where it's stuck:
   - Step 2 (NLP models): Downloads spaCy model (~2-3 min)
   - Step 6 (Embeddings): Computes embeddings on first run (~2-3 min)
   - If stuck > 10 minutes, redeploy

3. **Out of memory** - ML models need 1GB+ RAM
   - Upgrade Railway plan if needed

### Issue 2: CORS Errors

**Symptoms:** Frontend can't reach backend, console shows CORS policy errors

**Solutions:**
1. Verify `ALLOWED_ORIGINS` in Railway includes your exact Vercel URL
2. Check that Railway redeployed after you updated the variable
3. Try with and without trailing slash in URL
4. Clear browser cache or try incognito mode

**Example of correct ALLOWED_ORIGINS:**
```
https://airbnbeautiful.vercel.app,https://airbnbeautiful-git-deployment-vercel-railway.vercel.app
```

### Issue 3: Frontend Shows "Failed to fetch"

**Symptoms:** Frontend shows connection errors

**Check:**
1. Is Railway backend running? Visit the URL directly in browser
2. Is `VITE_API_BASE_URL` set correctly in Vercel?
3. Did Vercel redeploy after you set the environment variable?
   - Go to Deployments → Click "..." → Redeploy
4. Check browser Network tab for actual error message

### Issue 4: Environment Variables Not Updating

**Symptoms:** Changes to environment variables don't take effect

**Solutions:**
- **Vercel:** Environment variable changes require a new deployment
  - Go to Deployments tab → Click "..." → Redeploy
- **Railway:** Changes trigger auto-redeploy automatically
  - Wait 2-3 minutes for redeploy to complete

### Issue 5: Database Not Found Error

**Status:** ✅ **This issue is fixed automatically!**

The backend now includes automatic data preparation:
- On first deployment, if database doesn't exist, it's automatically created
- The `start.sh` script handles this before starting the server
- You'll see: "📦 Preparing data (this may take 2-3 minutes on first deployment)..."

If you still see this error:
1. Check that `start.sh` file exists in backend directory
2. Verify Procfile contains: `web: bash start.sh`
3. Check Railway logs for network issues during dataset download
4. Try redeploying

### Issue 6: Railway Build Fails with OpenCV Error

**Symptoms:** Deployment fails with: `ImportError: libGL.so.1: cannot open shared object file`

**Solution:**
- This is fixed by the `nixpacks.toml` file in the backend directory
- If missing, create it with:
  ```toml
  [phases.setup]
  aptPkgs = [
      "libgl1-mesa-glx",
      "libglib2.0-0",
      "libsm6",
      "libxext6",
      "libxrender-dev",
      "libgomp1",
      "libglu1-mesa"
  ]
  ```
- Railway will automatically detect and install these dependencies
- Redeploy after adding the file

---

## Post-Deployment Checklist

- [ ] Backend accessible and returns health check
- [ ] Frontend loads without errors
- [ ] Search functionality works
- [ ] Listing details display correctly
- [ ] No CORS errors in browser console
- [ ] API calls succeed (check Network tab)
- [ ] Both Railway and Vercel show active deployments

---

## Monitoring & Maintenance

### Railway Monitoring

- **View Logs:** Railway Dashboard → Deployments → View Logs
- **Check Metrics:** Monitor CPU, Memory, and Network usage
- **Set up Alerts:** Railway can notify you of crashes

### Vercel Monitoring

- **Analytics:** Vercel Dashboard → Analytics (track page views, performance)
- **Deployment History:** See all deployments and rollback if needed
- **Preview Deployments:** Each push to non-main branches creates preview URLs

### Cost Considerations

**Railway:**
- Free tier: $5 credit/month (enough for testing)
- Hobby plan: $5/month for more resources
- ML models need at least 1GB RAM

**Vercel:**
- Free tier: Unlimited deployments for personal projects
- Pro plan: $20/month for commercial use and analytics

---

## Updating Your Application

Both Railway and Vercel support automatic deployments:

1. **Make changes locally**
2. **Test locally** (see [SETUP_GUIDE.md](./SETUP_GUIDE.md))
3. **Commit and push to GitHub**
4. **Both services auto-deploy** from your main branch
5. **Monitor deployments** in respective dashboards

### Rollback if Needed

**Railway:**
- Go to Deployments → Click previous deployment → Redeploy

**Vercel:**
- Go to Deployments → Click "..." on previous deployment → Promote to Production

---

## Next Steps

- **Custom Domain:** See [CUSTOM_DOMAIN.md](./CUSTOM_DOMAIN.md) for Namecheap setup
- **API Reference:** See [API_REFERENCE.md](./API_REFERENCE.md) for endpoint documentation
- **Local Development:** See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for local setup

---

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Build Guide](https://vitejs.dev/guide/build.html)

---

**Need help?** Check the troubleshooting section above or open an issue on GitHub.

