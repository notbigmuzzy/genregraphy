#!/usr/bin/env python3
"""
Fetch Classical music data from MusicBrainz
A simple script to scrape Classical genre data across all years
"""

import musicbrainzngs
import json
import time
from tqdm import tqdm
from pathlib import Path

# Configuration
musicbrainzngs.set_useragent("Genregraphy", "0.1", "notbigmuzzy@gmail.com")

YEAR_START = 1950
YEAR_END = 2025
GENRE = "classical"

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

GENRE_GROUPS = load_genre_groups()

def fetch_count(genre, year, retries=3):
    """Fetch album count for a specific genre and year with retry logic"""
    for attempt in range(retries):
        try:
            genre_escaped = genre.replace('"', '\\"')
            query = f'tag:"{genre_escaped}" AND date:{year} AND (type:album OR type:compilation OR type:live OR type:single)'
            result = musicbrainzngs.search_release_groups(query=query, limit=1)
            count = result['release-group-count']
            print(f"  {year}: {count} albums")
            return count
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            else:
                print(f"Error fetching {genre}/{year} after {retries} attempts: {e}")
                return 0

def fetch_classical_data():
    """Fetch Classical music data across all years"""
    print(f"Fetching Classical music data from {YEAR_START} to {YEAR_END}")
    print("=" * 60)
    
    years_dir = Path(__file__).parent.parent / 'src/api/years'
    years_dir.mkdir(parents=True, exist_ok=True)
    
    # Get the group for Classical genre
    group = GENRE_GROUPS.get(GENRE, "The Avant-Garde Isles")
    
    with tqdm(total=(YEAR_END - YEAR_START + 1), desc="Fetching Classical") as pbar:
        for year in range(YEAR_START, YEAR_END + 1):
            year_file = years_dir / f'{year}.json'
            
            # Load existing year data
            year_data = {}
            if year_file.exists():
                with open(year_file, 'r', encoding='utf-8') as f:
                    year_data = json.load(f)
            
            # Fetch count for Classical
            count = fetch_count(GENRE, year)
            
            # Initialize group if not exists
            if group not in year_data:
                year_data[group] = {}
            
            # Add Classical genre to the group
            year_data[group][GENRE] = count
            
            # Save updated year file
            with open(year_file, 'w', encoding='utf-8') as f:
                json.dump(year_data, f, indent=2, ensure_ascii=False)
            
            pbar.update(1)
            time.sleep(1.1)  # Rate limiting: 1 request per second
    
    print(f"\n✓ Classical data saved to {years_dir}")
    print("\nNow run merge_years.py to update the main genres.json file")

def main():
    """Main execution"""
    print("Classical Music Data Fetcher")
    print("=" * 60)
    print(f"Genre: {GENRE}")
    print(f"Years: {YEAR_START}-{YEAR_END}")
    print(f"Total requests: {YEAR_END - YEAR_START + 1}")
    print(f"Estimated time: ~{(YEAR_END - YEAR_START + 1) / 60:.1f} minutes")
    print("=" * 60)
    
    proceed = input("\nProceed? (y/n): ").strip().lower()
    
    if proceed == 'y':
        fetch_classical_data()
    else:
        print("Cancelled")

if __name__ == "__main__":
    main()
