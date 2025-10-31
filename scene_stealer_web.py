#!/usr/bin/env python3
"""
Scene Stealer Web - Tonight's Watchlist Generator
A modern web app for curated movie watchlists with vibe classification
"""

from flask import Flask, render_template_string, jsonify, request
import requests
import json
import re
import random
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# TMDB API Configuration
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_API_KEY = "de7accef476898dc3ad71660e6ff3da7"
TMDB_READ_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkZTdhY2NlZjQ3Njg5OGRjM2FkNzE2NjBlNmZmM2RhNyIsIm5iZiI6MTc2MTkzMTc3MS44MzksInN1YiI6IjY5MDRmMWZiOGY0MDE3MDZkNGY5MjQ4NyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.7XDPlWsIUfWs73N4ja-WspLUa8d4tGfrqiAbHoRVh8A"

# Global cache
movie_cache = {}
cache_timestamp = None
CACHE_DURATION = 3600  # 1 hour

# Fallback data in case API is unavailable
FALLBACK_MOVIES = [
    {
        'id': '1', 'title': 'The Shawshank Redemption', 'year': '1994', 'rating': 9.3,
        'genres': ['Drama'], 'overview': 'Two imprisoned men bond over years, finding solace and eventual redemption.',
        'vibes': ['😊 feel-good', '🧠 mind-bending'], 'poster_url': None
    },
    {
        'id': '2', 'title': 'Pulp Fiction', 'year': '1994', 'rating': 8.9,
        'genres': ['Crime', 'Drama'], 'overview': 'The lives of two mob hitmen, a boxer, and others intertwine.',
        'vibes': ['🔪 thriller', '🌑 dark'], 'poster_url': None
    },
    {
        'id': '3', 'title': 'The Dark Knight', 'year': '2008', 'rating': 9.0,
        'genres': ['Action', 'Crime'], 'overview': 'Batman faces the Joker in this epic superhero thriller.',
        'vibes': ['💥 action', '🔪 thriller'], 'poster_url': None
    }
]

