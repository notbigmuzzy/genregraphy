<template>
    <div class="details-panel">
        <div class="detailspanel-section">
            <button @click="$emit('close')">← Back</button>
        </div>
        <br /><br />

        <div class="details-area">
            <div class="detailspanel-section title center">
                <p>Details for genre <b>{{ genre }}</b> in the year <b>{{ year }}</b></p>
            </div>

            <div class="detailspanel-section">
                <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Quas alias, saepe distinctio numquam voluptas pariatur, voluptatem, sequi molestias ex corrupti architecto eius. Minima quos, totam necessitatibus quidem enim fugiat ipsam?</p>
                <p>Sit amet consectetur adipisicing elit. Lorem, ipsum dolor sit amet consectetur adipisicing elit. Voluptas . Voluptatibus dignissimos autem nihil consequatur!</p>
            </div>
            <div class="detailspanel-section">
                <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Quas alias, saepe distinctio numquam voluptas pariatur, voluptatem, sequi molestias ex corrupti architecto eius. Minima quos, totam necessitatibus quidem enim fugiat ipsam?</p>
            </div>

            <hr />
        </div>
    </div>
</template>

<script setup>
defineProps({
    genre: {
        type: String,
        default: null
    },
    year: {
        type: Number,
        required: true
    }
})

defineEmits(['close'])
</script>
