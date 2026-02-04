<template>
	<div class="description-panel" :class="props.isDescriptionVisible ? 'visible' : 'hidden'">
		<button
			class="close-button"
			@click="hideDescription"
		>-></button>
		<div class="scrollable-area">
			<div class="panel-text-block">
				<p v-if="props.content?.isPeak">
					<strong>Peak year for this Genre !!!</strong>
					<br/>
				</p>
				<h2 class="uppercase">{{ props.content?.genreName }}</h2>
				<hr/>
				<p><strong>Part of:</strong> {{ props.content?.continent }}</p>
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
					<strong>{{ props.content?.continent }}</strong>
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
							{{ artist.name }} - Wikipedia page <a :href="'https://en.wikipedia.org/w/api.php?action=opensearch&search=' + encodeURIComponent(artist.name) + '+Band&limit=1&namespace=0&format=json'" target="_blank">(link)</a>
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
				<p>
					<b>Sample Track from Top Album</b>
				</p>
				<p>
					<button @click="handleRecordClick('beatles')">
						Play Sample for Genre {{ props.content?.genreName }} from year {{ props.content?.year }}
					</button>
				</p>
				<audio controls id="sample-player">
					<source src="#" type="audio/mpeg">
					Your browser does not support the audio element.
				</audio>
			</div>
		</div>
	</div>
</template>

<script setup>

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

const hideDescription = () => {
	document.getElementById('sample-player').src = "#";
	document.querySelector('.scrollable-area').scrollTop = 0;
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

const handleRecordClick = async (name) => {
    const url = await getAudioUrl(name);
    if (url) {
        const audio = document.getElementById('sample-player');
        audio.src = url;
        audio.play();
    } else {
        alert("No audio found for " + name);
    }
}


</script>