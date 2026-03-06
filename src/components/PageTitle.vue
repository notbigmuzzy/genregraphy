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
    </div>
</template>

<script setup>
const props = defineProps({
    options: {
        type: Object,
        required: true
    }
})

defineEmits(['update:option'])
</script>