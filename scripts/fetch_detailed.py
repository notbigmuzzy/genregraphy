#!/usr/bin/env python3
"""
Genregraphy Detailed Data Fetcher
Fetches detailed genre/year data from MusicBrainz API
"""

import musicbrainzngs
import json
import time
from tqdm import tqdm
from pathlib import Path

# Configuration
musicbrainzngs.set_useragent("Genregraphy", "0.1", "notbigmuzzy@gmail.com")

YEAR_START = 1950
YEAR_END = 1950

def load_genres():
    """Load genres from texts/genres.txt file"""
    genres_file = Path(__file__).parent / 'texts/genres.txt'
    genres = []
    
    with open(genres_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
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

def load_genre_start_years():
    """Load genre start years mapping"""
    start_years_file = Path(__file__).parent / 'texts/genre_start_years.txt'
    start_years = {}
    
    if not start_years_file.exists():
        return {}
    
    with open(start_years_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if ' -> ' in line:
                    genre, year = line.split(' -> ')
                    start_years[genre.strip().lower()] = int(year.strip())
    
    return start_years

GENRES = load_genres()
GENRE_GROUPS = load_genre_groups()
GENRE_SYNONYMS = load_genre_synonyms()
GENRE_START_YEARS = load_genre_start_years()

def fetch_albums_and_artists(genre, year, limit=5, retries=3):
    """Fetch albums for genre/year and extract artists from those albums"""
    albums = []
    artists_dict = {}  # Track unique artists
    seen_album_names = set()  # Track album names for deduplication
    seen_artist_names = set()  # Track artist names for deduplication
    offset = 0
    page_size = 100  # Try larger page size for efficiency
    max_pages = 5  # Maximum 5 pages (500 results)
    
    for page in range(max_pages):
        for attempt in range(retries):
            try:
                # Search with offset for pagination
                # Use indexed search method like browser
                query = f'tag:"rock" AND date:{year}'
                result = musicbrainzngs.search_release_groups(
                    query=query, 
                    limit=page_size, 
                    offset=offset,
                    strict=True
                )
                
                release_groups = result.get('release-group-list', [])
                
                if not release_groups:
                    break
                
                for rg in release_groups:
                    # Get basic info
                    album_name = rg.get('title', 'Unknown')
                    album_mbid = rg.get('id', '')
                    album_type = rg.get('type', '')
                    first_release_date = rg.get('first-release-date', '')
                    
                    # Skip if album name equals year
                    if album_name == str(year):
                        continue
                    
                    # Skip if album name contains numbers
                    if any(char.isdigit() for char in album_name):
                        continue
                    
                    # Skip if album name contains "date" (MusicBrainz query bug)
                    if 'date' in album_name.lower():
                        continue
                    
                    # Check if release year matches
                    if not first_release_date:
                        continue
                        
                    if not first_release_date.startswith(str(year)):
                        continue
                    
                    # Get artist info
                    artist_credit = rg.get('artist-credit', [])
                    if not artist_credit:
                        continue
                    
                    artist_data = artist_credit[0].get('artist', {})
                    artist_name = artist_data.get('name', 'Unknown')
                    artist_mbid = artist_data.get('id', '')
                    
                    # Skip Various Artists compilations
                    if artist_name == 'Various Artists':
                        continue
                    
                    # Skip if we already have an album with this name
                    if album_name in seen_album_names:
                        continue
                    
                    # Skip if we already have an album from this artist
                    if artist_name in seen_artist_names:
                        continue
                    
                    # Mark as seen
                    seen_album_names.add(album_name)
                    seen_artist_names.add(artist_name)
                    
                    # Add album
                    albums.append({
                        'name': album_name,
                        'mbid': album_mbid,
                        'artist': artist_name,
                        'year': first_release_date
                    })
                    
                    # Track artist
                    if artist_mbid and artist_mbid not in artists_dict:
                        artists_dict[artist_mbid] = {
                            'name': artist_name,
                            'mbid': artist_mbid,
                            'album_count': 0
                        }
                    
                    if artist_mbid:
                        artists_dict[artist_mbid]['album_count'] += 1
                    
                    # Stop if we have enough albums
                    if len(albums) >= limit:
                        break
                
                # Rate limiting between pages
                time.sleep(1.1)
                
                # Stop if we have enough albums
                if len(albums) >= limit:
                    break
                
                # Move to next page
                offset += page_size
                break  # Break retry loop if successful
                
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                else:
                    break
        
        # Stop pagination if we have enough
        if len(albums) >= limit:
            break
    
    # Get top 5 artists (by album count in this result set)
    artists = sorted(
        artists_dict.values(),
        key=lambda x: x['album_count'],
        reverse=True
    )[:limit]
    
    print(f"  Found {len(albums)} albums and {len(artists)} artists for {genre}/{year}")
    return albums, artists

def fetch_sample_tracks(albums, retries=3):
    """Fetch first track from each album"""
    tracks = []
    
    for album in albums:
        album_mbid = album.get('mbid')
        album_artist = album.get('artist')
        
        if not album_mbid:
            continue
        
        for attempt in range(retries):
            try:
                # Get release group to find releases
                result = musicbrainzngs.get_release_group_by_id(
                    album_mbid,
                    includes=['releases']
                )
                
                releases = result.get('release-group', {}).get('release-list', [])
                if not releases:
                    break
                
                release_id = releases[0]['id']
                
                # Get release with recordings
                release_data = musicbrainzngs.get_release_by_id(
                    release_id,
                    includes=['recordings']
                )
                
                media_list = release_data.get('release', {}).get('medium-list', [])
                if not media_list:
                    break
                
                track_list = media_list[0].get('track-list', [])
                if not track_list:
                    break
                
                # Get first track
                track = track_list[0]
                recording = track.get('recording', {})
                
                tracks.append({
                    'name': recording.get('title', 'Unknown'),
                    'artist': album_artist,
                    'album': album.get('name')
                })
                
                time.sleep(1.1)  # Rate limiting
                break
                
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                else:
                    break
    
    return tracks

def build_detailed_data():
    """Fetch detailed data with albums, artists, and sample tracks"""
    # Create detailed directory
    detailed_dir = Path(__file__).parent.parent / 'src/api/detailed'
    detailed_dir.mkdir(parents=True, exist_ok=True)
    
    total_requests = len(GENRES) * (YEAR_END - YEAR_START + 1)
    
    with tqdm(total=total_requests, desc="Fetching detailed data") as pbar:
        for year in range(YEAR_START, YEAR_END + 1):
            year_file = detailed_dir / f'{year}.json'
            
            # Skip if year file already exists
            if year_file.exists():
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
                        'sample_tracks': []
                    }
                
                # Check if year is before genre start year
                start_year = GENRE_START_YEARS.get(actual_genre, 1950)  # Default to 1950
                if year < start_year:
                    pbar.update(1)
                    continue
                
                # Fetch albums and extract artists
                albums, artists = fetch_albums_and_artists(genre, year, limit=5)
                time.sleep(1.1)
                
                if albums:
                    year_data[group][actual_genre]['top_albums'] = albums
                
                if artists:
                    year_data[group][actual_genre]['top_artists'] = artists
                
                # Fetch sample tracks from albums
                if albums:
                    tracks = fetch_sample_tracks(albums)
                    if tracks:
                        year_data[group][actual_genre]['sample_tracks'] = tracks
                
                pbar.update(1)
            
            # Save year file
            with open(year_file, 'w', encoding='utf-8') as f:
                json.dump(year_data, f, indent=2, ensure_ascii=False)

def main():
    """Main execution"""
    build_detailed_data()

if __name__ == "__main__":
    main()
