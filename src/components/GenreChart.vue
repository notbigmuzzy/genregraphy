<template>
  <div class="genre-chart">
    <div class="controls">
      <label for="genre-select">Izaberi žanr:</label>
      <select id="genre-select" v-model="selectedGenre">
        <option v-for="genre in allGenres" :key="genre" :value="genre">
          {{ genre }}
        </option>
      </select>
    </div>

    <div class="chart">
      <div class="y-axis">
        <div class="y-label">1000</div>
        <div class="y-label">750</div>
        <div class="y-label">500</div>
        <div class="y-label">250</div>
        <div class="y-label">0</div>
      </div>
      <div class="bars">
        <div v-for="year in years" :key="year" class="chart-column">
          <div class="bar-container">
            <div 
              class="bar" 
              :style="{ height: getBarHeight(year) + '%' }"
              :title="`${year}: ${getCount(year)} albuma`"
            >
              <span class="count">{{ getCount(year) }}</span>
            </div>
          </div>
          <div class="year-label">{{ year }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import genresData from '../api/genres.json';

const years = [1995, 1996, 1997, 1998, 1999, 2000];
const selectedGenre = ref('rock');
const genreData = ref(genresData);
const allGenres = ref([]);

// Napravi listu svih žanrova
onMounted(() => {
  const genresSet = new Set();
  Object.values(genresData).forEach(yearData => {
    Object.values(yearData).forEach(groupData => {
      Object.keys(groupData).forEach(genre => {
        genresSet.add(genre);
      });
    });
  });
  allGenres.value = Array.from(genresSet).sort();
});

// Nađi count za izabrani žanr i godinu
const getCount = (year) => {
  const yearData = genreData.value[year];
  if (!yearData) return 0;
  
  for (const groupData of Object.values(yearData)) {
    if (groupData[selectedGenre.value] !== undefined) {
      return groupData[selectedGenre.value];
    }
  }
  return 0;
};

// Izračunaj visinu bara (maksimum 1000 = 100%)
const getBarHeight = (year) => {
  const count = getCount(year);
  return Math.min((count / 1000) * 100, 100);
};
</script>

<style scoped>
.genre-chart {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.controls {
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

label {
  font-weight: 600;
  font-size: 1rem;
  color: #333;
}

select {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  border: 2px solid #333;
  border-radius: 4px;
  background: white;
  color: #333;
  cursor: pointer;
  min-width: 200px;
}

select:hover {
  border-color: #666;
}

select:focus {
  outline: none;
  border-color: #667eea;
}

.chart {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 400px;
  padding-right: 0.5rem;
}

.y-label {
  font-size: 0.8rem;
  color: #666;
  text-align: right;
}

.bars {
  display: flex;
  gap: 2rem;
  align-items: flex-end;
  flex: 1;
}

.chart-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.bar-container {
  width: 100%;
  height: 400px;
  background: #f0f0f0;
  border-radius: 4px 4px 0 0;
  position: relative;
  display: flex;
  align-items: flex-end;
}

.bar {
  width: 100%;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 0.5rem;
  transition: height 0.3s ease;
  border-radius: 4px 4px 0 0;
  min-height: 30px;
}

.count {
  color: white;
  font-weight: 600;
  font-size: 0.85rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.year-label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #333;
}
</style>
