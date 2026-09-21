<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'

const router = useRouter()
const query = ref('')

function search() {
  const value = query.value.trim()
  if (value) {
    router.push({ name: 'search', query: { q: value } })
  }
}
</script>

<template>
  <header class="site-header">
    <div class="header-content">
      <RouterLink class="brand" to="/">
        <span>Shape<span class="brand-accent">find</span></span>
      </RouterLink>

      <form class="header-search" role="search" @submit.prevent="search">
        <span class="search-icon" aria-hidden="true">⌕</span>
        <input
          v-model="query"
          type="search"
          placeholder="Rechercher un modèle 3D..."
          aria-label="Rechercher un modèle 3D"
        />
        <button type="submit">Rechercher</button>
      </form>

      <nav aria-label="Navigation principale">
        <RouterLink to="/">Accueil</RouterLink>
        <a href="#catalogue">Catalogue</a>
      </nav>
    </div>
  </header>

  <RouterView />
</template>
