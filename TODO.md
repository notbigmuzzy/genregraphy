# PHASE 1: Data Engineering (The Python Scraper)
<!-- Goal: Create a lightweight, high-performance static "API" using JSON files.
[*] Define the Genre Taxonomy: Curate a list of ~100 primary genres. Map obscure sub-genres to these "umbrella" terms (e.g., Acid House -> House)
[*] Extract "The Pulse" (Map Data):
    Iterate through years 1950–2025.
    Aggregate counts of album releases per genre per year.
    Logic: One album with 3 tags = +1 point for each respective genre.
[*] Extract "The Vault" (Discovery Data):
    For every year + genre combination, fetch 20–30 random releases.
    Store minimal metadata: Title, Artist, Release Year, and MusicBrainz ID (MBID).
[*] Optimization & Export:
    Export summary.json: A compact file mapping Year -> Genre -> Count.
    Export details/: A directory of JSON files named by genre (e.g., rock.json) containing the chronological catalog. -->

# PHASE 2: Frontend Architecture (Vue 3)
<!-- Goal: Build the "skeleton" to handle state and navigation.
[*] Project Setup: Initialize Vue 3 with D3
[*] State Management: Set up a global store (Pinia or a reactive object) to track:
    currentYear (linked to the slider).
    selectedGenre (linked to map clicks).
[*] Component Layout:
    <GenreMap />: The D3 container.
    <TimeSlider />: A custom range input for scrubbing through decades.
    <InfoPanel />: A slide-out sidebar for album/artist discovery. -->

# PHASE 3: Data Visualization (D3.js)
<!-- Goal: Turn numbers into "living" territories.
[*] Coordinate Anchoring: Assign fixed "center points" for major genre families (e.g., Electronics in the top-right, Rock in the center) to prevent the map from spinning erratically during transitions.
[*] Voronoi Engine: Implement a Weighted Voronoi Tessellation where the "weight" (album count) determines the polygon's area.
[*] The Time-Traveler Logic:
    Watch the currentYear state.
    Use d3.interpolate() to smoothly "morph" the polygon boundaries when the slider moves.
[*] Interaction Layer: Add on("click") events to polygons to update the global selectedGenre. -->

# PHASE 4: User Experience & Polish
<!-- Goal: Make the map feel like a premium discovery tool.
[*] Lazy Loading: Implement a fetcher that only downloads rock.json the first time a user clicks the Rock territory.
[*] Randomized Discovery: Inside the sidebar, use a shuffle function to display 5–10 random entries for the active year from your pre-scraped data.
[*] Visual "Continents": Apply color palettes based on genre families (e.g., shades of blue for Electronic, reds for Rock) to help user orientation.
[*] Responsive Design: Ensure the SVG map scales correctly for different screen sizes. -->

# EXTRA
<!-- 1. Vizuelni Identitet HARD NOUP
    Default Year (1983): Maksimalan "decay". Implementacija SVG/Canvas filtera za desaturaciju (crno-belo), feTurbulence za šum (grain) i blagu hromatsku aberaciju na ivicama polja.
    Evolucija (1983 ➔ 2026): Linearni prelaz ka kristalno čistoj, visokokontrastnoj modernoj estetici (Retina-ready).
    Vignette: Blago zatamnjenje uglova ekrana za starije godine koje fokusira pogled na centar mape. -->

2. Navigacija Lore Scrollbar
    Snap Points: Desetak markera na scrollbar-u za ključne istorijske momente (npr. Birth of Metal, Synth Pop Explosion, Grunge Rupture).
    Visual Feedback: Ti podeoci su deblji ili drugačije boje; na hover/snap se aktivira kratak, ciničan naslov (bez marketing slopa).
    State Persistence: Svaki pomeraj scrollbar-a ažurira URL parametar (?year=XXXX), tako da je svaka godina "shareable" link.

3. Interakcija Autoplay + Keyboard controls
    Autoplay Mode: Opciona funkcija koja automatski "vozi" kroz decenije uz glatke D3 transitions.
    Interactive Override: Autoplay se trenutno gasi čim korisnik dotakne mapu ili scrollbar (poštovanje namere korisnika).
    Transition Logic: Novi žanrovi fizički "guraju" stare polja, simulirajući pritisak i promenu u muzičkom ekosistemu.

4. Share & Export: "Cartographic Snapshots"
    SVG Snapshot: Dugme za eksport trenutnog stanja mape u visokoj rezoluciji.
    Snapshot Metadata: Na dnu eksporta diskretno piše godina i možda tvoj potpis (npr. "Cartographic Record: 1983").
    Direct Sharing: Pošto URL prati godinu, share dugme samo kopira link koji otvara mapu tačno u tom momentu.