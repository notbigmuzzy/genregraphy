import json
from pathlib import Path

decades_data = {
    "1950": {
        "top_artists": [{"name": "Muddy Waters, Howlin' Wolf, B.B. King, Bo Diddley, Elmore James, John Lee Hooker, Jimmy Reed, Buddy Guy, T-Bone Walker, Chuck Berry"}],
        "top_albums": [
            {"name": "The Best of Muddy Waters", "artist": "Muddy Waters", "year": "1958"},
            {"name": "Moanin' in the Moonlight", "artist": "Howlin' Wolf", "year": "1959"},
            {"name": "Bo Diddley", "artist": "Bo Diddley", "year": "1958"},
            {"name": "Sing and Play the Blues", "artist": "B.B. King", "year": "1959"},
            {"name": "I'm John Lee Hooker", "artist": "John Lee Hooker", "year": "1959"}
        ],
        "sample_tracks": [{"name": "Hoochie Coochie Man", "artist": "Muddy Waters", "album": "The Best of Muddy Waters"}]
    },
    "1960": {
        "top_artists": [{"name": "Cream, The Jimi Hendrix Experience, The Rolling Stones, The Yardbirds, Fleetwood Mac, Ten Years After, The Animals, The Paul Butterfield Blues Band, Canned Heat, Jeff Beck Group"}],
        "top_albums": [
            {"name": "Disraeli Gears", "artist": "Cream", "year": "1967"},
            {"name": "Are You Experienced", "artist": "The Jimi Hendrix Experience", "year": "1967"},
            {"name": "Truth", "artist": "Jeff Beck Group", "year": "1968"},
            {"name": "Fleetwood Mac", "artist": "Fleetwood Mac", "year": "1968"},
            {"name": "The Paul Butterfield Blues Band", "artist": "The Paul Butterfield Blues Band", "year": "1965"}
        ],
        "sample_tracks": [{"name": "Sunshine of Your Love", "artist": "Cream", "album": "Disraeli Gears"}]
    },
    "1970": {
        "top_artists": [{"name": "Led Zeppelin, ZZ Top, The Allman Brothers Band, Aerosmith, Bad Company, Rory Gallagher, Free, Robin Trower, Foghat, Johnny Winter"}],
        "top_albums": [
            {"name": "Sticky Fingers", "artist": "The Rolling Stones", "year": "1971"},
            {"name": "Tres Hombres", "artist": "ZZ Top", "year": "1973"},
            {"name": "Irish Tour '74", "artist": "Rory Gallagher", "year": "1974"},
            {"name": "Bad Company", "artist": "Bad Company", "year": "1974"},
            {"name": "Bridge of Sighs", "artist": "Robin Trower", "year": "1974"}
        ],
        "sample_tracks": [{"name": "La Grange", "artist": "ZZ Top", "album": "Tres Hombres"}]
    },
    "1980": {
        "top_artists": [{"name": "Stevie Ray Vaughan and Double Trouble, George Thorogood and the Destroyers, The Fabulous Thunderbirds, ZZ Top, Gary Moore, Eric Clapton, Robert Cray, The Jeff Healey Band, Bonnie Raitt, Colin James"}],
        "top_albums": [
            {"name": "Texas Flood", "artist": "Stevie Ray Vaughan and Double Trouble", "year": "1983"},
            {"name": "Bad to the Bone", "artist": "George Thorogood and the Destroyers", "year": "1982"},
            {"name": "Tuff Enuff", "artist": "The Fabulous Thunderbirds", "year": "1986"},
            {"name": "Journeyman", "artist": "Eric Clapton", "year": "1989"},
            {"name": "See the Light", "artist": "The Jeff Healey Band", "year": "1988"}
        ],
        "sample_tracks": [{"name": "Pride and Joy", "artist": "Stevie Ray Vaughan and Double Trouble", "album": "Texas Flood"}]
    },
    "1990": {
        "top_artists": [{"name": "Jonny Lang, Kenny Wayne Shepherd Band, The Black Crowes, Gov't Mule, Gary Moore, Susan Tedeschi, Blues Traveler, Ben Harper, The White Stripes, Joe Bonamassa"}],
        "top_albums": [
            {"name": "Still Got the Blues", "artist": "Gary Moore", "year": "1990"},
            {"name": "Shake Your Money Maker", "artist": "The Black Crowes", "year": "1990"},
            {"name": "Ledbetter Heights", "artist": "Kenny Wayne Shepherd Band", "year": "1995"},
            {"name": "Lie to Me", "artist": "Jonny Lang", "year": "1997"},
            {"name": "Gov't Mule", "artist": "Gov't Mule", "year": "1995"}
        ],
        "sample_tracks": [{"name": "Still Got the Blues", "artist": "Gary Moore", "album": "Still Got the Blues"}]
    },
    "2000": {
        "top_artists": [{"name": "The White Stripes, The Black Keys, John Mayer Trio, Joe Bonamassa, The Raconteurs, Derek Trucks Band, Gov't Mule, Clutch, The Jon Spencer Blues Explosion, North Mississippi Allstars"}],
        "top_albums": [
            {"name": "Elephant", "artist": "The White Stripes", "year": "2003"},
            {"name": "Thickfreakness", "artist": "The Black Keys", "year": "2003"},
            {"name": "Try!", "artist": "John Mayer Trio", "year": "2005"},
            {"name": "The Ballad of John Henry", "artist": "Joe Bonamassa", "year": "2009"},
            {"name": "Consolers of the Lonely", "artist": "The Raconteurs", "year": "2008"}
        ],
        "sample_tracks": [{"name": "Seven Nation Army", "artist": "The White Stripes", "album": "Elephant"}]
    },
    "2010": {
        "top_artists": [{"name": "The Black Keys, Gary Clark Jr., Rival Sons, Kaleo, Marcus King Band, Royal Blood, Christone \\\"Kingfish\\\" Ingram, The Record Company, Greta Van Fleet, Tyler Bryant & The Shakedown"}],
        "top_albums": [
            {"name": "El Camino", "artist": "The Black Keys", "year": "2011"},
            {"name": "Blak and Blu", "artist": "Gary Clark Jr.", "year": "2012"},
            {"name": "Great Western Valkyrie", "artist": "Rival Sons", "year": "2014"},
            {"name": "Kingfish", "artist": "Christone \\\"Kingfish\\\" Ingram", "year": "2019"},
            {"name": "A/B", "artist": "Kaleo", "year": "2016"}
        ],
        "sample_tracks": [{"name": "Lonely Boy", "artist": "The Black Keys", "album": "El Camino"}]
    },
    "2020": {
        "top_artists": [{"name": "Marcus King, Christone \\\"Kingfish\\\" Ingram, Samantha Fish, Larkin Poe, Rival Sons, Black Pistol Fire, The Black Keys, Fantastic Negrito, Ayron Jones, Gov't Mule"}],
        "top_albums": [
            {"name": "El Dorado", "artist": "Marcus King", "year": "2020"},
            {"name": "662", "artist": "Christone \\\"Kingfish\\\" Ingram", "year": "2021"},
            {"name": "Blood Harmony", "artist": "Larkin Poe", "year": "2022"},
            {"name": "Dropout Boogie", "artist": "The Black Keys", "year": "2022"},
            {"name": "Darkfighter", "artist": "Rival Sons", "year": "2023"}
        ],
        "sample_tracks": [{"name": "The Well", "artist": "Marcus King", "album": "El Dorado"}]
    }
}

def inject_blues_rock_decades():
    decades_dir = Path("src/api/decades")
    target_group = "Jazz, Blues & Soul"
    
    for decade, decade_content in decades_data.items():
        file_path = decades_dir / f"{decade}.json"
        
        if not file_path.exists():
            print(f"Warning: {file_path} doesn't exist. Skipping.")
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if target_group not in data:
            data[target_group] = {}
            
        data[target_group]["blues-rock"] = decade_content
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Successfully injected blues-rock into {file_path}")

if __name__ == "__main__":
    inject_blues_rock_decades()
