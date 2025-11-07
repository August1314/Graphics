<template>
  <div id="app" class="app-container">
    <h1>Native Drawing App</h1>
    <p>Cross-platform drawing application with C++ rendering engine</p>
    <p class="status">Status: Project initialized ✓</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';

onMounted(() => {
  console.log('Native Drawing App initialized');
});
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, sans-serif;
}

h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

p {
  color: #666;
  margin: 0.25rem 0;
}

.status {
  margin-top: 2rem;
  padding: 0.5rem 1rem;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 4px;
  font-weight: 500;
}
</style>
