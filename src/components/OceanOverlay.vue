<template>
    <div class="ocean-overlay">
        <Sextant :year="props.year" :albums="props.albums" :genres="props.genres" />
        <Fish />
        <Shrimps />
        <Seahorse />
        <Bottle />
        <Ship />
    </div>
</template>

<script setup>
import Sextant from '../icons/Sextant.vue'
import Fish from '../icons/Fish.vue'
import Shrimps from '../icons/Shrimps.vue'
import Seahorse from '../icons/Seahorse.vue'
import Bottle from '../icons/Bottle.vue'
import Ship from '../icons/Ship.vue'

const props = defineProps({
    year: {
        type: Number,
        required: true
    },
    albums: {
        type: Number,
        default: 0
    },
    genres: {
        type: Number,
        default: 0
    }
})

</script>