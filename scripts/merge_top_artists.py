import json
import os
import glob

def merge_top_artists_names():
    # Putanja do foldera sa dekadama
    decades_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'api', 'decades')
    json_files = glob.glob(os.path.join(decades_dir, '*.json'))
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            changed = False
            for category, genres in data.items():
                for genre_name, genre_data in genres.items():
                    if 'top_artists' in genre_data:
                        artists = genre_data['top_artists']
                        
                        # Ako postoji više od jednog izvođača, spoji ih
                        if len(artists) > 1:
                            names = [artist['name'] for artist in artists if 'name' in artist]
                            if names:
                                merged_name = ', '.join(names)
                                genre_data['top_artists'] = [{'name': merged_name}]
                                changed = True
            
            # Ako smo napravili izmenu, čuvamo fajl
            if changed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent='\t', ensure_ascii=False)
                print(f"Ažuriran: {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"Greška pri procesiranju {file_path}: {e}")

if __name__ == '__main__':
    merge_top_artists_names()
