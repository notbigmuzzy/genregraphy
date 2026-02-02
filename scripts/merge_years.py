#!/usr/bin/env python3
import json
import os
from pathlib import Path

years_dir = '../src/api/years'
output_file = '../src/api/genres.json'

def load_genre_start_years():
    """Load genre start years from texts/genre_start_years.txt"""
    start_years_file = Path(__file__).parent / 'texts/genre_start_years.txt'
    genre_start_years = {}
    
    with open(start_years_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                if ' -> ' in line:
                    genre, year = line.split(' -> ')
                    genre_start_years[genre.strip().lower()] = int(year.strip())
    
    return genre_start_years

# Učitaj start godine za žanrove
genre_start_years = load_genre_start_years()
print(f"Loaded {len(genre_start_years)} genre start years")

merged_data = {}

# Učitaj sve godine
for filename in sorted(os.listdir(years_dir)):
    if not filename.endswith('.json'):
        continue
    
    filepath = os.path.join(years_dir, filename)
    year = int(filename.replace('.json', ''))
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filtriraj podatke prema start godinama žanrova
    continents = []
    year_mapped_total = 0
    
    for group, genres in data.items():
        group_genres = {}
        group_total = 0
        
        for genre, count in genres.items():
            genre_lower = genre.lower()
            start_year = genre_start_years.get(genre_lower, 1950)  # Default 1950
            
            # Ako je godina pre start godine, postavi na 0
            if year < start_year:
                group_genres[genre] = 0
            else:
                group_genres[genre] = count
                group_total += count
                year_mapped_total += count
        
        # Dodaj kontinent kao objekat u niz
        continents.append({
            "name": group,
            "genres": group_genres,
            "total": group_total
        })
    
    # Struktura za godinu
    year_data = {
        "continents": continents,
        "metadata": {
            "mapped_total": year_mapped_total
        }
    }
    
    merged_data[str(year)] = year_data
    print(f"Loaded {filename} (mapped_total: {year_mapped_total})")

# Nađi peak godine za svaki žanr (po procentu od ukupne produkcije)
print("\nCalculating peak years for each genre (by percentage of total production)...")
genre_peaks = {}  # {genre: {year: year, percentage: percentage}}

for year_str, year_data in merged_data.items():
    year_int = int(year_str)
    total_year = year_data["metadata"]["mapped_total"]
    if total_year == 0:
        continue
    
    for continent in year_data["continents"]:
        for genre, count in continent["genres"].items():
            if count > 0:  # Ignoriši 0 vrednosti
                # Proveri da li je žanr već postojao u toj godini
                genre_lower = genre.lower()
                start_year = genre_start_years.get(genre_lower, 1950)
                
                # Preskači godine pre nego što je žanr počeo
                if year_int < start_year:
                    continue
                
                percentage = (count / total_year) * 100
                if genre not in genre_peaks or percentage > genre_peaks[genre]["percentage"]:
                    genre_peaks[genre] = {"year": year_str, "percentage": percentage}

# Dodaj peak_genres u svaku godinu
for year_str, year_data in merged_data.items():
    peak_genres = [genre for genre, peak_info in genre_peaks.items() if peak_info["year"] == year_str]
    year_data["metadata"]["peak_genres"] = peak_genres

# Sačuvaj spojene podatke
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, indent=2)

print(f"\nMerged {len(merged_data)} years into {output_file}")
print("Applied genre start year filters")
print(f"Calculated peak years for {len(genre_peaks)} genres")
