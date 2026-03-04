# ♪ genregraphy ♪

This is an interactive music genre visualization tool built with Python and D3.js. It renders music genres as a fantasy, cartography map (weighted Voronoi tessellation) where each genre's "territory" grows or shrinks based on its number of album releases in a given year.

---

### Check it out at:
https://notbigmuzzy.github.io/genregraphy/

--

## Tech Stack
- **Vite + Vue 3** — component architecture and state
- **D3.js** — SVG rendering, Voronoi tessellation, animated transitions
- **Python** — data pipeline (MusicBrainz / Last.fm scraping, genre mapping, JSON generation)

---

## Features
Scrub through time from **1950 to 2025** using the year slider and watch the musical landscape shift as genres rise and fall in popularity. Genre families are anchored to cardinal directions like continents — Rock & Metal to the east and north, Electronic & Hip-Hop to the west, Reggae to the south — giving the map a consistent geography across decades.

Click any genre territory to open a details panel with deeper information about that genre. 

The underlying data was assembled from **MusicBrainz** and **Last.fm** via a set of Python scraping and processing scripts.



