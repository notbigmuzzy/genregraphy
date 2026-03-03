<template>
    <div class="world-map">
        <OceanOverlay :year="currentYear" />
        <MusicMap class="continent continent-west" :genres="genres" :year="currentYear" :allowedGroups="continents.west" />
        <MusicMap class="continent continent-east" :genres="genres" :year="currentYear" :allowedGroups="continents.east" />
        <MusicMap class="continent continent-north" :genres="genres" :year="currentYear" :allowedGroups="continents.north" />
        <MusicMap class="continent continent-south" :genres="genres" :year="currentYear" :allowedGroups="continents.south" />
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

</script>
