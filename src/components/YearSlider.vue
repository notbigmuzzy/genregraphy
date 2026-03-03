<template>
    <div class="year-slider-container" :class="loaded ? '' : 'disabled'">
        <Slider
            v-model="internalYear"
            orientation="vertical"
            :min="1950"
            :max="2025"
            :step="1"
            :lazy="true"
            :options="sliderOptions"
        />
    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import Slider from '@vueform/slider'

const props = defineProps({
    modelValue: {
        type: Number,
        default: 1950
    },
    loaded: {
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

const sliderOptions = {
    pips: {
        mode: 'steps',
        density: 2,
        filter: (value) => {
            if (value % 10 === 0) return 1   // MEGA — label + velika crtica
            if (value % 5 === 0) return 2    // mini — mala crtica, bez labele
            return 0
        }
    }
}
</script>
