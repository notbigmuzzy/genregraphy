#!/usr/bin/env python3
"""
Generate genre_groups.txt from genres.txt automatically
Reads group headers (comments) and maps genres to groups
"""

from pathlib import Path


def generate_mapping():
    """Generate genre to group mapping from genres.txt structure"""
    genres_file = Path(__file__).parent / 'texts/genres.txt'
    output_file = Path(__file__).parent / 'texts/genre_groups.txt'
    
    current_group = None
    mappings = []
    
    with open(genres_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip first header lines
            if not line or line.startswith('# Genregraphy') or line.startswith('# Add or remove') or line.startswith('# One genre'):
                continue
            
            # Check if it's a group header (comment with group name)
            if line.startswith('#'):
                # Extract group name (remove # and strip)
                current_group = line.lstrip('#').strip()
            elif current_group:
                # It's a genre line, map it to current group
                genre = line.lower()
                mappings.append(f"{genre} -> {current_group}")
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Genre to Group Mapping\n")
        f.write("# Auto-generated from genres.txt\n")
        f.write("# Format: genre -> group name\n\n")
        
        current_group = None
        for mapping in mappings:
            genre, group = mapping.split(' -> ')
            
            # Add group header comment when group changes
            if group != current_group:
                f.write(f"\n# {group}\n")
                current_group = group
            
            f.write(f"{mapping}\n")
    
    print(f"✓ Generated {output_file}")
    print(f"  Total mappings: {len(mappings)}")


if __name__ == "__main__":
    generate_mapping()
