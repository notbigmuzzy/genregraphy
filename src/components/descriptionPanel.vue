<template>
	<div class="description-panel" :class="props.isDescriptionVisible ? 'visible' : 'hidden'">
		<button
			class="close-button"
			@click="hideDescription"
		>-></button>
		<div class="scrollable-area" v-show="!wikiUrl">
			<div class="panel-text-block">
				<p v-if="props.content?.isPeak">
					<strong>Peak year for this Genre !!!</strong>
					<br/>
				</p>
				<h2 class="uppercase">{{ props.content?.genreName }}</h2>
				<hr/>
				<p><strong>Part of:</strong> {{ props.content?.genre_group }}</p>
				<p><strong>Year:</strong> {{ props.content?.year }}</p>
				<hr/>
				<p class="description">
					Lorem ipsum dolor sit amet consectetur adipisicing elit.
					Quidem molestiae eius aliquid, quod laudantium recusandae aliquam voluptatibus.
					Lure aspernatur quis corrupti ex alias ipsam minus similique maxime perspiciatis maiores! Laudantium?
					<br/><br/>
					Additional information about
					<strong>{{ props.content?.genreName }}</strong>
					in
					<strong>{{ props.content?.year }}</strong>
					on
					<strong>{{ props.content?.genre_group }}</strong>
					can be placed here.
				</p>
				<hr/>
				<div v-if="props.content?.detailedData" class="section">
					<b>
						Notable Artists in
						<span class="uppercase">
							{{ props.content?.genreName }}
						</span>
							for the {{ props.content?.decade }}s
					</b>
					<ul v-if="props.content?.detailedData?.top_artists">
						<li v-for="artist in props.content.detailedData.top_artists" :key="artist.name">
							{{ artist.name }} - 
							<a :href="artistLinks[artist.name] || '#'" @click.prevent="openWiki(artistLinks[artist.name])" title="Wikipedia" class="wiki-link">
								<i>Wikipedia page</i>
							</a>
						</li>
					</ul>
				</div>
				<hr/>
				<div v-if="props.content?.detailedData" class="section">
					<b>
						Popular Albums for genre
						<span class="uppercase">
							{{ props.content?.genreName }}
						</span>
							in the {{ props.content?.decade }}s
					</b>
					<ul v-if="props.content?.detailedData?.top_albums">
						<li v-for="album in props.content.detailedData.top_albums" :key="album.name">
							<strong>{{ album.name }}</strong> - {{ album.artist }} ({{ album.year }})
						</li>
					</ul>
				</div>
				<hr/>
				<p class="group">
					<button @click="handleRecordClick(props.content?.detailedData?.sample_tracks[0]?.artist)">
						Play Sample Track
					</button>
					<audio controls id="sample-player">
						<source src="#" type="audio/mpeg">
						Your browser does not support the audio element.
					</audio>
				</p>
			</div>
		</div>
		<div class="iframe-panel" v-if="wikiUrl">
			<button
				class="close-button iframe-close"
				@click="hideIframe"
			>BACK</button>
			<div v-if="iframeLoading" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white;">
				Loading...
			</div>
			<iframe :src="wikiUrl" style="width:100%; height:100%; border:none;" @load="iframeLoading = false" />
		</div>
	</div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
	isDescriptionVisible: {
		type: Boolean,
		required: false
	},
	content: {
		type: Object,
		required: false
	}
})

const emit = defineEmits(['update:isDescriptionVisible'])

const wikiUrl = ref(null)
const iframeLoading = ref(false)

const openWiki = (url) => {
	if (url && url !== '#') {
		wikiUrl.value = url.replace('.wikipedia.org', '.m.wikipedia.org')
		iframeLoading.value = true
	}
}

const hideIframe = () => {
	wikiUrl.value = null
	iframeLoading.value = false
}

const hideDescription = () => {
	wikiUrl.value = null
	iframeLoading.value = false
	document.getElementById('sample-player').src = "#";
	document.querySelector('.scrollable-area').scrollTop = 0;
	document.getElementById('sample-player').classList.remove('playing');
	emit('update:isDescriptionVisible', false);
};

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

const getGenreAudioUrl = async (genre) => {
    try {

        const query = encodeURIComponent(`${genre} music`);
        const searchUrl = `https://archive.org/advancedsearch.php?q=${query}+AND+mediatype%3A(audio)&fl[]=identifier&sort[]=downloads+desc&output=json`;

        const searchRes = await fetch(searchUrl);
        const searchData = await searchRes.json();
        const docs = searchData.response.docs;

        if (!docs || docs.length === 0) return null;

        const identifier = docs[0].identifier;

        const metaUrl = `https://archive.org/metadata/${identifier}`;
        const metaRes = await fetch(metaUrl);
        const metaData = await metaRes.json();
        const mp3File = metaData.files.find(f => f.name.endsWith('.mp3'));

        if (mp3File) {
            return `https://archive.org/download/${identifier}/${mp3File.name}`;
        }
        
        return null;
    } catch (error) {
        console.error("No sample for this Genre", error);
        return null;
    }
}

const artistLinks = ref({});
const fetchWikipediaLink = async (artistName) => {
    if (artistLinks.value[artistName]) return;

    try {
        const searchTerm = encodeURIComponent(artistName + " music band");
        const url = `https://en.wikipedia.org/w/api.php?action=opensearch&search=${searchTerm}&limit=1&namespace=0&format=json&origin=*`;
        const response = await fetch(url);
        const data = await response.json();

        if (data[3] && data[3].length > 0) {
            artistLinks.value[artistName] = data[3][0];
        } else {
            const simpleSearch = encodeURIComponent(artistName);
            const simpleUrl = `https://en.wikipedia.org/w/api.php?action=opensearch&search=${simpleSearch}&limit=1&namespace=0&format=json&origin=*`;
            const simpleRes = await fetch(simpleUrl);
            const simpleData = await simpleRes.json();
            
             if (simpleData[3] && simpleData[3].length > 0) {
                artistLinks.value[artistName] = simpleData[3][0];
            } else {
                artistLinks.value[artistName] = '#';
            }
        }
    } catch (error) {
        console.error("Wikipedia fetch error", error);
        artistLinks.value[artistName] = '#';
    }
}

watch(() => props.content, (newVal) => {
    if (newVal?.detailedData?.top_artists) {
        newVal.detailedData.top_artists.forEach(artist => {
            fetchWikipediaLink(artist.name);
        });
    }
}, { immediate: true });

const handleRecordClick = async (name) => {
    const url = await getAudioUrl(name);
    if (url) {
        const audio = document.getElementById('sample-player');
        audio.src = url;
        audio.play();
		audio.classList.add('playing');
    } else {
        console.log("No audio found for " + name);
    }
}

</script>