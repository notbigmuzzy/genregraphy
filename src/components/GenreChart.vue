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

const years = [1950,1951,1952,1953,1954,1955,1956,1957,1958,1959,1960,1961,1962,1963,1964,1965,1966,1967,1968,1969,1970,1971,1972,1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010, 2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025];
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
