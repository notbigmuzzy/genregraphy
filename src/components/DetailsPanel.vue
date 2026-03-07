<template>
    <div class="details-panel">
        <button class="close-panel" @click="$emit('close')">
            <span>←</span><span>←</span><span>←</span>
        </button>
        <div class="details-area">
            <div class="detailspanel-section title">
                <h2>The {{ year }} {{ formattedGenre }} Scene</h2>
            </div>
            <div class="detailspanel-section" v-if="genreDescription">
                <p>{{ genreDescription }}</p>
            </div>
            <hr />
            <template v-if="genreData">
                <div class="detailspanel-section wiki">
                    <h3>Defining Voices of the {{ decade.toString().substring(2, 3) }}0s in {{ formattedGenre }}</h3>
                    <ul>
                        <li v-for="artistName in genreData.top_artists[0].name.split(', ')" :key="artistName">
                            <button
                                @click.prevent="openWiki(artistName)"
                                :class="{ 'is-active': activeWikiArtist === artistName }"
                            >
                                {{ artistName }}
                                <span v-if="activeWikiArtist === artistName"> ✕</span>
                            </button>
                        </li>
                    </ul>
                </div>
                <div class="wikipedia-iframe-wrap" :class="{ 'is-open': wikiOpen }" ref="wikiContainer"></div>
                <hr />
                <div class="detailspanel-section albums">
                    <h3>Must-Hear Albums</h3>
                    <ul>
                        <li v-for="album in genreData.top_albums" :key="album.name + album.artist">
                            <button @click="openYoutube(album.name, album.artist)" :class="{ 'is-active': activeYoutubeAlbum === album.name }">
                                <em>{{ album.name }}</em> — {{ album.artist }}
                                <span class="details-count">({{ album.year }})</span>
                                <span v-if="activeYoutubeAlbum === album.name"> ✕</span>
                            </button>
                        </li>
                    </ul>
                </div>
                <div class="video-iframe-wrap" :class="{ 'is-open': youtubeOpen }" ref="youtubeContainer"></div>
                <hr />
                <div class="detailspanel-section preview">
                    <h3>Check out the Vibes</h3>
                    <div class="player-wrap" :class="isPlaying ? 'playing' : null">
                        <button @click="handleRecordClick(genreData.sample_tracks[0]?.artist)" :disabled="isAudioLoading || isPlaying">
                            {{ currentTrackName || 'Play Sample Track' }}
                        </button>
                        <button v-if="isAudioLoading || isPlaying" @click="stopAudio" class="stop-btn">
                            {{ isAudioLoading ? 'Loading...' : 'Stop' }}
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
            <br />
        </div>
    </div>
</template>

<script setup>
import { ref, watch, computed, nextTick } from 'vue'
import genreDescriptions from '../api/genre_descriptions.json'

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

const formattedGenre = computed(() => {
    if (!props.genre) return ''
    return props.genre.split(' ').map(word => word ? word[0].toUpperCase() + word.substring(1) : '').join(' ')
})

const genreDescription = computed(() => {
    if (!props.genre) return ''

    const lookupKey = Object.keys(genreDescriptions).find(
        k => k.toLowerCase() === props.genre.toLowerCase()
    )
    
    return lookupKey ? genreDescriptions[lookupKey] : ''
})

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

const isPlaying = ref(false)
const isAudioLoading = ref(false)
const currentTrackName = ref(null)

