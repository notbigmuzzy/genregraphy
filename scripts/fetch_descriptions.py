import json
import urllib.request
import urllib.parse
import time
import re
import os

API_KEY = "8b962327fc2137d86986845f9c046e02"
GENRES_TXT = "scripts/texts/genres.txt"
OUTPUT_JSON = "src/api/genre_descriptions.json"

def clean_summary(text):
    if not text:
        return ""
    # Ukloni "Read more on Last.fm" link
    text = re.sub(r'<a href="https://www\.last\.fm/.*?>Read more on Last\.fm</a>', '', text, flags=re.IGNORECASE)
    # Ukloni sve preostale html tagove za svaki slucaj
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def main():
    if not os.path.exists(GENRES_TXT):
        print(f"File not found: {GENRES_TXT}")
        return

    with open(GENRES_TXT, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    genres = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            genres.append(line)

    print(f"Pronadjeno {len(genres)} zanrova za obradu.")
    
    descriptions = {}
    
    # Ako vec postoji deo fajla, ucitaj ga da ne idemo s pocetka zbog rate limits
    if os.path.exists(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
                descriptions = json.load(f)
        except:
            pass

    for i, curr_genre in enumerate(genres):
        if curr_genre in descriptions and descriptions[curr_genre]:
            continue # Preskoci vec obradjene
            
        print(f"[{i+1}/{len(genres)}] Skidam info za: {curr_genre}... ", end="")
        
        url = f"https://ws.audioscrobbler.com/2.0/?method=tag.getinfo&tag={urllib.parse.quote(curr_genre)}&api_key={API_KEY}&format=json"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Genregraphy/1.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                tag_info = data.get('tag', {})
                wiki = tag_info.get('wiki', {})
                summary = wiki.get('summary', '')
                
                cleaned = clean_summary(summary)
                descriptions[curr_genre] = cleaned
                
                if not cleaned:
                    print("NEMA OPISA!")
                else:
                    print("OK")
                    
        except Exception as e:
            print(f"Greška: {e}")
        
        # Podesi mali delay zbog rate limits (cesto max 5 po sekundi, mi idemo 0.5s)
        time.sleep(0.5)
        
        # Sčuvaj svakih 10 radi sigurnosti
        if i % 10 == 0:
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(descriptions, f, indent=2, ensure_ascii=False)

    # Zavrsno cuvanje
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(descriptions, f, indent=2, ensure_ascii=False)

    print("\nZavršeno! Fajl sačuvan u", OUTPUT_JSON)

if __name__ == "__main__":
    main()
