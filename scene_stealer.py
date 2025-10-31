#!/usr/bin/env python3
"""
Scene Stealer - Tonight's Watchlist Generator
A curated movie watchlist generator with vibe classification
"""

import requests
import json
import re
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# TMDB API Configuration
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_API_KEY = "your_api_key_here"  # Replace with actual API key

# Vibe classification keywords
VIBE_KEYWORDS = {
    "🔪 thriller": ["thriller", "suspense", "murder", "mystery", "crime", "detective", "killer", "death", "investigation"],
    "🛋️ comfort": ["family", "friendship", "heartwarming", "feel-good", "comedy", "romantic comedy", "uplifting", "wholesome"],
    "👽 weird": ["surreal", "bizarre", "strange", "experimental", "cult", "absurd", "unconventional", "trippy", "mind-bending"],
    "💥 action": ["action", "adventure", "fight", "chase", "explosion", "battle", "war", "superhero", "martial arts"],
    "❤️ romance": ["romance", "love", "relationship", "romantic", "dating", "marriage", "passion", "couple"],
    "🌑 dark": ["dark", "disturbing", "psychological", "horror", "tragic", "depressing", "violent", "gritty"],
    "☀️ lighthearted": ["light", "fun", "cheerful", "amusing", "entertaining", "playful", "carefree", "joyful"]
}

