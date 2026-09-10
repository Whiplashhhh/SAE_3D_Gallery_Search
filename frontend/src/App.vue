<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterView } from 'vue-router'
import './App.css'

const modeSombre = ref(false)

onMounted(() => {
  modeSombre.value = localStorage.getItem('theme') === 'dark'
})

function basculerTheme() {
  modeSombre.value = !modeSombre.value
  localStorage.setItem('theme', modeSombre.value ? 'dark' : 'light')
}
</script>

<template>
  <div class="app-shell" :class="{ 'dark-theme': modeSombre }">
    <header class="topbar">
      <div class="brand">
        <span class="brand-mark">3D</span>
        <div>
          <h1>3D Gallery Search</h1>
          <p>Recherche sémantique de modèles 3D</p>
        </div>
      </div>

      <button
        class="theme-toggle"
        type="button"
        :aria-label="modeSombre ? 'Activer le mode clair' : 'Activer le mode sombre'"
        @click="basculerTheme"
      >
        {{ modeSombre ? 'Mode clair' : 'Mode sombre' }}
      </button>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>
