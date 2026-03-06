<template>
    <div 
        class="world-map"
        :class="{
            'showing-genre-names': options?.genreNames,
            'showing-group-names': options?.groupNames
        }"
    >
        <OceanOverlay :year="currentYear" />
        <MusicMap class="continent continent-west" :genres="genres" :year="currentYear" :allowedGroups="continents.west" :options="options" @genre-click="$emit('genre-click', $event)" />
        <MusicMap class="continent continent-east" :genres="genres" :year="currentYear" :allowedGroups="continents.east" :options="options" @genre-click="$emit('genre-click', $event)" />
        <MusicMap class="continent continent-north" :genres="genres" :year="currentYear" :allowedGroups="continents.north" :options="options" @genre-click="$emit('genre-click', $event)" />
        <MusicMap class="continent continent-south" :genres="genres" :year="currentYear" :allowedGroups="continents.south" :options="options" @genre-click="$emit('genre-click', $event)" />
    </div>
</template>

<script setup>
import MusicMap from './MusicMap.vue'
import OceanOverlay from './OceanOverlay.vue'

const props = defineProps({
    genres: Object,
    currentYear: Number,
    continents: Object,
    options: Object,
})

const emit = defineEmits(['genre-click'])

</script>