# Vibe classification with confidence scoring
VIBE_KEYWORDS = {
    "🔪 thriller": {
        "keywords": ["thriller", "suspense", "murder", "mystery", "crime", "detective", "killer", "investigation", "psychological"],
        "color": "#dc2626"
    },
    "🛋️ comfort": {
        "keywords": ["family", "friendship", "heartwarming", "feel-good", "comedy", "romantic comedy", "uplifting", "wholesome"],
        "color": "#ea580c"
    },
    "👽 weird": {
        "keywords": ["surreal", "bizarre", "strange", "experimental", "cult", "absurd", "unconventional", "trippy", "mind-bending"],
        "color": "#7c3aed"
    },
    "💥 action": {
        "keywords": ["action", "adventure", "fight", "chase", "explosion", "battle", "war", "superhero", "martial arts"],
        "color": "#dc2626"
    },
    "❤️ romance": {
        "keywords": ["romance", "love", "relationship", "romantic", "dating", "marriage", "passion", "couple"],
        "color": "#ec4899"
    },
    "🌑 dark": {
        "keywords": ["dark", "disturbing", "psychological", "horror", "tragic", "depressing", "violent", "gritty"],
        "color": "#1f2937"
    },
    "☀️ lighthearted": {
        "keywords": ["light", "fun", "cheerful", "amusing", "entertaining", "playful", "carefree", "joyful"],
        "color": "#eab308"
    },
    "🧠 mind-bending": {
        "keywords": ["complex", "philosophical", "cerebral", "thought-provoking", "intellectual", "puzzle", "twist"],
        "color": "#2563eb"
    },
    "😊 feel-good": {
        "keywords": ["inspiring", "motivational", "positive", "hopeful", "optimistic", "touching", "emotional"],
        "color": "#16a34a"
    },
    "⚡ intense": {
        "keywords": ["intense", "gripping", "edge-of-seat", "nail-biting", "adrenaline", "fast-paced", "high-stakes"],
        "color": "#f59e0b"
    }
}

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scene Stealer - Tonight's Watchlist</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f8fafc;
            min-height: 100vh;
            transition: all 0.3s ease;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            position: sticky;
            top: 0;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(10px);
            z-index: 100;
            padding: 20px 0;
            border-radius: 0 0 20px 20px;
        }
        
        .title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(45deg, #f59e0b, #ec4899, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #94a3b8;
            font-size: 1.2rem;
            margin-bottom: 30px;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #8b5cf6, #ec4899);
            color: white;
        }
        
        .btn-secondary {
            background: rgba(148, 163, 184, 0.1);
            color: #94a3b8;
            border: 1px solid rgba(148, 163, 184, 0.2);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        }
        
        .search-container {
            max-width: 400px;
            margin: 0 auto 30px;
            position: relative;
        }
        
        .search-input {
            width: 100%;
            padding: 15px 20px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 25px;
            background: rgba(30, 41, 59, 0.5);
            color: #f8fafc;
            font-size: 16px;
            outline: none;
            transition: all 0.3s ease;
        }
        
        .search-input:focus {
            border-color: #8b5cf6;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
        }
        
        .vibe-filters {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 40px;
        }
        
        .vibe-tag {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
            background: rgba(30, 41, 59, 0.5);
        }
        
        .vibe-tag:hover, .vibe-tag.active {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .movie-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .movie-card {
            background: rgba(30, 41, 59, 0.6);
            border-radius: 15px;
            overflow: hidden;
            transition: all 0.3s ease;
            border: 1px solid rgba(148, 163, 184, 0.1);
            cursor: pointer;
        }
        
        .movie-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            border-color: rgba(139, 92, 246, 0.3);
        }
        
        .movie-poster {
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: linear-gradient(45deg, #1e293b, #334155);
        }
        
        .movie-info {
            padding: 20px;
        }
        
        .movie-title {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 8px;
            color: #f8fafc;
        }
        
        .movie-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            color: #94a3b8;
            font-size: 14px;
        }
        
        .movie-rating {
            display: flex;
            align-items: center;
            gap: 4px;
            font-weight: 600;
        }
        
        .movie-vibes {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            margin-bottom: 12px;
        }
        
        .movie-vibe {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .movie-description {
            color: #cbd5e1;
            font-size: 14px;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .loading {
            text-align: center;
            padding: 60px 20px;
            color: #94a3b8;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(139, 92, 246, 0.1);
            border-left: 4px solid #8b5cf6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            text-align: center;
            padding: 40px 20px;
            color: #ef4444;
            background: rgba(239, 68, 68, 0.1);
            border-radius: 15px;
            margin: 20px 0;
        }
        
        @media (max-width: 768px) {
            .title {
                font-size: 2rem;
            }
            
            .controls {
                flex-direction: column;
                align-items: center;
            }
            
            .movie-grid {
                grid-template-columns: 1fr;
            }
            
            .vibe-filters {
                gap: 8px;
            }
            
            .vibe-tag {
                font-size: 12px;
                padding: 6px 12px;
            }
        }
        
        .hidden {
            display: none !important;
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🎬 Scene Stealer</h1>
            <p class="subtitle">Tonight's Curated Watchlist</p>
            
            <div class="controls">
                <button class="btn btn-primary" onclick="generateNewList()">
                    🎬 Generate New List
                </button>
                <button class="btn btn-secondary" onclick="surpriseMe()">
                    🎲 Surprise Me
                </button>
                <button class="btn btn-secondary" onclick="saveList()">
                    💾 Save List
                </button>
            </div>
            
            <div class="search-container">
                <input type="text" class="search-input" placeholder="🔍 Search movies..." 
                       oninput="searchMovies(this.value)">
            </div>
            
            <div class="vibe-filters" id="vibeFilters">
                <!-- Vibe filters will be populated by JavaScript -->
            </div>
        </div>
        
        <div id="movieGrid" class="movie-grid">
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading your personalized watchlist...</p>
            </div>
        </div>
    </div>

    <script>
        let allMovies = [];
        let filteredMovies = [];
        let activeVibes = new Set();
        
        // Initialize the app
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Scene Stealer initializing...');
            setupVibeFilters();
            loadMovies();
        });
        
        async function loadMovies() {
            try {
                console.log('Loading movies...');
                const response = await fetch('/api/movies');
                const data = await response.json();
                
                console.log('API response:', data);
                
                if (data.error) {
                    showError(data.error);
                    return;
                }
                
                if (!data.movies || data.movies.length === 0) {
                    showError('No movies found. The API might be having issues.');
                    return;
                }
                
                allMovies = data.movies;
                filteredMovies = [...allMovies];
                console.log(`Loaded ${allMovies.length} movies`);
                renderMovies(filteredMovies);
            } catch (error) {
                console.error('Load movies error:', error);
                showError('Failed to load movies. Please check your connection.');
            }
        }
        
        function setupVibeFilters() {
            const vibes = JSON.parse('{{ vibes_json | safe }}');
            const filtersContainer = document.getElementById('vibeFilters');
            
            Object.entries(vibes).forEach(([vibe, data]) => {
                const tag = document.createElement('div');
                tag.className = 'vibe-tag';
                tag.textContent = vibe;
                tag.style.backgroundColor = data.color + '20';
                tag.style.borderColor = data.color;
                tag.onclick = () => toggleVibeFilter(vibe, tag);
                filtersContainer.appendChild(tag);
            });
        }
        
        function toggleVibeFilter(vibe, element) {
            if (activeVibes.has(vibe)) {
                activeVibes.delete(vibe);
                element.classList.remove('active');
            } else {
                activeVibes.add(vibe);
                element.classList.add('active');
            }
            
            filterMovies();
        }
        
        function filterMovies() {
            if (activeVibes.size === 0) {
                filteredMovies = [...allMovies];
            } else {
                filteredMovies = allMovies.filter(movie => 
                    movie.vibes.some(vibe => activeVibes.has(vibe))
                );
            }
            
            renderMovies(filteredMovies);
        }
        
        function searchMovies(query) {
            if (!query.trim()) {
                filterMovies();
                return;
            }
            
            const searchResults = filteredMovies.filter(movie =>
                movie.title.toLowerCase().includes(query.toLowerCase()) ||
                movie.overview.toLowerCase().includes(query.toLowerCase())
            );
            
            renderMovies(searchResults);
        }
        
        function renderMovies(movies) {
            const grid = document.getElementById('movieGrid');
            
            if (movies.length === 0) {
                grid.innerHTML = '<div class="error">No movies found matching your criteria.</div>';
                return;
            }
            
            grid.innerHTML = movies.map(movie => `
                <div class="movie-card fade-in" onclick="showMovieDetails('${movie.id}')">
                    <img class="movie-poster" 
                         src="${movie.poster_url || '/static/placeholder.jpg'}" 
                         alt="${movie.title}"
                         onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMzM0MTU1Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk0YTNiOCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk5vIEltYWdlPC90ZXh0Pjwvc3ZnPg=='">
                    <div class="movie-info">
                        <h3 class="movie-title">${movie.title}</h3>
                        <div class="movie-meta">
                            <span>${movie.year}</span>
                            <div class="movie-rating">
                                <span>⭐</span>
                                <span>${movie.rating}</span>
                            </div>
                        </div>
                        <div class="movie-vibes">
                            ${movie.vibes.map(vibe => {
                                const vibes = JSON.parse('{{ vibes_json | safe }}');
                                const vibeData = vibes[vibe] || {color: '#94a3b8'};
                                return `<span class="movie-vibe" style="background-color: ${vibeData.color}20; color: ${vibeData.color};">${vibe}</span>`;
                            }).join('')}
                        </div>
                        <p class="movie-description">${movie.overview}</p>
                    </div>
                </div>
            `).join('');
        }
        
        async function generateNewList() {
            document.getElementById('movieGrid').innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Generating fresh recommendations...</p>
                </div>
            `;
            
            try {
                const response = await fetch('/api/generate');
                const data = await response.json();
                
                if (data.error) {
                    showError(data.error);
                    return;
                }
                
                allMovies = data.movies;
                filteredMovies = [...allMovies];
                activeVibes.clear();
                
                // Reset vibe filters
                document.querySelectorAll('.vibe-tag').forEach(tag => {
                    tag.classList.remove('active');
                });
                
                renderMovies(filteredMovies);
            } catch (error) {
                showError('Failed to generate new list.');
            }
        }
        
        async function surpriseMe() {
            try {
                const response = await fetch('/api/surprise');
                const data = await response.json();
                
                if (data.error) {
                    showError(data.error);
                    return;
                }
                
                renderMovies([data.movie]);
            } catch (error) {
                showError('Failed to get surprise recommendation.');
            }
        }
        
        function saveList() {
            const movies = filteredMovies.length > 0 ? filteredMovies : allMovies;
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
            const filename = `scene-stealer-watchlist-${timestamp}.json`;
            
            const data = {
                generated: new Date().toISOString(),
                movies: movies.map(movie => ({
                    title: movie.title,
                    year: movie.year,
                    rating: movie.rating,
                    vibes: movie.vibes,
                    overview: movie.overview,
                    poster_url: movie.poster_url
                }))
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        }
        
        function showError(message) {
            document.getElementById('movieGrid').innerHTML = `
                <div class="error">
                    <h3>Oops! Something went wrong</h3>
                    <p>${message}</p>
                    <button class="btn btn-primary" onclick="loadMovies()" style="margin-top: 15px;">
                        Try Again
                    </button>
                </div>
            `;
        }
        
        function showMovieDetails(movieId) {
            // Future enhancement: show modal with full details
            console.log('Show details for movie:', movieId);
        }
    </script>
</body>
</html>
"""

def main():
    """Main function containing all Scene Stealer web logic"""
    
    app = Flask(__name__)
    
    def get_api_key():
        """Get TMDB API key - now pre-configured"""
        return TMDB_API_KEY
    

    
    def make_tmdb_request(endpoint: str, params: Dict = None, retry_count: int = 0) -> Optional[Dict]:
        """Make TMDB API request with improved error handling and simple retry"""
        max_retries = 2
        
        try:
            url = f"{TMDB_BASE_URL}/{endpoint}"
            
            # Use Bearer token authentication (preferred)
            headers = {
                "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}",
                "Content-Type": "application/json",
                "User-Agent": "Scene-Stealer/1.0"
            }
            
            # Add API key as fallback
            if not params:
                params = {}
            params["api_key"] = TMDB_API_KEY
            
            # Make request with reasonable timeout
            response = requests.get(
                url, 
                headers=headers, 
                params=params, 
                timeout=10,  # Simple timeout
                verify=True
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectTimeout:
            if retry_count < max_retries:
                print(f"⚠️  Connection timeout for {endpoint}, retrying... ({retry_count + 1}/{max_retries})")
                time.sleep(2)
                return make_tmdb_request(endpoint, params, retry_count + 1)
            print(f"❌ Connection timeout for {endpoint} after {max_retries} retries")
            return None
            
        except requests.exceptions.ReadTimeout:
            if retry_count < max_retries:
                print(f"⚠️  Read timeout for {endpoint}, retrying... ({retry_count + 1}/{max_retries})")
                time.sleep(2)
                return make_tmdb_request(endpoint, params, retry_count + 1)
            print(f"❌ Read timeout for {endpoint} after {max_retries} retries")
            return None
            
        except requests.exceptions.ConnectionError as e:
            if retry_count < max_retries:
                print(f"⚠️  Connection error for {endpoint}, retrying... ({retry_count + 1}/{max_retries})")
                time.sleep(3)
                return make_tmdb_request(endpoint, params, retry_count + 1)
            print(f"❌ Connection error for {endpoint}: {e}")
            return None
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP error for {endpoint}: {e}")
            return None
            
        except Exception as e:
            print(f"❌ Unexpected error for {endpoint}: {e}")
            return None
    
    def fetch_trending_movies() -> List[Dict]:
        """Fetch and cache trending movies"""
        global movie_cache, cache_timestamp
        
        # Check cache
        if cache_timestamp and datetime.now() - cache_timestamp < timedelta(seconds=CACHE_DURATION):
            if 'trending' in movie_cache:
                print(f"Using cached data ({len(movie_cache['trending'])} movies)")
                return movie_cache['trending']
        
        print("Fetching fresh movie data...")
        
        # Try simpler endpoint first if others fail
        endpoints = [
            "movie/popular",  # Most reliable endpoint
            "trending/movie/day",
            "movie/top_rated"
        ]
        
        all_movies = []
        seen_ids = set()
        successful_requests = 0
        
        for endpoint in endpoints:
            print(f"   Trying {endpoint}...")
            data = make_tmdb_request(endpoint)
            if data and 'results' in data:
                successful_requests += 1
                print(f"   ✅ Success! Got {len(data['results'])} movies")
                
                for movie in data['results'][:6]:  # Reduced further to avoid timeouts
                    if (movie.get('id') and 
                        movie['id'] not in seen_ids and 
                        movie.get('adult') == False and
                        movie.get('overview')):  # Pre-check for overview
                        
                        movie_details = get_movie_details(movie['id'])
                        if movie_details:
                            all_movies.append(movie_details)
                            seen_ids.add(movie['id'])
                            
                        # Stop early if we have enough movies
                        if len(all_movies) >= 20:
                            break
                            
            else:
                print(f"   ❌ Failed to fetch from {endpoint}")
            
            # If we have some movies and at least one successful request, that's enough
            if len(all_movies) >= 10 and successful_requests > 0:
                break
        
        # Cache results even if we don't have many
        if all_movies:
            movie_cache['trending'] = all_movies
            cache_timestamp = datetime.now()
            print(f"✅ Successfully cached {len(all_movies)} movies")
        else:
            print("❌ No movies fetched - API may be unavailable")
        
        return movie_cache.get('trending', [])
    
    def get_movie_details(movie_id: int) -> Optional[Dict]:
        """Get detailed movie information"""
        if movie_id in movie_cache:
            return movie_cache[movie_id]
        
        data = make_tmdb_request(f"movie/{movie_id}")
        if not data or 'id' not in data:
            return None
        
        # Ensure we have required fields
        if not data.get('title'):
            return None
            
        movie = {
            'id': str(data['id']),  # Convert to string for JavaScript compatibility
            'title': data['title'],
            'year': data['release_date'][:4] if data.get('release_date') else 'N/A',
            'rating': round(float(data.get('vote_average', 0)), 1),
            'genres': [g['name'] for g in data.get('genres', [])],
            'overview': data.get('overview', 'No description available.'),
            'poster_url': f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get('poster_path') else None
        }
        
        movie['vibes'] = classify_vibes(movie)
        movie_cache[movie_id] = movie
        return movie
    
    def classify_vibes(movie: Dict) -> List[str]:
        """Classify movie vibes with confidence scoring"""
        text = f"{' '.join(movie['genres'])} {movie['overview']}".lower()
        vibe_scores = {}
        
        for vibe, data in VIBE_KEYWORDS.items():
            score = sum(1 for keyword in data['keywords'] if keyword in text)
            if score > 0:
                vibe_scores[vibe] = score
        
        # Sort by score and take top vibes
        sorted_vibes = sorted(vibe_scores.items(), key=lambda x: x[1], reverse=True)
        vibes = [vibe for vibe, score in sorted_vibes[:3]]  # Max 3 vibes
        
        # Ensure at least one vibe
        if not vibes:
            genres = [g.lower() for g in movie['genres']]
            if any(g in genres for g in ['horror', 'thriller']):
                vibes.append("🔪 thriller")
            elif any(g in genres for g in ['comedy', 'family']):
                vibes.append("😊 feel-good")
            elif any(g in genres for g in ['action', 'adventure']):
                vibes.append("💥 action")
            elif any(g in genres for g in ['romance']):
                vibes.append("❤️ romance")
            else:
                vibes.append("☀️ lighthearted")
        
        return vibes
    
    def generate_curated_list(movies: List[Dict], count: int = 10) -> List[Dict]:
        """Generate curated watchlist with diversity"""
        if not movies:
            return []
        
        # Sort by rating
        sorted_movies = sorted(movies, key=lambda x: x['rating'], reverse=True)
        
        # Select diverse movies
        selected = []
        used_vibes = set()
        
        # First pass: prioritize vibe diversity
        for movie in sorted_movies:
            if len(selected) >= count:
                break
            
            movie_vibes = set(movie['vibes'])
            if not used_vibes or not movie_vibes.issubset(used_vibes):
                selected.append(movie)
                used_vibes.update(movie_vibes)
        
        # Second pass: fill with highest rated
        for movie in sorted_movies:
            if len(selected) >= count:
                break
            if movie not in selected:
                selected.append(movie)
        
        return selected[:count]
    
    @app.route('/')
    def index():
        """Main page"""
        import json
        vibes_json = json.dumps(VIBE_KEYWORDS)
        return render_template_string(HTML_TEMPLATE, vibes=VIBE_KEYWORDS, vibes_json=vibes_json)
    
    @app.route('/api/movies')
    def api_movies():
        """Get curated movie list"""
        try:
            movies = fetch_trending_movies()
            if not movies:
                print("⚠️  Using fallback movie data due to API issues")
                movies = FALLBACK_MOVIES
            
            curated = generate_curated_list(movies)
            return jsonify({'movies': curated})
        except Exception as e:
            print(f"❌ API error, using fallback: {e}")
            return jsonify({'movies': FALLBACK_MOVIES})
    
    @app.route('/api/generate')
    def api_generate():
        """Generate new watchlist"""
        try:
            # Clear cache to force refresh
            global cache_timestamp
            cache_timestamp = None
            
            movies = fetch_trending_movies()
            if not movies:
                return jsonify({'error': 'Failed to fetch movies'})
            
            # Shuffle and select different movies
            random.shuffle(movies)
            curated = generate_curated_list(movies)
            return jsonify({'movies': curated})
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'})
    
    @app.route('/api/surprise')
    def api_surprise():
        """Get surprise movie recommendation"""
        try:
            movies = fetch_trending_movies()
            if not movies:
                return jsonify({'error': 'Failed to fetch movies'})
            
            # Pick random vibe and find matching movie
            target_vibe = random.choice(list(VIBE_KEYWORDS.keys()))
            matching_movies = [m for m in movies if target_vibe in m['vibes']]
            
            if not matching_movies:
                movie = random.choice(movies)
            else:
                movie = random.choice(matching_movies)
            
            return jsonify({'movie': movie})
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'})
    
    @app.route('/api/test')
    def api_test():
        """Test API connectivity"""
        try:
            data = make_tmdb_request("movie/popular", {"page": 1})
            if data and 'results' in data:
                return jsonify({
                    'status': 'success', 
                    'message': f'API working! Found {len(data["results"])} movies',
                    'sample_movie': data['results'][0]['title'] if data['results'] else 'None'
                })
            else:
                return jsonify({'status': 'error', 'message': 'API request failed'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'API test failed: {str(e)}'})
    
    # API key is pre-configured
    api_key = get_api_key()
    
    print("🎬 Scene Stealer Web App")
    print("=" * 40)
    print("✅ TMDB API configured")
    print("🔄 Testing API connection...")
    
    # Test API connection with better error handling
    print("   Attempting connection to TMDB API...")
    test_data = make_tmdb_request("movie/popular", {"page": 1})
    if test_data and 'results' in test_data:
        print(f"✅ API working! Found {len(test_data['results'])} popular movies")
    else:
        print("⚠️  API test failed, but starting server anyway...")
        print("   The web app will handle API errors gracefully")
        print("   Check your internet connection if issues persist")
    
    print("🌐 Starting web server...")
    print("🌐 Open http://localhost:5000 in your browser")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    # Get port from environment variable (for Render deployment) or default to 5000
    import os
    port = int(os.environ.get('PORT', 5000))
    
    try:
        app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Scene Stealer stopped. Thanks for using!")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()