<template>
    <PageTitle :options="options" @update:option="updateOption" />
    <div class="the-frame">
        <Transition name="frame" mode="out-in">
            <LoadPagePanel
                v-if="!loaded"
                key="load-panel"
                @loaded="loaded = $event"
            />
            <WorldMap
                v-else-if="genres && !showDetails"
                key="world-map"
                :genres="genres"
                :currentYear="currentYear"
                :continents="continents"
                :options="options"
                @genre-click="selectedGenre = $event; showDetails = true"
                @wheel="onMapScroll"
            />
            <DetailsPanel
                v-else-if="showDetails"
                key="details-panel"
                :genre="selectedGenre"
                :year="currentYear"
                @close="showDetails = false"
            />
        </Transition>
    </div>
    <YearSlider
        v-model="currentYear"
        :loaded="loaded"
        :showDetails="showDetails"
    />
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import PageTitle from './components/PageTitle.vue'
import WorldMap from './components/WorldMap.vue'
import YearSlider from './components/YearSlider.vue'
import LoadPagePanel from './components/LoadPagePanel.vue'
import DetailsPanel from './components/DetailsPanel.vue'

const genres = ref(null)
const loaded = ref(true)
const selectedGenre = ref(null)
const showDetails = ref(false)

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

    if (e.key === 'ArrowDown') {
        currentYear.value = Math.min(2025, currentYear.value + 1)
    } else if (e.key === 'ArrowUp') {
        currentYear.value = Math.max(1950, currentYear.value - 1)
    } else if (e.key === 'PageDown') {
        currentYear.value = Math.min(2025, currentYear.value + 5)
    } else if (e.key === 'PageUp') {
        currentYear.value = Math.max(1950, currentYear.value - 5)
    } else if (e.key === 'Home') {
        currentYear.value = 1950
    } else if (e.key === 'End') {
        currentYear.value = 2025
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