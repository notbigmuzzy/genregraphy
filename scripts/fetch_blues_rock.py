import musicbrainzngs
import json
import time

# Configuration
musicbrainzngs.set_useragent("Genregraphy", "0.1", "notbigmuzzy@gmail.com")

YEAR_START = 1950
YEAR_END = 2025

def fetch_blues_rock_count(year, retries=3):
    """Fetch album count for blues-rock variants"""
    query = f'(tag:"blues-rock" OR tag:"blues rock" OR tag:"blues&rock" OR tag:"blues & rock") AND date:{year} AND (type:album OR type:ep OR type:single)'
    
    for attempt in range(retries):
        try:
            result = musicbrainzngs.search_release_groups(query=query, limit=1)
            count = result['release-group-count']
            print(f"[{year}] Count: {count}")
            return count
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"Error fetching {year} after {retries} attempts: {e}")
                return 0

def main():
    years_data = {}
    print("Fetching blues-rock counts...")
    for year in range(YEAR_START, YEAR_END + 1):
        count = fetch_blues_rock_count(year)
        years_data[str(year)] = count
        time.sleep(1.1)  # Rate limiting
        
    out_file = 'src/api/blues_rock.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(years_data, f, indent=2)
    print(f"Saved counts to {out_file}")

if __name__ == "__main__":
    main()
