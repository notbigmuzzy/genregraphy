<template>
    <div class="year-slider-container">
        <Slider
            v-model="internalYear"
            orientation="vertical"
            :min="1950"
            :max="2025"
            :step="1"
            :lazy="true"
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
</script>
