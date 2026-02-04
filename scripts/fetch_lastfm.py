#!/usr/bin/env python3
"""
Genregraphy Data Fetcher (Last.fm)
Fetches detailed genre/year data from Last.fm API
"""

import pylast
import musicbrainzngs
import json
import time
from tqdm import tqdm
from pathlib import Path

# Configuration - ADD YOUR API KEY HERE
API_KEY = "8b962327fc2137d86986845f9c046e02"
API_SECRET = "ee3cd3e0701109b3e43c0dedd68598e2"

# MusicBrainz setup
musicbrainzngs.set_useragent("Genregraphy", "0.1", "notbigmuzzy@gmail.com")

YEAR_START = 1970
YEAR_END = 1970

def load_genres():
    """Load genres from texts/genres.txt file"""
    genres_file = Path(__file__).parent / 'texts/genres.txt'
    genres = []
    
    with open(genres_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                genres.append(line.lower())
    
    return genres

def load_genre_groups():
    """Load genre to group mapping from texts/genre_groups.txt"""
    mapping_file = Path(__file__).parent / 'texts/genre_groups.txt'
    genre_to_group = {}
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if ' -> ' in line:
                    genre, group = line.split(' -> ')
                    genre_to_group[genre.strip().lower()] = group.strip()
    
    return genre_to_group

def load_genre_synonyms():
    """Load genre synonyms mapping"""
    synonyms_file = Path(__file__).parent / 'texts/genre_synonyms.txt'
    synonyms = {}
    
    if not synonyms_file.exists():
        return {}
    
    with open(synonyms_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if ' -> ' in line:
                    synonym, primary = line.split(' -> ')
                    synonyms[synonym.strip().lower()] = primary.strip().lower()
    
    return synonyms

GENRES = load_genres()
GENRE_GROUPS = load_genre_groups()
GENRE_SYNONYMS = load_genre_synonyms()

# Initialize Last.fm network
network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

def fetch_top_artists(genre, limit=5):
    """Fetch top artists for a genre from Last.fm"""
    try:
        tag = network.get_tag(genre)
        top_artists = tag.get_top_artists(limit=limit)
        
        artists = []
        for item in top_artists:
            artist = item.item
            weight = item.weight  # Popularity weight
            
            artists.append({
                'name': artist.get_name(),
                'playcount': int(weight) if weight else 0,
                'mbid': artist.get_mbid() or ''
            })
        
        return artists
    except Exception as e:
        print(f"Error fetching artists for {genre}: {e}")
        return []

def verify_album_year_mb(mbid, target_year):
    """Verify album year using MusicBrainz (try both release-group and release)"""
    try:
        # First try as release-group
        result = musicbrainzngs.get_release_group_by_id(mbid)
        release_group = result.get('release-group', {})
        first_release_date = release_group.get('first-release-date', '')
        
        # Check if year matches (date format: YYYY-MM-DD or YYYY)
        if first_release_date and first_release_date.startswith(str(target_year)):
            return True, first_release_date
        return False, first_release_date
    except musicbrainzngs.ResponseError as e:
        # If 404, try as release instead
        if '404' in str(e):
            try:
                result = musicbrainzngs.get_release_by_id(mbid, includes=['release-groups'])
                release = result.get('release', {})
                date = release.get('date', '')
                
                if date and date.startswith(str(target_year)):
                    return True, date
                
                # Try getting release-group date
                rg = release.get('release-group', {})
                if rg:
                    try:
                        rg_id = rg.get('id')
                        if rg_id:
                            time.sleep(1.1)
                            rg_result = musicbrainzngs.get_release_group_by_id(rg_id)
                            rg_data = rg_result.get('release-group', {})
                            first_release_date = rg_data.get('first-release-date', '')
                            if first_release_date and first_release_date.startswith(str(target_year)):
                                return True, first_release_date
                    except:
                        pass
                
                return False, date
            except Exception as e2:
                print(f"      MB Error (both attempts) for {mbid}: {e2}")
                return False, None
        else:
            print(f"      MB Error for {mbid}: {e}")
            return False, None
    except Exception as e:
        print(f"      MB Error for {mbid}: {e}")
        return False, None

def fetch_top_albums(genre, year, limit=5):
    """Fetch top albums for a genre from Last.fm, validate year with MusicBrainz"""
    try:
        tag = network.get_tag(genre)
        # Get many albums from Last.fm (sorted by popularity)
        top_albums = tag.get_top_albums(limit=200)
        
        albums = []
        checked = 0
        
        for item in top_albums:
            album = item.item
            album_name = album.get_title()
            artist_name = album.get_artist().get_name()
            mbid = album.get_mbid()
            
            checked += 1
            
            if not mbid:
                print(f"    [{checked}] {album_name} by {artist_name} - No MBID, skipping")
                continue
            
            # Validate year with MusicBrainz
            is_valid, release_date = verify_album_year_mb(mbid, year)
            
            if is_valid:
                print(f"    [{checked}] ✓ {album_name} by {artist_name} - {release_date}")
                albums.append({
                    'name': album_name,
                    'artist': artist_name,
                    'playcount': item.weight if item.weight else 0,
                    'mbid': mbid,
                    'year': release_date
                })
                
                if len(albums) >= limit:
                    break
            else:
                print(f"    [{checked}] ✗ {album_name} by {artist_name} - {release_date or 'No date'}")
            
            # Rate limiting for MusicBrainz (1 call/sec)
            time.sleep(1.1)
        
        print(f"  Found {len(albums)} albums for {genre}/{year} after checking {checked} albums")
        return albums
    except Exception as e:
        print(f"Error fetching albums for {genre}/{year}: {e}")
        return []

def fetch_sample_track(album_artist, album_name):
    """Fetch first track from an album"""
    try:
        album = network.get_album(album_artist, album_name)
        tracks = album.get_tracks()
        
        if tracks and len(tracks) > 0:
            track = tracks[0]
            return {
                'name': track.get_title(),
                'artist': album_artist
            }
        return None
    except Exception as e:
        print(f"Error fetching track for {album_name}: {e}")
        return None

def build_detailed_data():
    """Fetch detailed data with top artists, albums, and sample tracks"""
    print("\nFetching detailed data from Last.fm...")
    
    # Create detailed directory
    detailed_dir = Path(__file__).parent.parent / 'src/api/detailed'
    detailed_dir.mkdir(parents=True, exist_ok=True)
    
    total_requests = len(GENRES) * (YEAR_END - YEAR_START + 1)
    
    with tqdm(total=total_requests, desc="Fetching detailed data") as pbar:
        for year in range(YEAR_START, YEAR_END + 1):
            year_file = detailed_dir / f'{year}.json'
            
            # Skip if year file already exists
            if year_file.exists():
                print(f"  Skipping {year} (file already exists)")
                pbar.update(len(GENRES))
                continue
            
            year_data = {}
            
            for genre in GENRES:
                # Check if this genre is a synonym - use primary genre instead
                actual_genre = GENRE_SYNONYMS.get(genre, genre)
                
                # Get the group for this genre
                group = GENRE_GROUPS.get(actual_genre, "Other")
                
                # Initialize group if not exists
                if group not in year_data:
                    year_data[group] = {}
                
                # Initialize genre if not exists
                if actual_genre not in year_data[group]:
                    year_data[group][actual_genre] = {
                        'top_artists': [],
                        'top_albums': [],
                        'sample_track': None
                    }
                
                print(f"  Processing {actual_genre} for {year}...")
                
                # Fetch top artists (general for genre, not year-specific)
                artists = fetch_top_artists(genre, limit=5)
                if artists:
                    year_data[group][actual_genre]['top_artists'] = artists
                time.sleep(0.5)  # Rate limiting
                
                # Fetch top albums
                albums = fetch_top_albums(genre, year, limit=5)
                if albums:
                    year_data[group][actual_genre]['top_albums'] = albums
                time.sleep(0.5)
                
                # Fetch sample track from first album
                if albums and albums[0].get('name') and albums[0].get('artist'):
                    track = fetch_sample_track(albums[0]['artist'], albums[0]['name'])
                    if track:
                        year_data[group][actual_genre]['sample_track'] = track
                    time.sleep(0.5)
                
                pbar.update(1)
            
            # Save year file
            with open(year_file, 'w', encoding='utf-8') as f:
                json.dump(year_data, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Saved {year_file.name}")
    
    print(f"✓ All detailed year files saved to {detailed_dir}")

def main():
    """Main execution"""
    print("Genregraphy Data Fetcher (Last.fm)")
    print("=" * 50)
    print(f"Genres: {len(GENRES)}")
    print(f"Years: {YEAR_START}-{YEAR_END}")
    print(f"Total requests: ~{len(GENRES) * (YEAR_END - YEAR_START + 1) * 3}")
    print(f"Estimated time: ~{(len(GENRES) * (YEAR_END - YEAR_START + 1) * 3 * 0.5) / 60:.1f} minutes")
    print("=" * 50)
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("\n⚠️  Please add your Last.fm API key to the script!")
        print("Get one at: https://www.last.fm/api/account/create")
        return
    
    input("\nPress Enter to start fetching detailed data...")
    build_detailed_data()

if __name__ == "__main__":
    main()
