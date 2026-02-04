import json
import os
import re

def load_genre_start_years(filepath):
    """
    Parses the genre_start_years.txt file.
    Returns a dict: { 'genre_name': start_year_int }
    """
    genre_years = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Expecting format: genre -> year
            if '->' in line:
                parts = line.split('->')
                genre = parts[0].strip().lower()
                try:
                    year = int(parts[1].strip())
                    genre_years[genre] = year
                except ValueError:
                    print(f"Warning: Could not parse year in line: {line}")
    return genre_years

def load_decade_genres(json_path):
    """
    Loads a decade JSON file and returns a set of all genre keys found within it.
    Structure is assumed: { "Group": { "genre": { data... }, ... }, ... }
    """
    genres = set()
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for group, contents in data.items():
            if isinstance(contents, dict):
                for genre_key in contents.keys():
                    genres.add(genre_key.lower())
    except Exception as e:
        print(f"Error reading {json_path}: {e}")
    return genres

def main():
    base_dir = '/home/nbm/Code/genregraphy'
    start_years_path = os.path.join(base_dir, 'scripts/texts/genre_start_years.txt')
    decades_dir = os.path.join(base_dir, 'src/api/decades')
    output_path = os.path.join(base_dir, 'missing_genres_report.txt')

    # 1. Load start years
    if not os.path.exists(start_years_path):
        print(f"Error: {start_years_path} not found.")
        return

    genre_start_years = load_genre_start_years(start_years_path)
    print(f"Loaded {len(genre_start_years)} genres with start years.")

    # 2. Iterate specific decades (files we know match the pattern)
    # Assuming decades from 1950 to 2020 based on previous context
    decades = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]
    
    missing_report = {}

    for decade in decades:
        json_filename = f"{decade}.json"
        json_path = os.path.join(decades_dir, json_filename)
        
        if not os.path.exists(json_path):
            print(f"Warning: {json_path} does not exist. Skipping.")
            continue
            
        # Get genres currently in the JSON
        existing_genres = load_decade_genres(json_path)
        
        missing_in_decade = []
        
        # Check logic: "ako zanr pocinje bilo gde u dekadi treba da bude u listi"
        # If genre starts in [decade, decade+9], it must be present.
        decade_start = decade
        decade_end = decade + 9
        
        for genre, start_year in genre_start_years.items():
            if decade_start <= start_year <= decade_end:
                if genre not in existing_genres:
                    # Double check exact string matching or simple normalization
                    # We lowercased everything, so it should be fine.
                    missing_in_decade.append(f"{genre} (starts {start_year})")
        
        if missing_in_decade:
            missing_report[decade] = missing_in_decade

    # 3. Write Output
    with open(output_path, 'w', encoding='utf-8') as out:
        if missing_report:
            out.write("Missing Types Report\n")
            out.write("===================\n\n")
            for decade in sorted(missing_report.keys()):
                out.write(f"Decade {decade}s:\n")
                out.write("----------------\n")
                for item in sorted(missing_report[decade]):
                    out.write(f"- {item}\n")
                out.write("\n")
            print(f"Report generated at {output_path}")
        else:
            out.write("No missing genres found based on start years.\n")
            print("No missing genres found.")

if __name__ == "__main__":
    main()
