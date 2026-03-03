<template>
    <div class="world-map">
        <OceanOverlay :year="currentYear" />
        <MusicMap class="continent continent-west" :genres="genres" :year="currentYear" :allowedGroups="continents.west" @genre-click="$emit('genre-click', $event)" />
        <MusicMap class="continent continent-east" :genres="genres" :year="currentYear" :allowedGroups="continents.east" @genre-click="$emit('genre-click', $event)" />
        <MusicMap class="continent continent-north" :genres="genres" :year="currentYear" :allowedGroups="continents.north" @genre-click="$emit('genre-click', $event)" />
        <MusicMap class="continent continent-south" :genres="genres" :year="currentYear" :allowedGroups="continents.south" @genre-click="$emit('genre-click', $event)" />
    </div>
</template>

<script setup>
import MusicMap from './MusicMap.vue'
import OceanOverlay from './OceanOverlay.vue'

const props = defineProps({
    genres: Object,
    currentYear: Number,
    continents: Object,
})

const emit = defineEmits(['genre-click'])

</script>
