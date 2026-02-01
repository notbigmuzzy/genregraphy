<template>
  <div class="genre-chart">
    <div class="controls">
      <label for="group-select">Izaberi grupu:</label>
      <select id="group-select" v-model="selectedGroup">
        <option v-for="group in allGroups" :key="group" :value="group">
          {{ group }}
        </option>
      </select>
    </div>

    <div class="chart">
      <div class="y-axis">
        <div class="y-label">1200</div>
        <div class="y-label">900</div>
        <div class="y-label">600</div>
        <div class="y-label">300</div>
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
import { ref, onMounted } from 'vue';
import genresData from '../api/genres.json';

const years = [1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010];
const selectedGroup = ref('The Rock Shield');
const genreData = ref(genresData);
const allGroups = ref([]);

onMounted(() => {
  const groupsSet = new Set();
  Object.values(genresData).forEach(yearData => {
    Object.keys(yearData).forEach(group => {
      groupsSet.add(group);
    });
  });
  allGroups.value = Array.from(groupsSet).sort();
});

const getCount = (year) => {
  const yearData = genreData.value[year];
  if (!yearData) return 0;
  
  const groupData = yearData[selectedGroup.value];
  if (!groupData) return 0;
  
  return Object.values(groupData).reduce((sum, count) => sum + count, 0);
};

const getBarHeight = (year) => {
  const count = getCount(year);
  return Math.min((count / 1200) * 100, 100);
};
</script>
