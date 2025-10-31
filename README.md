# 🎬 Scene Stealer - Tonight's Watchlist Generator

A modern web app that curates personalized movie watchlists with intelligent vibe classification using TMDB data.

## Features

- 🎯 **Smart Curation**: AI-powered vibe classification (thriller, comfort, weird, action, romance, etc.)
- 🎨 **Modern UI**: Netflix-inspired design with smooth animations
- 🔍 **Interactive Filtering**: Real-time search and vibe-based filtering
- 📱 **Responsive**: Works perfectly on mobile and desktop
- 💾 **Export**: Save watchlists as JSON files
- 🎲 **Surprise Mode**: Random movie recommendations

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   python scene_stealer_web.py
   ```

3. **Open in browser:**
   ```
   http://localhost:5000
   ```

## Deploy to Render

### Option 1: One-Click Deploy
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Option 2: Manual Deploy

1. **Fork this repository** to your GitHub account

2. **Create a new Web Service** on [Render](https://render.com):
   - Connect your GitHub repository
   - Choose "scene-stealer" as the service name
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `python scene_stealer_web.py`
   - Choose the free plan

3. **Deploy**: Render will automatically build and deploy your app

4. **Access**: Your app will be available at `https://scene-stealer-[random].onrender.com`

## Environment Variables

The app works out of the box with pre-configured TMDB API credentials. For production use, consider setting your own:

- `TMDB_API_KEY`: Your TMDB API key
- `TMDB_READ_ACCESS_TOKEN`: Your TMDB read access token
- `PORT`: Server port (automatically set by Render)

## API Endpoints

- `GET /` - Main web interface
- `GET /api/movies` - Get curated movie list
- `GET /api/generate` - Generate new watchlist
- `GET /api/surprise` - Get random movie recommendation
- `GET /api/test` - Test API connectivity

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: Vanilla JavaScript, CSS3
- **API**: TMDB (The Movie Database)
- **Deployment**: Render
- **Styling**: Modern CSS with gradients and animations

## File Structure

```
scene-stealer/
├── scene_stealer_web.py    # Main application (single file)
├── requirements.txt        # Python dependencies
├── Procfile               # Process configuration
├── render.yaml            # Render deployment config
└── README.md              # This file
```

## Contributing

This is a single-file application designed for simplicity. Feel free to fork and customize!

## License

MIT License - feel free to use this for your own projects.

---

**Made with ❤️ for movie lovers who can't decide what to watch tonight!**