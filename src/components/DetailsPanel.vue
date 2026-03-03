<template>
    <div class="details-panel">
        <div class="detailspanel-section">
            <button @click="$emit('close')">← Back</button>
        </div>
        <br />
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
                <div class="detailspanel-section wiki">
                    <h3>Top Artists for {{ decade }}s in {{ genre }}</h3>
                    <ul>
                        <li v-for="artist in genreData.top_artists" :key="artist.name">
                            <button
                                @click.prevent="openWiki(artist.name)"
                                :class="{ 'is-active': activeWikiArtist === artist.name }"
                            >
                                {{ artist.name }}
                                <span v-if="activeWikiArtist === artist.name"> ✕</span>
                            </button>
                        </li>
                    </ul>
                </div>
                <div class="wikipedia-iframe" :class="{ 'is-open': wikiOpen }" ref="wikiContainer"/>
                <hr />
                <div class="detailspanel-section albums">
                    <h3>Top Albums — {{ decade }}s</h3>
                    <ul>
                        <li v-for="album in genreData.top_albums" :key="album.name + album.artist">
                            <button>
                                <em>{{ album.name }}</em> — {{ album.artist }}
                                <span class="details-count">({{ album.year }})</span>
                            </button>
                        </li>
                    </ul>
                </div>
                <hr />
                <div class="detailspanel-section preview">
                    <h3>Sample tracks</h3>
                    <div class="player-wrap">
                        <button @click="handleRecordClick(genreData.sample_tracks[0]?.artist)">
                            Play Sample Track
                        </button>
                        <audio controls id="samplePlayer">
                            <source src="#" type="audio/mpeg">
                            Your browser does not support the audio element.
                        </audio>
                    </div>
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

const handleRecordClick = async (name) => {
    const url = await getAudioUrl(name);
    if (url) {
        const audio = document.getElementById('samplePlayer');
        audio.src = url;
        audio.play();
		audio.classList.add('playing');
    } else {
        console.log("No audio found for " + name);
    }
}

const getAudioUrl = async (artist) => {
    try {
        const searchUrl = `https://archive.org/advancedsearch.php?q=creator%3A(${encodeURIComponent(artist)})+AND+mediatype%3A(audio)&fl[]=identifier&output=json`;
        
        const searchRes = await fetch(searchUrl);
        const searchData = await searchRes.json();
        const docs = searchData.response.docs;

        if (!docs || docs.length === 0) return null;

        const identifier = docs.length > 1 ? docs[1].identifier : docs[0].identifier;
        const metaUrl = `https://archive.org/metadata/${identifier}`;
        const metaRes = await fetch(metaUrl);
        const metaData = await metaRes.json();
        const mp3File = metaData.files.find(f => f.name.endsWith('.mp3'));

        if (mp3File) {
            return `https://archive.org/download/${identifier}/${mp3File.name}`;
        }
        
        return null;
    } catch (error) {
        console.error("No sample for this Artist", error);
        return null;
    }
}

const wikiUrl = ref(null)
const wikiOpen = ref(false)
const wikiContainer = ref(null)
const activeWikiArtist = ref(null)

const closeWiki = () => {
    wikiContainer.value.innerHTML = ''
	wikiOpen.value = false
	activeWikiArtist.value = null
}

const openWiki = (name) => {
	if (!name) return

	if (activeWikiArtist.value === name) {
		closeWiki()
		return
	}

    const pageUrl = `https://en.m.wikipedia.org/wiki/${encodeURIComponent(name)}`
    wikiUrl.value = pageUrl
	wikiOpen.value = true
	activeWikiArtist.value = name

	if (wikiContainer.value) {
		wikiContainer.value.innerHTML = `<iframe src="${pageUrl}" style="width:100%;height:600px;border:none;" loading="lazy"></iframe>`

		setTimeout(() => {
            const scrollParent = wikiContainer.value.closest('.details-area')
            const wikiSection = scrollParent?.querySelector('.detailspanel-section.wiki')
            if (scrollParent && wikiSection) {
                scrollParent.scrollTo({
                    top: wikiSection.offsetTop - 80,
                    behavior: 'smooth'
                })
            }
		}, 400)
	}
}

watch([() => props.genre, () => props.year], loadDecadeData, { immediate: true })
</script>
