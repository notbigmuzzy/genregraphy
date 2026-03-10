<template>
    <div class="left-titlebar">
        <div class="options-menu-wrapper">
            <button>☰</button>
            <ul class="options-menu">
                <li>
                    <label class="toggle-label">
                        <span>Main Categories</span>
                        <div class="toggle-switch">
                            <input
                                name="show-genre-groups"
                                type="checkbox"
                                :checked="options.groupNames"
                                @click="options.groupNames ? $event.preventDefault() : null"
                                @change="$emit('update:option', 'groupNames', true)"
                            />
                            <span class="slider round"></span>
                        </div>
                    </label>
                </li>
                <li>
                    <label class="toggle-label">
                        <span>All Subgenres</span>
                        <div class="toggle-switch">
                            <input
                                name="show-genre-names"
                                type="checkbox"
                                :checked="options.genreNames"
                                @click="options.genreNames ? $event.preventDefault() : null"
                                @change="$emit('update:option', 'genreNames', true)"
                            />
                            <span class="slider round"></span>
                        </div>
                    </label>
                </li>
            </ul>
        </div>
        <h1>
            <span>Genregraphy</span>
        </h1>
        <div class="options-about-wrapper">
            <button>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
            </button>
            <div class="options-about-menu">
                <div class="about-section">
                    <p>
                        Created with 🎼 by <a href="https://notbigmuzzy.github.io" target="_blank" rel="noopener noreferrer">NBM</a>
                    </p>
                    <hr />
                    <p>
                        Data sourced from <a href="https://musicbrainz.org/doc/MusicBrainz_API" target="_blank" rel="noopener noreferrer">MusicBrainz API</a>
                    </p>
                    <hr />
                    <p>
                        <button @click="showStatsScreen">Album / Genre Stats</button>
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
const props = defineProps({
    options: {
        type: Object,
        required: true
    }
})

const emit = defineEmits(['update:option', 'showStats'])

const showStatsScreen = () => {
    emit('showStats', true);
}

</script>