const formatTrackName = (url) => {
    let path = url;
    if (path.includes('/items/')) {
        path = path.split('/items/')[1];
    } else if (path.includes('/download/')) {
        path = path.split('/download/')[1];
    }
    
    path = path.replace(/\.[a-zA-Z0-9]+$/, '');
    path = decodeURIComponent(path);
    path = path.replace(/[-/]/g, ' ');
    path = path.replace(/\s+/g, ' ').trim();
    
    return path.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

const handleRecordClick = async (name) => {
    isAudioLoading.value = true;
    const url = await getAudioUrl(name);
    
    if (!isAudioLoading.value) return; 

    if (url) {
        currentTrackName.value = formatTrackName(url);
        const audio = document.getElementById('samplePlayer');
        
        audio.oncanplaythrough = null;
        audio.onended = null;
        audio.onerror = null;

        audio.src = url;
        audio.play().then(() => {
            if (!isAudioLoading.value) { 
                audio.pause();
                return;
            }
            isAudioLoading.value = false;
            isPlaying.value = true;
            audio.classList.add('playing');
        }).catch(err => {
            isAudioLoading.value = false;
            isPlaying.value = false;
            console.error("Error playing audio.", err);
        });

        audio.onended = () => {
            isPlaying.value = false;
            currentTrackName.value = null;
            audio.classList.remove('playing');
        };
    } else {
        isAudioLoading.value = false;
        currentTrackName.value = null;
        console.log("No audio found for " + name);
    }
}

const stopAudio = () => {
    isAudioLoading.value = false;
    isPlaying.value = false;
    currentTrackName.value = null;
    
    const audio = document.getElementById('samplePlayer');
    if (audio) {
        audio.pause();
        audio.removeAttribute('src'); 
        audio.load();
        audio.classList.remove('playing');
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

const wikiOpen = ref(false)
const wikiLoading = ref(false)
const wikiContainer = ref(null)
const activeWikiArtist = ref(null)
const artistLinks = ref({})

const youtubeOpen = ref(false)
const youtubeContainer = ref(null)
const activeYoutubeAlbum = ref(null)

const closeYoutube = () => {
	youtubeContainer.value.innerHTML = ''
	youtubeOpen.value = false
	activeYoutubeAlbum.value = null
}

const openYoutube = (albumName, artist) => {
	if (activeYoutubeAlbum.value === albumName) {
		closeYoutube()
		return
	}

	activeYoutubeAlbum.value = albumName
	youtubeOpen.value = true

	setTimeout(() => {
		const scrollParent = youtubeContainer.value?.closest('.details-area')
		const albumsSection = scrollParent?.querySelector('.detailspanel-section.albums ul')
		if (scrollParent && albumsSection) {
			scrollParent.scrollTo({
                top: albumsSection.offsetTop - 20,
                behavior: 'smooth'
            })
		}
	}, 50)

	const query = encodeURIComponent(`${albumName} ${artist}`)
	const iframe = document.createElement('iframe')
	iframe.src = `https://www.bing.com/videos/riverview/relatedvideo?q=${query}+album`
	iframe.style.cssText = 'width:100%;height:500px;border:none;'
	iframe.allowFullscreen = true
	youtubeContainer.value.innerHTML = ''
	youtubeContainer.value.appendChild(iframe)
}

const fetchWikipediaLink = async (artistName) => {
    if (artistLinks.value[artistName]) return;

    try {
        const searchUrl = `https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(artistName + ' artist')}&srlimit=1&format=json&origin=*`;
        const res = await fetch(searchUrl);
        const data = await res.json();
        const results = data.query?.search;

        if (results && results.length > 0) {
            const title = results[0].title.replace(/ /g, '_');
            artistLinks.value[artistName] = `https://en.m.wikipedia.org/wiki/${title}`;
        } else {
            artistLinks.value[artistName] = '#';
        }
    } catch (error) {
        console.error("Wikipedia fetch error", error);
        artistLinks.value[artistName] = '#';
    }
}

const closeWiki = () => {
	wikiContainer.value.innerHTML = ''
	wikiOpen.value = false
	wikiLoading.value = false
	activeWikiArtist.value = null
}

const openWiki = async (name) => {
	if (!name) return

	if (activeWikiArtist.value === name) {
		closeWiki()
		return
	}

	wikiOpen.value = true
	wikiLoading.value = true
	activeWikiArtist.value = name

	setTimeout(() => {
		const scrollParent = wikiContainer.value?.closest('.details-area')
		const wikiSection = scrollParent?.querySelector('.detailspanel-section.wiki ul')
		if (scrollParent && wikiSection) {
			scrollParent.scrollTo({
				top: wikiSection.offsetTop - 20,
				behavior: 'smooth'
			})
		}
	}, 50)

	const bar = document.createElement('div')
	bar.className = 'wiki-progress-bar'
	wikiContainer.value.innerHTML = ''
	wikiContainer.value.appendChild(bar)

	await fetchWikipediaLink(name)
	const pageUrl = artistLinks.value[name]
	if (!pageUrl || pageUrl === '#') {
		wikiOpen.value = false
		wikiLoading.value = false
		activeWikiArtist.value = null
		return
	}

	const iframe = document.createElement('iframe')
    setTimeout(() => {
        iframe.src = pageUrl
        iframe.style.cssText = 'width:100%;height:600px;border:none;'
        iframe.addEventListener('load', () => {
            bar.remove()
            wikiLoading.value = false
        })
        wikiContainer.value.appendChild(iframe)
    }, 50)
}

watch([() => props.genre, () => props.year], loadDecadeData, { immediate: true })
</script>
