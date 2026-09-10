<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { products, searchProducts } from '../data/products'

const route = useRoute()
const router = useRouter()
const query = ref(typeof route.query.q === 'string' ? route.query.q : '')

watch(
  () => route.query.q,
  (value) => {
    query.value = typeof value === 'string' ? value : ''
  },
)

const results = computed(() => searchProducts(query.value))

function search() {
  router.push({ name: 'search', query: { q: query.value.trim() } })
}
</script>

<template>
  <main class="results-page">
    <div class="results-container">
      <div class="results-top">
        <div>
          <p class="eyebrow">CATALOGUE 3D</p>
          <h1 v-if="query">Résultats pour <em>« {{ query }} »</em></h1>
          <h1 v-else>Tous les modèles</h1>
        </div>
        <form class="results-search" role="search" @submit.prevent="search">
          <span class="search-icon" aria-hidden="true">⌕</span>
          <input v-model="query" type="search" aria-label="Modifier la recherche" />
          <button type="submit">Rechercher</button>
        </form>
      </div>

      <div class="results-meta">
        <span>{{ results.length }} modèle{{ results.length > 1 ? 's' : '' }} trouvé{{ results.length > 1 ? 's' : '' }}</span>
        <span class="sort-label">Triés par pertinence <span aria-hidden="true">⌄</span></span>
      </div>

      <div v-if="results.length" class="product-grid results-grid">
        <article v-for="product in results" :key="product.id" class="product-card">
          <div class="product-image" :style="{ '--product-color': product.color }">
            <span>{{ product.emoji }}</span>
            <small>{{ product.category }}</small>
          </div>
          <div class="product-info">
            <div>
              <h2>{{ product.title }}</h2>
              <p>{{ product.description }}</p>
              <div class="tags">
                <span v-for="tag in product.tags" :key="tag">{{ tag }}</span>
              </div>
            </div>
            <span class="match-score">{{ product.score }}%</span>
          </div>
        </article>
      </div>

      <div v-else class="empty-state">
        <span class="empty-icon" aria-hidden="true">⌕</span>
        <h2>Aucun modèle trouvé</h2>
        <p>Essayez une autre description ou recherchez par catégorie, couleur ou objet.</p>
        <button @click="query = ''; search()">Voir tous les modèles</button>
      </div>
    </div>
  </main>
</template>
