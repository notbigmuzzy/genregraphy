#!/usr/bin/env python3
import json
import os

years_dir = '../src/api/years'
output_file = '../src/api/genres.json'

merged_data = {}

# Učitaj sve godine
for filename in sorted(os.listdir(years_dir)):
    if not filename.endswith('.json'):
        continue
    
    filepath = os.path.join(years_dir, filename)
    year = filename.replace('.json', '')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    merged_data[year] = data
    print(f"Loaded {filename}")

# Sačuvaj spojene podatke
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, indent=2)

print(f"\nMerged {len(merged_data)} years into {output_file}")
