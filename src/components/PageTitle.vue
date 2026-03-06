<template>
    <div class="left-titlebar">
        <div class="options-menu-wrapper">
            <button>☰</button>
            <ul class="options-menu">
                <li>
                    <label class="toggle-label">
                        <span>Show genre names</span>
                        <div class="toggle-switch">
                            <input name="show-genre-names" type="checkbox" :checked="options.genreNames" @change="$emit('update:option', 'genreNames', $event.target.checked)"/>
                            <span class="slider round"></span>
                        </div>
                    </label>
                </li>
                <li>
                    <label class="toggle-label">
                        <span>Show genre groups</span>
                        <div class="toggle-switch">
                            <input name="show-genre-groups" type="checkbox" :checked="options.groupNames" @change="$emit('update:option', 'groupNames', $event.target.checked)"/>
                            <span class="slider round"></span>
                        </div>
                    </label>
                </li>
            </ul>
        </div>
        <h1>
            <span>Genregraphy</span>
        </h1>
    </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
    options: {
        type: Object,
        required: true
    }
})

defineEmits(['update:option'])
</script>