#!/usr/bin/env python3
"""
Genregraphy Data Fetcher
Fetches genre/year data from MusicBrainz API
"""

import musicbrainzngs
import json
import time
from tqdm import tqdm
from pathlib import Path

# Configuration
musicbrainzngs.set_useragent("Genregraphy", "0.1", "notbigmuzzy@gmail.com")

YEAR_START = 1994
YEAR_END = 1994


def load_genres():
    """Load genres from genres.txt file"""
    genres_file = Path(__file__).parent / 'genres.txt'
    genres = []
    
    with open(genres_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if line and not line.startswith('#'):
                genres.append(line.lower())
    
    return genres


def load_genre_groups():
    """Load genre to group mapping from genre_groups.txt"""
    mapping_file = Path(__file__).parent / 'genre_groups.txt'
    genre_to_group = {}
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                if ' -> ' in line:
                    genre, group = line.split(' -> ')
                    genre_to_group[genre.strip().lower()] = group.strip()
    
    return genre_to_group


def load_genre_synonyms():
    """Load genre synonyms mapping"""
    synonyms_file = Path(__file__).parent / 'genre_synonyms.txt'
    synonyms = {}
    
    if not synonyms_file.exists():
        return {}
    
    with open(synonyms_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                if ' -> ' in line:
                    synonym, primary = line.split(' -> ')
                    synonyms[synonym.strip().lower()] = primary.strip().lower()
    
    return synonyms


GENRES = load_genres()
GENRE_GROUPS = load_genre_groups()
GENRE_SYNONYMS = load_genre_synonyms()


def fetch_count(genre, year, retries=3):
    """Fetch album count for a specific genre and year with retry logic"""
    for attempt in range(retries):
        try:
            query = f'tag:{genre} AND date:{year} AND (type:album OR type:compilation OR type:live OR type:single)'
            result = musicbrainzngs.search_release_groups(query=query, limit=1)
            return result['release-group-count']
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retry
                continue
            else:
                print(f"Error fetching {genre}/{year} after {retries} attempts: {e}")
                return 0


def fetch_examples(genre, year, limit=20, retries=3):
    """Fetch example albums for a specific genre and year with retry logic"""
    for attempt in range(retries):
        try:
            query = f'tag:{genre} AND date:{year} AND (type:album OR type:compilation OR type:live OR type:single)'
            result = musicbrainzngs.search_release_groups(query=query, limit=limit)
            
            examples = []
            for rg in result.get('release-group-list', []):
                examples.append({
                    'title': rg.get('title', 'Unknown'),
                    'artist': rg.get('artist-credit-phrase', 'Unknown Artist'),
                    'year': year,
                    'genre': genre
                })
            
            return examples
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            else:
                print(f"Error fetching examples for {genre}/{year} after {retries} attempts: {e}")
                return []


def build_summary_data():
    """Phase A: Build summary map data (counts only) grouped by genre groups"""
    print("Phase A: Fetching summary counts...")
    
    summary = {}
    total_requests = len(GENRES) * (YEAR_END - YEAR_START + 1)
    
    with tqdm(total=total_requests, desc="Fetching counts") as pbar:
        for year in range(YEAR_START, YEAR_END + 1):
            summary[str(year)] = {}
            
            for genre in GENRES:
                count = fetch_count(genre, year)
                
                # Check if this genre is a synonym - use primary genre instead
                actual_genre = GENRE_SYNONYMS.get(genre, genre)
                
                # Get the group for this genre
                group = GENRE_GROUPS.get(actual_genre, "Other")
                
                # Initialize group if not exists
                if group not in summary[str(year)]:
                    summary[str(year)][group] = {}
                
                # Add or merge genre count to its group
                if actual_genre not in summary[str(year)][group]:
                    summary[str(year)][group][actual_genre] = 0
                
                summary[str(year)][group][actual_genre] += count
                
                pbar.update(1)
                time.sleep(1.1)  # Rate limiting: 1 request per second
    
    # Save to file
    output_path = Path(__file__).parent.parent / 'src/api/genres.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Summary data saved to {output_path}")
    return summary


def build_detailed_data(top_n=10):
    """Phase B: Build detailed data with examples for top entries"""
    print("\nPhase B: Fetching detailed examples...")
    
    detailed = []
    
    # Fetch examples for all genres and years (same as summary)
    for year in tqdm(range(YEAR_START, YEAR_END + 1), desc="Fetching examples"):
        for genre in GENRES:
            examples = fetch_examples(genre, year, limit=10)
            if examples:
                detailed.extend(examples)
            time.sleep(1.1)
    
    # Save detailed data
    output_path = Path(__file__).parent.parent / 'src/api/detailed.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(detailed, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Detailed data saved to {output_path}")
    return detailed


def main():
    """Main execution"""
    print("Genregraphy Data Fetcher")
    print("=" * 50)
    print(f"Genres: {len(GENRES)}")
    print(f"Years: {YEAR_START}-{YEAR_END}")
    print(f"Total requests: ~{len(GENRES) * (YEAR_END - YEAR_START + 1)}")
    print(f"Estimated time: ~{(len(GENRES) * (YEAR_END - YEAR_START + 1)) / 60:.1f} minutes")
    print("=" * 50)
    
    choice = input("\n1) Summary only (fast)\n2) Summary + Details (slow)\nChoice: ").strip()
    
    if choice == "1":
        build_summary_data()
    elif choice == "2":
        build_summary_data()
        build_detailed_data()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