def main():
    """Main function containing all Scene Stealer logic"""
    
    # Cache for movie data to avoid repeated API calls
    movie_cache = {}
    current_watchlist = []
    
    def get_api_key():
        """Get TMDB API key from user if not set"""
        if TMDB_API_KEY == "your_api_key_here":
            print("🎬 Scene Stealer - Tonight's Watchlist Generator")
            print("=" * 50)
            print("To get started, you need a free TMDB API key:")
            print("1. Visit: https://www.themoviedb.org/settings/api")
            print("2. Create account and request API key")
            print("3. Enter your API key below")
            print()
            key = input("Enter your TMDB API key: ").strip()
            return key
        return TMDB_API_KEY
    
    def make_tmdb_request(endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make request to TMDB API with error handling"""
        try:
            url = f"{TMDB_BASE_URL}/{endpoint}"
            default_params = {"api_key": api_key}
            if params:
                default_params.update(params)
            
            response = requests.get(url, params=default_params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return None
    
    def fetch_trending_movies() -> List[Dict]:
        """Fetch trending movies from TMDB"""
        print("🔄 Fetching trending movies...")
        
        # Try cache first
        cache_key = f"trending_{datetime.now().strftime('%Y-%m-%d-%H')}"
        if cache_key in movie_cache:
            return movie_cache[cache_key]
        
        data = make_tmdb_request("trending/movie/day")
        if not data or 'results' not in data:
            print("❌ Failed to fetch trending movies")
            return []
        
        movies = []
        for movie in data['results'][:20]:  # Get top 20 trending
            movie_details = get_movie_details(movie['id'])
            if movie_details:
                movies.append(movie_details)
        
        movie_cache[cache_key] = movies
        return movies
    
    def get_movie_details(movie_id: int) -> Optional[Dict]:
        """Get detailed movie information"""
        if movie_id in movie_cache:
            return movie_cache[movie_id]
        
        data = make_tmdb_request(f"movie/{movie_id}")
        if not data:
            return None
        
        movie = {
            'id': data['id'],
            'title': data['title'],
            'year': data['release_date'][:4] if data.get('release_date') else 'N/A',
            'rating': round(data.get('vote_average', 0), 1),
            'genres': [g['name'] for g in data.get('genres', [])],
            'overview': data.get('overview', ''),
            'poster_url': f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get('poster_path') else None
        }
        
        movie_cache[movie_id] = movie
        return movie
    
    def classify_vibes(movie: Dict) -> List[str]:
        """Classify movie vibes based on genres and overview"""
        text = f"{' '.join(movie['genres'])} {movie['overview']}".lower()
        vibes = []
        
        for vibe, keywords in VIBE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                vibes.append(vibe)
        
        # Ensure at least one vibe
        if not vibes:
            # Default classification based on genres
            genres = [g.lower() for g in movie['genres']]
            if any(g in genres for g in ['horror', 'thriller']):
                vibes.append("🔪 thriller")
            elif any(g in genres for g in ['comedy', 'family']):
                vibes.append("🛋️ comfort")
            elif any(g in genres for g in ['action', 'adventure']):
                vibes.append("💥 action")
            elif any(g in genres for g in ['romance']):
                vibes.append("❤️ romance")
            else:
                vibes.append("☀️ lighthearted")
        
        return vibes
    
    def generate_watchlist(movies: List[Dict], count: int = 8) -> List[Dict]:
        """Generate curated watchlist with vibe classification"""
        watchlist = []
        
        for movie in movies[:count * 2]:  # Get more than needed for variety
            vibes = classify_vibes(movie)
            movie['vibes'] = vibes
            watchlist.append(movie)
        
        # Sort by rating and variety of vibes
        watchlist.sort(key=lambda x: x['rating'], reverse=True)
        
        # Select diverse vibes
        selected = []
        used_vibes = set()
        
        for movie in watchlist:
            if len(selected) >= count:
                break
            
            # Prefer movies with new vibes
            movie_vibes = set(movie['vibes'])
            if not used_vibes or not movie_vibes.issubset(used_vibes):
                selected.append(movie)
                used_vibes.update(movie_vibes)
        
        # Fill remaining slots with highest rated
        while len(selected) < count and len(selected) < len(watchlist):
            for movie in watchlist:
                if movie not in selected:
                    selected.append(movie)
                    break
        
        return selected[:count]
    
    def display_watchlist(watchlist: List[Dict], title: str = "Tonight's Watchlist"):
        """Display formatted watchlist"""
        print(f"\n🎬 {title}")
        print("=" * 60)
        
        if not watchlist:
            print("No movies found. Try generating a new list!")
            return
        
        for i, movie in enumerate(watchlist, 1):
            vibes_str = " | ".join(movie['vibes'])
            print(f"\n{i}. {movie['title']} ({movie['year']}) ⭐ {movie['rating']}")
            print(f"   {vibes_str}")
            print(f"   Genres: {', '.join(movie['genres'])}")
            
            # Truncate overview
            overview = movie['overview']
            if len(overview) > 120:
                overview = overview[:120] + "..."
            print(f"   {overview}")
    
    def filter_by_vibe(watchlist: List[Dict], target_vibe: str) -> List[Dict]:
        """Filter watchlist by specific vibe"""
        filtered = []
        for movie in watchlist:
            if any(target_vibe.lower() in vibe.lower() for vibe in movie['vibes']):
                filtered.append(movie)
        return filtered
    
    def search_by_title(watchlist: List[Dict], query: str) -> List[Dict]:
        """Search watchlist by movie title"""
        query = query.lower()
        return [movie for movie in watchlist if query in movie['title'].lower()]
    
    def save_watchlist(watchlist: List[Dict]):
        """Save watchlist to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"watchlist_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Scene Stealer Watchlist - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write("=" * 60 + "\n\n")
                
                for i, movie in enumerate(watchlist, 1):
                    vibes_str = " | ".join(movie['vibes'])
                    f.write(f"{i}. {movie['title']} ({movie['year']}) ⭐ {movie['rating']}\n")
                    f.write(f"   {vibes_str}\n")
                    f.write(f"   Genres: {', '.join(movie['genres'])}\n")
                    f.write(f"   {movie['overview']}\n\n")
            
            print(f"✅ Watchlist saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
    
    def show_menu():
        """Display main menu"""
        print("\n" + "=" * 50)
        print("🎬 Scene Stealer Menu")
        print("=" * 50)
        print("1. Generate new watchlist")
        print("2. Filter by vibe")
        print("3. Search by title")
        print("4. Surprise me (random vibes)")
        print("5. Save current watchlist")
        print("6. Show current watchlist")
        print("7. Refresh trending movies")
        print("8. Exit")
        print("=" * 50)
    
    def show_vibe_menu():
        """Display vibe filter menu"""
        print("\nAvailable vibes:")
        vibes = list(VIBE_KEYWORDS.keys())
        for i, vibe in enumerate(vibes, 1):
            print(f"{i}. {vibe}")
        return vibes
    
    # Main execution starts here
    print("🎬 Scene Stealer - Tonight's Watchlist Generator")
    print("=" * 50)
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("❌ API key required to continue")
        return
    
    # Initial movie fetch
    movies = fetch_trending_movies()
    if not movies:
        print("❌ Could not fetch movies. Check your API key and connection.")
        return
    
    print(f"✅ Loaded {len(movies)} trending movies")
    
    # Generate initial watchlist
    current_watchlist = generate_watchlist(movies)
    display_watchlist(current_watchlist)
    
    # Main menu loop
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            # Generate new watchlist
            current_watchlist = generate_watchlist(movies)
            display_watchlist(current_watchlist)
        
        elif choice == '2':
            # Filter by vibe
            if not current_watchlist:
                print("❌ No watchlist available. Generate one first!")
                continue
            
            vibes = show_vibe_menu()
            try:
                vibe_choice = int(input("\nSelect vibe number: ")) - 1
                if 0 <= vibe_choice < len(vibes):
                    target_vibe = vibes[vibe_choice].split()[1]  # Remove emoji
                    filtered = filter_by_vibe(current_watchlist, target_vibe)
                    display_watchlist(filtered, f"Movies with '{vibes[vibe_choice]}' vibe")
                else:
                    print("❌ Invalid choice")
            except ValueError:
                print("❌ Please enter a valid number")
        
        elif choice == '3':
            # Search by title
            if not current_watchlist:
                print("❌ No watchlist available. Generate one first!")
                continue
            
            query = input("Enter movie title to search: ").strip()
            if query:
                results = search_by_title(current_watchlist, query)
                display_watchlist(results, f"Search results for '{query}'")
        
        elif choice == '4':
            # Surprise me mode
            random_vibes = random.sample(list(VIBE_KEYWORDS.keys()), 2)
            surprise_list = []
            for movie in movies:
                movie['vibes'] = classify_vibes(movie)
                if any(any(vibe.split()[1] in mv for mv in movie['vibes']) for vibe in random_vibes):
                    surprise_list.append(movie)
            
            surprise_list = surprise_list[:6]
            display_watchlist(surprise_list, f"Surprise! Random vibes: {' & '.join(random_vibes)}")
            current_watchlist = surprise_list
        
        elif choice == '5':
            # Save watchlist
            if current_watchlist:
                save_watchlist(current_watchlist)
            else:
                print("❌ No watchlist to save")
        
        elif choice == '6':
            # Show current watchlist
            if current_watchlist:
                display_watchlist(current_watchlist)
            else:
                print("❌ No current watchlist. Generate one first!")
        
        elif choice == '7':
            # Refresh movies
            movie_cache.clear()
            movies = fetch_trending_movies()
            if movies:
                print(f"✅ Refreshed with {len(movies)} new trending movies")
                current_watchlist = generate_watchlist(movies)
                display_watchlist(current_watchlist)
        
        elif choice == '8':
            # Exit
            print("🎬 Thanks for using Scene Stealer! Happy watching! 🍿")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()