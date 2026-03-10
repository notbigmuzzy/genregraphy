<template>
    <PageTitle
        :options="options"
        @update:option="updateOption"
        @showStats="showStatsScreen = $event"
    />
    <div class="the-frame">
        <Transition name="frame" mode="out-in">
            <LoadPagePanel
                v-if="!loaded"
                key="load-panel"
                @loaded="loaded = $event"
            />
            <WorldMap
                v-else-if="genres && !showDetails && !showStatsScreen"
                key="world-map"
                :genres="genres"
                :currentYear="currentYear"
                :continents="continents"
                :options="options"
                @genre-click="selectedGenre = $event; showDetails = true"
                @wheel="onMapScroll"
            />
            <DetailsPanel
                v-else-if="showDetails && !showStatsScreen"
                key="details-panel"
                :genre="selectedGenre"
                :year="currentYear"
                :isPeak="genres?.[currentYear]?.metadata?.peak_genres?.includes(selectedGenre) || false"
                :albums="selectedGenreAlbums"
                @close="showDetails = false"
            />
            <StatsScreen
                v-else-if="showStatsScreen"
                key="stats-screen"
                @showStats="showStatsScreen = $event"
                :stats="yearlyStats"
                :allData="genres"
            />
        </Transition>
    </div>
    <YearSlider
        v-model="currentYear"
        :loaded="loaded"
        :showStats="showStatsScreen"
        :showDetails="showDetails"
    />
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import PageTitle from './components/PageTitle.vue'
import WorldMap from './components/WorldMap.vue'
import YearSlider from './components/YearSlider.vue'
import LoadPagePanel from './components/LoadPagePanel.vue'
import DetailsPanel from './components/DetailsPanel.vue'
import StatsScreen from './components/StatsScreen.vue'

const genres = ref(null)
const loaded = ref(true)
const selectedGenre = ref(null)
const showDetails = ref(false)
const showStatsScreen = ref(false)

const savedOptions = localStorage.getItem('genregraphy_options')
const options = ref(savedOptions ? JSON.parse(savedOptions) : {
    genreNames: false,
    groupNames: true
})

const updateOption = (key, val) => {
    options.value[key] = val
    if (key === 'genreNames') {
        options.value.groupNames = !val
    } else if (key === 'groupNames') {
        options.value.genreNames = !val
    }
    localStorage.setItem('genregraphy_options', JSON.stringify(options.value))
}

const getYearFromUrl = () => {
    const params = new URLSearchParams(window.location.search)
    const y = parseInt(params.get('year'))
    return y >= 1950 && y <= 2025 ? y : 1983
}

const currentYear = ref(getYearFromUrl())

const selectedGenreAlbums = computed(() => {
    let count = 0
    if (genres.value?.[currentYear.value]?.genre_group && selectedGenre.value) {
        for (const group of genres.value[currentYear.value].genre_group) {
            if (group.genres?.[selectedGenre.value]) {
                count = group.genres[selectedGenre.value]
                break
            }
        }
    }
    return count
})

const yearlyStats = computed(() => {
    if (!genres.value) return []
    const stats = []
    for (let y = 1950; y <= 2025; y++) {
        let genreCount = 0
        let albumCount = 0
        if (genres.value[y]?.genre_group) {
            for (const group of genres.value[y].genre_group) {
                if (group.genres) {
                    for (const count of Object.values(group.genres)) {
                        if (count > 0) {
                            genreCount++
                            albumCount += count
                        }
                    }
                }
            }
        }
        stats.push({ year: y, genres: genreCount, albums: albumCount })
    }
    return stats
})

const continents = {
    west:  ['Electronic & Synth', 'Rhythm & Groove', 'Pop & Melodies'],
    east:  ['Rock & Overdrive', 'Jazz & Blues', 'Folk & Acoustics', 'Classical & Experimental'],
    north: ['Metal & Heavy'],
    south: ['Reggae & Global Beats'],
}

let lastScrollTime = 0
const onMapScroll = (e) => {
    if (window.innerWidth > 820) {
        e.preventDefault()
        
        const now = Date.now()
        if (now - lastScrollTime < 750) return
        lastScrollTime = now
        const dir = e.deltaY > 0 ? 1 : -1
        currentYear.value = Math.min(2025, Math.max(1950, currentYear.value + dir))
    }
}

watch(currentYear, (y) => {
    const params = new URLSearchParams(window.location.search)
    params.set('year', y)
    history.replaceState(null, '', '?' + params.toString())
})

const onKeyDown = (e) => {
    if (e.target && e.target.closest && e.target.closest('[class*="slider"]')) return

    switch (e.key) {
        case 'ArrowDown':
            currentYear.value = Math.min(2025, currentYear.value + 1)
            break
        case 'ArrowUp':
            currentYear.value = Math.max(1950, currentYear.value - 1)
            break
        case 'PageDown':
            currentYear.value = Math.min(2025, currentYear.value + 5)
            break
        case 'PageUp':
            currentYear.value = Math.max(1950, currentYear.value - 5)
            break
        case 'Home':
            currentYear.value = 1950
            break
        case 'End':
            currentYear.value = 2025
            break
    }
}

onMounted(async () => {
    window.addEventListener('keydown', onKeyDown)
    const response = await import('./api/genres.json')
    genres.value = response.default
})

onUnmounted(() => {
    window.removeEventListener('keydown', onKeyDown)
})

</script>