# Custom Domain Setup with Namecheap

Complete guide to configure a custom domain from Namecheap for your AirBnBeautiful deployment.

---

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] **Completed deployment** on Railway and Vercel (see [DEPLOYMENT.md](./DEPLOYMENT.md))
- [ ] **Domain purchased** from Namecheap (or any domain registrar)
- [ ] **Railway backend URL** (e.g., `https://your-app.up.railway.app`)
- [ ] **Vercel frontend URL** (e.g., `https://your-app.vercel.app`)

**Recommended domain structure:**
- `yourdomain.com` → Frontend (Vercel)
- `www.yourdomain.com` → Frontend (Vercel)
- `api.yourdomain.com` → Backend (Railway)

---

## Part 1: Configure Domain for Frontend (Vercel)

### Step 1.1: Add Domain in Vercel

1. **Go to Vercel Dashboard** → Your project

2. **Navigate to Settings** → **Domains**

3. **Click "Add Domain"**

4. **Enter your domain:**
   - `yourdomain.com` (root domain)
   - Click "Add"

5. **Add www subdomain:**
   - Click "Add Domain" again
   - Enter: `www.yourdomain.com`
   - Click "Add"

6. **Vercel will show DNS configuration:**
   - Keep this page open - you'll need these values

### Step 1.2: Configure DNS Records in Namecheap

