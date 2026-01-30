# PHASE 1: Data Engineering (The Python Scraper)

Goal: Create a lightweight, high-performance static "API" using JSON files.

[ ] Define the Genre Taxonomy: Curate a list of ~100 primary genres. Map obscure sub-genres to these "umbrella" terms (e.g., Acid House -> House).

[ ] Extract "The Pulse" (Map Data):

    Iterate through years 1950–2025.

    Aggregate counts of album releases per genre per year.

    Logic: One album with 3 tags = +1 point for each respective genre.

[ ] Extract "The Vault" (Discovery Data):

    For every year + genre combination, fetch 20–30 random releases.

    Store minimal metadata: Title, Artist, Release Year, and MusicBrainz ID (MBID).

[ ] Optimization & Export:

    Export summary.json: A compact file mapping Year -> Genre -> Count.

    Export details/: A directory of JSON files named by genre (e.g., rock.json) containing the chronological catalog.

# PHASE 2: Frontend Architecture (Vue 3)

Goal: Build the "skeleton" to handle state and navigation.

[ ] Project Setup: Initialize Vue 3 with Tailwind CSS for rapid UI styling.

[ ] State Management: Set up a global store (Pinia or a reactive object) to track:

    currentYear (linked to the slider).

    selectedGenre (linked to map clicks).

[ ] Component Layout:

    <GenreMap />: The D3 container.

    <TimeSlider />: A custom range input for scrubbing through decades.

    <InfoPanel />: A slide-out sidebar for album/artist discovery.

# PHASE 3: Data Visualization (D3.js)

Goal: Turn numbers into "living" territories.

[ ] Coordinate Anchoring: Assign fixed "center points" for major genre families (e.g., Electronics in the top-right, Rock in the center) to prevent the map from spinning erratically during transitions.

[ ] Voronoi Engine: Implement a Weighted Voronoi Tessellation where the "weight" (album count) determines the polygon's area.

[ ] The Time-Traveler Logic:

    Watch the currentYear state.

    Use d3.interpolate() to smoothly "morph" the polygon boundaries when the slider moves.

[ ] Interaction Layer: Add on("click") events to polygons to update the global selectedGenre.

# PHASE 4: User Experience & Polish

Goal: Make the map feel like a premium discovery tool.

[ ] Lazy Loading: Implement a fetcher that only downloads rock.json the first time a user clicks the Rock territory.

[ ] Randomized Discovery: Inside the sidebar, use a shuffle function to display 5–10 random entries for the active year from your pre-scraped data.

[ ] Visual "Continents": Apply color palettes based on genre families (e.g., shades of blue for Electronic, reds for Rock) to help user orientation.

[ ] Responsive Design: Ensure the SVG map scales correctly for different screen sizes.

# PHASE 5: Deployment

Goal: Host the project for free with zero maintenance.

[ ] Build & Deploy: Host the final build on GitHub Pages.

[ ] Cache Strategy: Ensure JSON files are served with appropriate cache headers for speed.

### 

STEP 1. Compile your list of 100 genres and run a test script for a single year (e.g., 1994) to see the distribution of "points."

https://musicbrainz.org/genres