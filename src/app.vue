<template>
    <div class="world-map" v-if="genres">
        <MusicMap class="continent continent--west" :genres="genres" :year="currentYear" :allowedGroups="continents.west" />
        <MusicMap class="continent continent--east" :genres="genres" :year="currentYear" :allowedGroups="continents.east" />
        <MusicMap class="continent continent--north" :genres="genres" :year="currentYear" :allowedGroups="continents.north" />
        <MusicMap class="continent continent--south" :genres="genres" :year="currentYear" :allowedGroups="continents.south" />
    </div>
    <YearSlider v-model="currentYear" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MusicMap from './components/MusicMap.vue'
import YearSlider from './components/YearSlider.vue'

const genres = ref(null)
const currentYear = ref(1950)

const continents = {
    west:  ['Electronic & Synth', 'Hip-Hop & Groove', 'Pop & Melodies'],
    east:  ['Rock & Overdrive', 'Jazz, Blues & Soul', 'Folk & Acoustics', 'Classical & Experimental'],
    north: ['Metal & Heavy'],
    south: ['Reggae & Global Beats'],
}

onMounted(async () => {
    const response = await import('./api/genres.json')
    genres.value = response.default
})
</script>