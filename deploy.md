# 🚀 Deployment Guide for Scene Stealer

## Quick Deploy to Render

### Step 1: Prepare Your Repository
1. Fork or clone this repository
2. Make sure all files are present:
   - `scene_stealer_web.py` (main app)
   - `requirements.txt` (dependencies)
   - `Procfile` (process config)
   - `render.yaml` (deployment config)
   - `runtime.txt` (Python version)

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `scene-stealer` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python scene_stealer_web.py`
   - **Plan**: Free (or paid for better performance)

### Step 3: Environment Variables (Optional)
If you want to use your own TMDB credentials:
- `TMDB_API_KEY`: Your API key
- `TMDB_READ_ACCESS_TOKEN`: Your access token

### Step 4: Deploy
1. Click "Create Web Service"
2. Wait for deployment (usually 2-5 minutes)
3. Your app will be live at: `https://your-service-name.onrender.com`

## Alternative: Deploy to Other Platforms

### Heroku
```bash
# Install Heroku CLI, then:
heroku create scene-stealer-app
git push heroku main
heroku open
```

### Railway
1. Connect GitHub repo to Railway
2. Deploy automatically

### Vercel (with modifications)
- Requires converting to serverless functions
- Not recommended for this Flask app

## Troubleshooting

### Common Issues:
1. **Build fails**: Check `requirements.txt` has correct versions
2. **App crashes**: Check logs for Python errors
3. **API errors**: TMDB API might be rate-limited (app has fallback data)
4. **Slow loading**: Free tier has cold starts, upgrade for better performance

### Checking Logs:
- **Render**: Go to service dashboard → "Logs" tab
- **Heroku**: `heroku logs --tail`

### Performance Tips:
- Free tiers sleep after inactivity
- First load might be slow (cold start)
- Consider upgrading to paid tier for production use

## Custom Domain (Optional)
1. In Render dashboard, go to "Settings"
2. Add your custom domain
3. Configure DNS records as instructed

---

**Your Scene Stealer app will be live and ready to help people find their perfect movie night! 🎬**