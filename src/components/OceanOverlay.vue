<template>
    <div class="ocean-overlay">
        <Sextant :year="props.year" />
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
    }
})

</script>