1. **Log in to Namecheap** at [namecheap.com](https://namecheap.com)

2. **Go to Domain List** → Click **"Manage"** next to your domain

3. **Navigate to "Advanced DNS" tab**

4. **Add DNS record for root domain:**
   - Click **"Add New Record"**
   - **Type:** `A Record`
   - **Host:** `@`
   - **Value:** `76.76.21.21` (Vercel's IP address)
   - **TTL:** `Automatic`
   - Click **✓** to save

5. **Add DNS record for www subdomain:**
   - Click **"Add New Record"**
   - **Type:** `CNAME Record`
   - **Host:** `www`
   - **Value:** `cname.vercel-dns.com.`
   - **TTL:** `Automatic`
   - Click **✓** to save

6. **Remove default records** (if they exist):
   - Delete any existing `A` records for `@`
   - Delete any existing `CNAME` records for `www`
   - Keep only the new records you just added

### Step 1.3: Verify Domain in Vercel

1. **Go back to Vercel** → **Settings** → **Domains**

2. **Click "Refresh"** next to your domain

3. **Wait for DNS propagation:**
   - Usually takes 5-60 minutes
   - Can take up to 48 hours in rare cases
   - Vercel will show checkmarks when ready

4. **SSL Certificate:**
   - Vercel automatically provisions SSL certificates
   - You'll see a green lock icon when ready
   - Both `http://` and `https://` will work, with automatic redirect to HTTPS

---

## Part 2: Configure Subdomain for Backend (Railway)

### Step 2.1: Add Custom Domain in Railway

1. **Go to Railway Dashboard** → Your backend service

2. **Navigate to Settings** → **Networking**

3. **Scroll to "Custom Domain" section**

4. **Click "Add Custom Domain"**

5. **Enter your subdomain:**
   - `api.yourdomain.com`
   - Click "Add"

6. **Railway will provide a CNAME target:**
   - Copy this value (e.g., `your-service.up.railway.app`)
   - Keep this page open

### Step 2.2: Add DNS Record in Namecheap

1. **Go back to Namecheap** → **Advanced DNS** tab

2. **Add DNS record for API subdomain:**
   - Click **"Add New Record"**
   - **Type:** `CNAME Record`
   - **Host:** `api`
   - **Value:** `your-service.up.railway.app.` (from Railway, step 2.1.6)
   - **TTL:** `Automatic`
   - Click **✓** to save

   > **Important:** Include the trailing dot (`.`) in the CNAME value

3. **Save all changes**

### Step 2.3: Verify Domain in Railway

1. **Go back to Railway** → **Settings** → **Networking**

2. **Check custom domain status:**
   - Should show "Active" after DNS propagates
   - Usually takes 5-60 minutes

3. **Test the domain:**
   ```bash
   curl https://api.yourdomain.com/health
   ```
   
   Expected response:
   ```json
   {"status":"healthy"}
   ```

---

## Part 3: Update Environment Variables

### Step 3.1: Update Railway Environment Variables

1. **Go to Railway** → Your backend service → **Variables** tab

2. **Update `ALLOWED_ORIGINS`** to include your custom domain:
   ```
   ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://your-app.vercel.app
   ```

   **Example:**
   ```
   ALLOWED_ORIGINS=https://airbnbeautiful.com,https://www.airbnbeautiful.com,https://airbnbeautiful.vercel.app
   ```

3. **Save changes** - Railway will auto-redeploy (~2-3 minutes)

### Step 3.2: Update Vercel Environment Variables

1. **Go to Vercel** → Your project → **Settings** → **Environment Variables**

2. **Update `VITE_API_BASE_URL`** to use your custom API domain:
   - Find the existing `VITE_API_BASE_URL` variable
   - Click **"Edit"**
   - Change value to: `https://api.yourdomain.com`
   - Apply to: **Production, Preview, and Development**

3. **Redeploy Vercel:**
   - Go to **Deployments** tab
   - Click **"..."** on the latest deployment
   - Click **"Redeploy"**
   - Wait for deployment to complete (~2-3 minutes)

---

## Part 4: DNS Propagation and Testing

### Step 4.1: Check DNS Propagation

**Use DNS checker tools:**
1. Visit [dnschecker.org](https://dnschecker.org)
2. Enter `yourdomain.com` → Check A record
3. Enter `www.yourdomain.com` → Check CNAME record
4. Enter `api.yourdomain.com` → Check CNAME record

**Expected results:**
- `yourdomain.com` → A record pointing to `76.76.21.21`
- `www.yourdomain.com` → CNAME pointing to `cname.vercel-dns.com`
- `api.yourdomain.com` → CNAME pointing to Railway

### Step 4.2: Test Frontend

1. **Visit your custom domain:**
   ```
   https://yourdomain.com
   ```

2. **Verify HTTPS works:**
   - Look for green lock icon in browser
   - Certificate should be valid
   - Automatic redirect from HTTP to HTTPS

3. **Test www subdomain:**
   ```
   https://www.yourdomain.com
   ```

4. **Check functionality:**
   - Search for listings
   - Open listing details
   - Try neighborhood chat
   - Test landlord mode

### Step 4.3: Test Backend API

1. **Test health endpoint:**
   ```bash
   curl https://api.yourdomain.com/health
   ```

2. **Test main endpoint:**
   ```bash
   curl https://api.yourdomain.com/
   ```

3. **Test featured listings:**
   ```bash
   curl https://api.yourdomain.com/listings/featured
   ```

### Step 4.4: Test Full Integration

1. **Open browser DevTools** (F12)

2. **Go to Console tab**

3. **Visit your frontend:** `https://yourdomain.com`

4. **Search for listings**

5. **Verify:**
   - ✅ No CORS errors
   - ✅ API calls go to `api.yourdomain.com`
   - ✅ Listings load successfully
   - ✅ All features work

---

## Troubleshooting

### Issue 1: DNS Not Propagating

**Symptoms:** Domain shows "Domain not found" or doesn't load

**Solutions:**

1. **Wait longer:**
   - DNS propagation typically takes 5-60 minutes
   - Can take up to 48 hours in rare cases
   - Be patient!

2. **Check DNS records:**
   - Use [dnschecker.org](https://dnschecker.org)
   - Verify records are configured correctly
   - Check for typos in values

3. **Clear DNS cache:**
   - **Mac:** `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`
   - **Windows:** `ipconfig /flushdns`
   - **Linux:** `sudo systemd-resolve --flush-caches`

4. **Try incognito mode:**
   - Browser cache can interfere
   - Incognito bypasses cache

### Issue 2: SSL Certificate Not Working

**Symptoms:** Browser shows "Not Secure" or certificate warning

**Solutions:**

1. **Wait for Vercel to provision certificate:**
   - Takes 5-15 minutes after DNS propagates
   - Check Vercel dashboard for status

2. **Verify DNS records are correct:**
   - A record for `@` must point to `76.76.21.21`
   - CNAME for `www` must point to `cname.vercel-dns.com`

3. **Force certificate refresh in Vercel:**
   - Go to Settings → Domains
   - Click "..." next to your domain
   - Click "Remove Domain"
   - Add domain again

### Issue 3: CORS Errors with Custom Domain

**Symptoms:** Frontend can't reach API, CORS policy errors in console

**Solutions:**

1. **Check `ALLOWED_ORIGINS` in Railway:**
   ```
   ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```
   - Include both root and www domains
   - No trailing slashes
   - Use exact domain names

2. **Verify Railway redeployed:**
   - Check Deployments tab
   - Wait for redeploy to complete

3. **Check `VITE_API_BASE_URL` in Vercel:**
   ```
   VITE_API_BASE_URL=https://api.yourdomain.com
   ```
   - No trailing slash
   - Must be exact custom domain

4. **Clear browser cache:**
   - Old API URLs might be cached
   - Try incognito mode

### Issue 4: API Subdomain Not Working

**Symptoms:** `api.yourdomain.com` doesn't resolve or shows errors

**Solutions:**

1. **Verify CNAME record in Namecheap:**
   - Host: `api`
   - Value: `your-service.up.railway.app.` (with trailing dot)
   - No typos

2. **Check Railway custom domain status:**
   - Should show "Active"
   - If not, wait for DNS propagation

3. **Test DNS propagation:**
   ```bash
   nslookup api.yourdomain.com
   dig api.yourdomain.com
   ```

4. **Check Railway logs:**
   - Ensure backend is running
   - Look for startup errors

### Issue 5: Redirect Loop

**Symptoms:** Page keeps redirecting endlessly

**Solutions:**

1. **Check Vercel domain configuration:**
   - Ensure both `yourdomain.com` and `www.yourdomain.com` are added
   - Vercel handles redirects automatically

2. **Remove conflicting DNS records:**
   - Don't have multiple A records for `@`
   - Don't have multiple CNAME records for `www`

3. **Clear all caches:**
   - Browser cache
   - DNS cache
   - Try different browser

---

## DNS Records Summary

Here's a quick reference of all DNS records you should have in Namecheap:

| Type | Host | Value | Purpose |
|------|------|-------|---------|
| A | @ | 76.76.21.21 | Root domain → Vercel |
| CNAME | www | cname.vercel-dns.com. | WWW subdomain → Vercel |
| CNAME | api | your-service.up.railway.app. | API subdomain → Railway |

**Notes:**
- Include trailing dots (`.`) in CNAME values
- TTL can be set to "Automatic" for all records
- Remove any default parking page records

---

## Post-Configuration Checklist

- [ ] `https://yourdomain.com` loads frontend
- [ ] `https://www.yourdomain.com` loads frontend
- [ ] `https://api.yourdomain.com/health` returns `{"status":"healthy"}`
- [ ] SSL certificates active (green lock icon)
- [ ] No CORS errors in browser console
- [ ] All application features work
- [ ] API calls use custom domain
- [ ] DNS records configured correctly

---

## Monitoring

### Domain Expiration

- **Set up auto-renewal** in Namecheap
- Domains expire annually (typically $10-15/year)
- Add calendar reminders 30 days before expiration

### SSL Certificates

- **Vercel manages SSL automatically**
- Certificates auto-renew
- No manual intervention needed

### DNS Changes

- **Avoid changing DNS records** without good reason
- DNS changes can take time to propagate
- Test changes in staging environment first

---

## Rolling Back

If you need to revert to Railway/Vercel default URLs:

1. **Update Vercel environment variable:**
   - Change `VITE_API_BASE_URL` back to Railway URL
   - Redeploy

2. **Update Railway environment variable:**
   - Change `ALLOWED_ORIGINS` back to Vercel URL
   - Wait for auto-redeploy

3. **Keep DNS records:**
   - Can leave them configured
   - Just don't use custom domains in app

---

## Additional Resources

- [Namecheap DNS Guide](https://www.namecheap.com/support/knowledgebase/article.aspx/767/10/how-to-change-dns-for-a-domain/)
- [Vercel Custom Domains](https://vercel.com/docs/concepts/projects/custom-domains)
- [Railway Custom Domains](https://docs.railway.app/deploy/exposing-your-app#custom-domains)
- [DNS Checker Tool](https://dnschecker.org)

---

**Need help?** Check the troubleshooting section above or refer to [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment issues.

