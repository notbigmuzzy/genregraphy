<template>
    <div 
        class="world-map"
        :class="{
            'showing-genre-names': options?.genreNames,
            'showing-group-names': options?.groupNames
        }"
    >
        <OceanOverlay :year="currentYear" :albums="yearDetails.albums" :genres="yearDetails.genres" />
        <MusicMap class="continent continent-west" :genres="genres" :year="currentYear" :allowedGroups="continents.west" :options="options" @genre-click="$emit('genre-click', $event)" />
        <MusicMap class="continent continent-east" :genres="genres" :year="currentYear" :allowedGroups="continents.east" :options="options" @genre-click="$emit('genre-click', $event)" />
        <MusicMap class="continent continent-north" :genres="genres" :year="currentYear" :allowedGroups="continents.north" :options="options" @genre-click="$emit('genre-click', $event)" />
        <MusicMap class="continent continent-south" :genres="genres" :year="currentYear" :allowedGroups="continents.south" :options="options" @genre-click="$emit('genre-click', $event)" />
    </div>
</template>

<script setup>
import { computed } from 'vue'
import MusicMap from './MusicMap.vue'
import OceanOverlay from './OceanOverlay.vue'

const props = defineProps({
    genres: Object,
    currentYear: Number,
    continents: Object,
    options: Object,
})

const emit = defineEmits(['genre-click'])

const yearDetails = computed(() => {
    let albums = 0
    let genresCount = 0
    if (props.genres && props.genres[props.currentYear]) {
        props.genres[props.currentYear].genre_group.forEach(g => {
            albums += g.total || 0
            if (g.genres) {
                genresCount += Object.values(g.genres).filter(v => v > 0).length
            }
        })
    }
    return { albums, genres: genresCount }
})
</script>
