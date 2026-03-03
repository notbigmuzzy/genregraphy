<template>
    <div class="details-panel">
        <div class="detailspanel-section">
            <button @click="$emit('close')">← Back</button>
        </div>
        <br /><br />

        <div class="details-area">
            <div class="detailspanel-section title center">
                <span><p>Genre <b>{{ genre }}</b> in the year <b>{{ year }}</b></p></span>
            </div>

            <div class="detailspanel-section">
                <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Quas alias, saepe distinctio numquam voluptas pariatur, voluptatem, sequi molestias ex corrupti architecto eius. Minima quos, totam necessitatibus quidem enim fugiat ipsam?</p>
                <p>Sit amet consectetur adipisicing elit. Lorem, ipsum dolor sit amet consectetur adipisicing elit. Voluptas . Voluptatibus dignissimos autem nihil consequatur!</p>
            </div>
            <div class="detailspanel-section">
                <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Quas alias, saepe distinctio numquam voluptas pariatur, voluptatem, sequi molestias ex corrupti architecto eius. Minima quos, totam necessitatibus quidem enim fugiat ipsam?</p>
            </div>

            <hr />

            <template v-if="genreData">
                <div class="detailspanel-section">
                    <h3>Top Artists for {{ decade }}s in {{ genre }}</h3>
                    <ul>
                        <li v-for="artist in genreData.top_artists" :key="artist.name">
                            <span>{{ artist.name }}</span>
                        </li>
                    </ul>
                </div>
                <hr />
                <div class="detailspanel-section">
                    <h3>Top Albums — {{ decade }}s</h3>
                    <ul>
                        <li v-for="album in genreData.top_albums" :key="album.name + album.artist">
                            <em>{{ album.name }}</em> — {{ album.artist }}
                            <span class="details-count">({{ album.year }})</span>
                        </li>
                    </ul>
                </div>
            </template>
            <template v-else>
                <div class="detailspanel-section"><p>No data available for the {{ decade }}s.</p></div>
            </template>

            <hr />
        </div>
    </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
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

const decade = computed(() => props.year ? Math.floor(props.year / 10) * 10 : null)
const loading = ref(false)
const genreData = ref(null)

const loadDecadeData = async () => {
    if (!props.genre || !decade.value) return

    loading.value = true
    genreData.value = null

    try {
        const data = await import(`../api/decades/${decade.value}.json`)
        const decadeJson = data.default

        for (const group of Object.values(decadeJson)) {
            const genreKey = Object.keys(group).find(
                k => k.toLowerCase() === props.genre.toLowerCase()
            )
            if (genreKey) {
                genreData.value = group[genreKey]
                break
            }
        }
    } catch {
        genreData.value = null
    } finally {
        loading.value = false
    }
}

watch([() => props.genre, () => props.year], loadDecadeData, { immediate: true })
</script>
