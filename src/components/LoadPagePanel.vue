<template>
    <div class="load-page-panel">
        <h2>Welcome to genregraphy!</h2>
        <div class="loadpanel-section">
            <p>Genregraphy is a music genre visualization tool that allows you to explore the evolution of music genres across the world from 1950 to 2025.</p>
        </div>
        <div class="loadpanel-section">
            <button @click="$emit('loaded', true)">Load the map</button>
        </div>
        <div class="loadpanel-section">
            <p>Click on the map to learn more about each genre and its history</p>
        </div>
    </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playwrite+CO+Guides&text=Welcome%20to%20Genregraphy!&display=swap');

h2 {
    font-family: 'Playwrite CO Guides', cursive;
}
</style>