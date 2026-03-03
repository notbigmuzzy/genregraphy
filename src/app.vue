<template>
    <PageTitle />
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
                @genre-click="selectedGenre = $event; showDetails = true"
                @wheel.prevent="onMapScroll"
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
import { ref, watch, onMounted } from 'vue'
import PageTitle from './components/PageTitle.vue'
import WorldMap from './components/WorldMap.vue'
import YearSlider from './components/YearSlider.vue'
import LoadPagePanel from './components/LoadPagePanel.vue'
import DetailsPanel from './components/DetailsPanel.vue'

const genres = ref(null)
const loaded = ref(true)
const selectedGenre = ref(null)
const showDetails = ref(false)

const getYearFromUrl = () => {
    const params = new URLSearchParams(window.location.search)
    const y = parseInt(params.get('year'))
    return y >= 1950 && y <= 2025 ? y : 1950
}

const currentYear = ref(getYearFromUrl())

const continents = {
    west:  ['Electronic & Synth', 'Hip-Hop & Groove', 'Pop & Melodies'],
    east:  ['Rock & Overdrive', 'Jazz, Blues & Soul', 'Folk & Acoustics', 'Classical & Experimental'],
    north: ['Metal & Heavy'],
    south: ['Reggae & Global Beats'],
}

let lastScrollTime = 0
const onMapScroll = (e) => {
    const now = Date.now()
    if (now - lastScrollTime < 750) return
    lastScrollTime = now
    const dir = e.deltaY > 0 ? 1 : -1
    currentYear.value = Math.min(2025, Math.max(1950, currentYear.value + dir))
}

watch(currentYear, (y) => {
    const params = new URLSearchParams(window.location.search)
    params.set('year', y)
    history.replaceState(null, '', '?' + params.toString())
})

onMounted(async () => {
    const response = await import('./api/genres.json')
    genres.value = response.default
})

</script>