# AirBnBeautiful Deployment Guide

Complete guide to deploy your Airbnb ML application with:
- 🚂 **Backend** on Railway
- ⚡ **Frontend** on Vercel  
- 🌐 **Custom Domain** from Namecheap

---

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] GitHub account with your code pushed to a repository
- [ ] Railway account (sign up at [railway.app](https://railway.app))
- [ ] Vercel account (sign up at [vercel.com](https://vercel.com))
- [ ] Namecheap domain purchased
- [ ] OpenAI API key (for RAG chat functionality)

---

## Part 1: Deploy Backend to Railway 🚂

### Step 1.1: Prepare Backend for Deployment

1. **Create a `.env` file in the `backend/` directory** (if not exists):
   ```bash
   OPENAI_API_KEY=your-openai-api-key-here
   ```

2. **Create `backend/runtime.txt`** to specify Python version:
   ```
   python-3.9.18
   ```

3. **Create `backend/Procfile`** (Railway start command):
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Update CORS in `backend/main.py`** (line 161-167):
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:8080",
           "https://yourdomain.com",  # Add your custom domain
           "https://*.vercel.app"     # Allow Vercel preview deployments
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

### Step 1.2: Deploy on Railway

> **Important:** The backend includes a `nixpacks.toml` file that installs system dependencies required for OpenCV and YOLO (libGL, libGLib, etc.). Railway will automatically detect and use this configuration.

> **✨ NEW: Automatic Data Preparation** - The backend now automatically downloads and prepares the Airbnb dataset on first deployment! No manual data setup required. See details below.

1. **Go to [railway.app](https://railway.app)** and sign in with GitHub

2. **Click "New Project"** → **"Deploy from GitHub repo"**

3. **Select your `AirBnBeautiful` repository**

4. **Configure the service:**
   - Click on the deployed service
   - Go to **Settings** → **Root Directory**
   - Set root directory to: `backend`

5. **Add Environment Variables:**
   - Go to **Variables** tab
   - Add these variables:
     ```
     OPENAI_API_KEY=your-actual-openai-key
     ```
   - **Note:** `PORT` and `PYTHON_VERSION` are automatically set by Railway

6. **Deploy!**
   - Railway will automatically use the `Procfile` to start the app
   - **First deployment takes 5-10 minutes** because:
     - ML dependencies are installed (~2-3 min)
     - Airbnb dataset is downloaded and processed (~2-3 min)
     - ML models are loaded (~1 min)
   - Subsequent deployments are faster (~2-3 min)

7. **Monitor the deployment:**
   - Click on the **Deployments** tab
   - Watch the logs - you should see:
     ```
     ⚠️  Database not found at data/airbnb.db
     📦 Preparing data (this may take 2-3 minutes on first deployment)...
     Loading Madrid dataset...
     ✅ Data preparation completed successfully!
     🌐 Starting FastAPI server...
     ```

8. **Get your Railway URL:**
   - Go to **Settings** → **Networking**
   - Copy the public URL (e.g., `https://your-app.up.railway.app`)
   - Test it by visiting: `https://your-app.up.railway.app/`
   - You should see: `{"status": "running", "endpoints": [...]}`

> **💡 Pro Tip:** The startup script (`start.sh`) automatically checks if the database exists. If not, it downloads the Madrid Airbnb dataset from GitHub and prepares it. This means you can deploy directly without any manual data setup!

### Step 1.3: Set Up Custom Domain for Backend (Optional)

1. **In Railway, go to Settings → Networking → Custom Domain**

2. **Add your subdomain** (e.g., `api.yourdomain.com`)

3. **Railway will provide DNS records** - save these for later

---

## Part 2: Deploy Frontend to Vercel ⚡

### Step 2.1: Prepare Frontend for Deployment

1. **Create `frontend/.env.production`**:
   ```
   VITE_API_BASE_URL=https://your-app.up.railway.app
   ```
   
   Replace with your actual Railway URL (or `https://api.yourdomain.com` if using custom domain)

2. **Verify build works locally:**
   ```bash
   cd frontend
   npm run build
   ```

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
   - Apply to: **Production, Preview, and Development**

6. **Click "Deploy"**

7. **Wait for deployment** (usually 2-3 minutes)

8. **Get your Vercel URL:**
   - Copy the deployment URL (e.g., `https://airbnbeautiful.vercel.app`)
   - Visit it to test your frontend

### Step 2.3: Update Backend CORS

1. **Go back to Railway** → Your backend service → **Variables**

2. **Add new environment variable:**
   ```
   ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,https://yourdomain.com
   ```

3. **Update `backend/main.py`** CORS to use environment variable:
   ```python
   import os
   
   # Get allowed origins from environment
   allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(",")
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=allowed_origins,
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **Commit and push changes** - Railway will auto-redeploy

---

## Part 3: Configure Custom Domain on Namecheap 🌐

### Step 3.1: Configure Domain for Frontend (Vercel)

1. **In Vercel Dashboard:**
   - Go to your project → **Settings** → **Domains**
   - Click **Add Domain**
   - Enter your domain: `yourdomain.com`
   - Also add: `www.yourdomain.com`

2. **Vercel will show DNS records** you need to add

3. **In Namecheap:**
   - Log in to [namecheap.com](https://namecheap.com)
   - Go to **Domain List** → Click **Manage** on your domain
   - Go to **Advanced DNS** tab

4. **Add these DNS records for Vercel:**

   For root domain (`yourdomain.com`):
   ```
   Type: A Record
   Host: @
   Value: 76.76.21.21
   TTL: Automatic
   ```

   For www subdomain:
   ```
   Type: CNAME Record
   Host: www
   Value: cname.vercel-dns.com
   TTL: Automatic
   ```

5. **Back in Vercel:**
   - Click **Refresh** on the domain
   - Wait 5-60 minutes for DNS propagation
   - Vercel will automatically provision SSL certificate

### Step 3.2: Configure Subdomain for Backend (Railway)

1. **In Railway Dashboard:**
   - Go to your backend service → **Settings** → **Networking**
   - Scroll to **Custom Domain**
   - Click **Add Custom Domain**
   - Enter: `api.yourdomain.com`

2. **Railway will provide a CNAME target** (e.g., `your-service.up.railway.app`)

3. **In Namecheap Advanced DNS:**
   - Click **Add New Record**
   - Add this record:
     ```
     Type: CNAME Record
     Host: api
     Value: your-service.up.railway.app
     TTL: Automatic
     ```

4. **Save Changes** and wait for DNS propagation (5-60 minutes)

### Step 3.3: Update Environment Variables with Custom Domains

1. **In Railway (Backend):**
   - Update `ALLOWED_ORIGINS` variable:
     ```
     ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://your-vercel-app.vercel.app
     ```

2. **In Vercel (Frontend):**
   - Update `VITE_API_BASE_URL`:
     ```
     VITE_API_BASE_URL=https://api.yourdomain.com
     ```
   - Trigger a **Redeploy** from the Deployments tab

---

## Part 4: Verification & Testing ✅

### Step 4.1: Test Backend

1. **Visit your backend URL:**
   ```
   https://api.yourdomain.com/
   ```
   
2. **You should see:**
   ```json
   {
     "status": "running",
     "endpoints": [...]
   }
   ```

3. **Test featured listings:**
   ```
   https://api.yourdomain.com/listings/featured
   ```

### Step 4.2: Test Frontend

1. **Visit your frontend:**
   ```
   https://yourdomain.com
   ```

2. **Test the application:**
   - Try searching for listings
   - Check if listings load
   - Open a listing detail page
   - Try the neighborhood chat
   - Test the landlord mode

### Step 4.3: Check Browser Console

1. **Open Developer Tools** (F12)
2. **Check Console tab** - no CORS errors should appear
3. **Check Network tab** - API calls should go to `api.yourdomain.com`

---

## Part 5: Common Issues & Troubleshooting 🔧

### Issue 1: CORS Errors

**Symptoms:** Frontend can't reach backend, console shows CORS policy errors

**Solution:**
- Verify `ALLOWED_ORIGINS` in Railway includes your Vercel domain
- Check CORS configuration in `backend/main.py`
- Ensure both HTTP and HTTPS are handled correctly

### Issue 2: "Failed to fetch" errors

**Symptoms:** Frontend shows connection errors

**Solution:**
- Verify `VITE_API_BASE_URL` in Vercel environment variables
- Check if backend is running: visit `https://api.yourdomain.com/`
- Look at Railway logs for errors

### Issue 3: DNS not propagating

**Symptoms:** Domain shows "Domain not found" or redirects incorrectly

**Solution:**
- Wait longer (DNS can take up to 48 hours, usually 5-60 minutes)
- Use [dnschecker.org](https://dnschecker.org) to verify DNS records
- Clear your browser cache or try incognito mode
- Flush DNS: `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (Mac)

### Issue 4: Database not found error (FIXED)

**Symptoms:** Deployment fails with `FileNotFoundError: Database not found: data/airbnb.db`

**Status:** ✅ **This issue is now fixed automatically!**

**What changed:**
- The backend now includes an automatic data preparation feature
- On first deployment, if the database doesn't exist, it's automatically created
- The `start.sh` script handles this before starting the server

**What you'll see in logs:**
```
⚠️  Database not found at data/airbnb.db
📦 Preparing data (this may take 2-3 minutes on first deployment)...
Loading Madrid dataset...
✅ Data preparation completed successfully!
```

**If you still see this error:**
1. Check that `start.sh` file exists in your backend directory
2. Verify the `Procfile` contains: `web: bash start.sh`
3. Check Railway logs for network issues during dataset download
4. Try redeploying - Railway will retry the data preparation

### Issue 5: Railway build fails with OpenCV/libGL error

**Symptoms:** Deployment fails with error: `ImportError: libGL.so.1: cannot open shared object file`

**Solution:**
- This error occurs when OpenCV system dependencies are missing
- **Fix:** Ensure `backend/nixpacks.toml` file exists with the following content:
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

### Issue 6: Railway build fails (general)

**Symptoms:** Deployment fails with module import errors

**Solution:**
- Check Railway logs for specific error
- Verify `requirements.txt` is correct
- Ensure Python version is set to 3.9
- Some ML models may need more memory - upgrade Railway plan if needed

### Issue 7: Vercel build fails

**Symptoms:** Deployment fails during build

**Solution:**
- Check build logs in Vercel dashboard
- Verify `package.json` dependencies are correct
- Try building locally: `npm run build`
- Check if `VITE_API_BASE_URL` is set correctly

### Issue 8: Environment variables not updating

**Symptoms:** Changes to env vars don't take effect

**Solution:**
- **Vercel:** Environment variable changes require a new deployment
  - Go to Deployments tab → Click "..." → Redeploy
- **Railway:** Changes trigger auto-redeploy, but you can force it:
  - Go to Deployments tab → Redeploy

---

## Part 6: Post-Deployment Checklist ✨

- [ ] Backend accessible at `https://api.yourdomain.com/`
- [ ] Frontend accessible at `https://yourdomain.com`
- [ ] SSL certificates are active (🔒 in browser)
- [ ] Search functionality works
- [ ] Listing details load correctly
- [ ] Neighborhood chat responds
- [ ] Landlord mode features work
- [ ] No CORS errors in browser console
- [ ] Both `www` and non-`www` versions redirect correctly

---

## Part 7: Monitoring & Maintenance 📊

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
- Pro plan: $20/month for commercial use, analytics, and team features

**Namecheap:**
- Domain renewal: varies by TLD (typically $10-15/year)

---

## Part 8: Updating Your Application 🔄

### Backend Updates

1. **Make changes locally**
2. **Test locally:** `cd backend && python main.py`
3. **Commit and push to GitHub**
4. **Railway auto-deploys** from main branch
5. **Monitor deployment** in Railway dashboard

### Frontend Updates

1. **Make changes locally**
2. **Test locally:** `cd frontend && npm run dev`
3. **Commit and push to GitHub**
4. **Vercel auto-deploys** from main branch
5. **Monitor deployment** in Vercel dashboard

### Rollback if Needed

**Railway:**
- Go to Deployments → Click previous deployment → Redeploy

**Vercel:**
- Go to Deployments → Click "..." on previous deployment → Promote to Production

---

## 🎉 Congratulations!

Your AirBnBeautiful application is now live with:
- ✅ Production-ready backend on Railway
- ✅ Fast, globally-distributed frontend on Vercel
- ✅ Custom domain with SSL
- ✅ Automatic deployments on every push

**Your live URLs:**
- Frontend: `https://yourdomain.com`
- Backend API: `https://api.yourdomain.com`

---

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [Namecheap DNS Guide](https://www.namecheap.com/support/knowledgebase/article.aspx/767/10/how-to-change-dns-for-a-domain/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Build Guide](https://vitejs.dev/guide/build.html)

---

**Need help?** Check the troubleshooting section above or review platform-specific documentation.

