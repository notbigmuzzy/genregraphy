<template>
    <div class="year-slider-container" :class="{ disabled: !loaded || showDetails }" @click="handleSliderClick">
        <Slider
            v-model="internalYear"
            :orientation="sliderOrientation"
            :min="1950"
            :max="2025"
            :step="1"
            :lazy="true"
            :options="sliderOptions"
        />
    </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import Slider from '@vueform/slider'

const props = defineProps({
    modelValue: {
        type: Number,
        default: 1950
    },
    loaded: {
        type: Boolean,
        default: false
    },
    showDetails: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['update:modelValue'])

const internalYear = ref(props.modelValue)

watch(internalYear, (newValue) => {
    emit('update:modelValue', newValue)
})

watch(() => props.modelValue, (newValue) => {
    internalYear.value = newValue
})

const windowWidth = ref(window.innerWidth)
const handleResize = () => {
    windowWidth.value = window.innerWidth
}

onMounted(() => {
    window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
})

const sliderOrientation = computed(() => windowWidth.value < 820 ? 'horizontal' : 'vertical')

const handleSliderClick = (e) => {
    const el = e.target.closest('.special-label')
    if (el && el.dataset.value) {
        internalYear.value = Number(el.dataset.value)
    }
}

const specialYears = {
    1951: "Rock n' Roll Birth",
    1964: "British Invasion",
    1968: "Heavy Metal Genesis",
    1977: "Punk & Disco",
    1984: "Synth-Pop Dominance",
    1993: "The Grunge Takeover",
    2001: "Nu-Metal Peak",
    2009: "EDM Explosion",
    2018: "Hip-Hop Hegemony"
}

const sliderOptions = {
    pips: {
        mode: 'steps',
        density: 2,
        filter: (value) => {
            if (specialYears[value]) return 1
            if (value % 10 === 0) return 1
            if (value % 5 === 0) return 2
            return 0
        },
        format: {
            to: (value) => {
                if (specialYears[value]) {
                    return `<span class="special-label" data-value="${value}">${specialYears[value]}</span>`
                } else {
                    return `<span class="common-label" data-value="${value}">${value}</span>`
                }
            }
        }
    }
}
</script>

<style lang="scss">
/* Sakriva sistemske markere (crtice) za specijalne labele */
.slider-marker:has(+ .slider-value .special-label) {
    display: none !important;
}
</style>
