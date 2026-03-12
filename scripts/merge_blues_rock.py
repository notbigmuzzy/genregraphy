import json

def merge_blues_rock():
    with open("src/api/genres.json", "r", encoding="utf-8") as f:
        genres_data = json.load(f)
        
    with open("src/api/blues_rock.json", "r", encoding="utf-8") as f:
        blues_rock_data = json.load(f)
        
    for year, count in blues_rock_data.items():
        if year in genres_data and "genre_group" in genres_data[year]:
            for group in genres_data[year]["genre_group"]:
                if group.get("name") == "Jazz & Blues":
                    if "genres" not in group:
                        group["genres"] = {}
                    group["genres"]["blues-rock"] = count
                    break
            
    with open("src/api/genres.json", "w", encoding="utf-8") as f:
        json.dump(genres_data, f, indent=2, ensure_ascii=False)
        
    print("Successfully merged blues-rock into genres.json under Jazz & Blues")

if __name__ == "__main__":
    merge_blues_rock()

