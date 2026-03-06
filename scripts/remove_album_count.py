import json
import os
import glob

def remove_album_count_from_decades():
    # Putanja do foldera sa dekadama
    decades_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'api', 'decades')
    json_files = glob.glob(os.path.join(decades_dir, '*.json'))
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Prilagođavanje strukture i uklanjanje album_count
            changed = False
            for category, genres in data.items():
                for genre_name, genre_data in genres.items():
                    if 'top_artists' in genre_data:
                        for artist in genre_data['top_artists']:
                            if 'album_count' in artist:
                                del artist['album_count']
                                changed = True
            
            # Ako smo napravili izmenu, čuvamo fajl
            if changed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent='\t', ensure_ascii=False)
                print(f"Ažuriran: {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"Greška pri procesiranju {file_path}: {e}")

if __name__ == '__main__':
    remove_album_count_from_decades()
