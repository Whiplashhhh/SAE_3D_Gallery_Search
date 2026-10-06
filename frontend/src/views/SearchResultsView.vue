<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { deleteModel, searchModels, type GalleryModel } from '../services/galleryApi'

const route = useRoute()
const router = useRouter()
const query = ref(typeof route.query.q === 'string' ? route.query.q : '')
const results = ref<GalleryModel[]>([])
const loading = ref(false)
const error = ref('')
const deletingId = ref('')

function escapeHtml(value: string) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

function highlighted(value: string) {
  const escapedValue = escapeHtml(value)
  const terms = query.value
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map((term) => escapeHtml(term).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))

  if (!terms.length) return escapedValue
  return escapedValue.replace(new RegExp(`(${terms.join('|')})`, 'gi'), '<mark>$1</mark>')
}

async function loadResults(value: string) {
  loading.value = true
  error.value = ''
  try {
    results.value = await searchModels(value)
  } catch (cause) {
    results.value = []
    error.value = cause instanceof Error ? cause.message : 'Impossible de charger les résultats.'
  } finally {
    loading.value = false
  }
}

watch(
  () => route.query.q,
  (value) => {
    query.value = typeof value === 'string' ? value : ''
    void loadResults(query.value)
  },
  { immediate: true },
)

function search() {
  router.push({ name: 'search', query: { q: query.value.trim() } })
}

async function removeModel(model: GalleryModel) {
  if (!window.confirm(`Supprimer « ${model.title} » ? Cette action est définitive.`)) return

  deletingId.value = model.id
  error.value = ''
  try {
    await deleteModel(model.id)
    results.value = results.value.filter((item) => item.id !== model.id)
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Impossible de supprimer le modèle.'
  } finally {
    deletingId.value = ''
  }
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
        <span v-if="loading">Chargement des résultats...</span>
        <span v-else>{{ results.length }} modèle{{ results.length > 1 ? 's' : '' }} trouvé{{ results.length > 1 ? 's' : '' }}</span>
        <span class="sort-label">Triés par pertinence <span aria-hidden="true">⌄</span></span>
      </div>

      <p v-if="error" class="catalogue-status catalogue-error">{{ error }}</p>
      <div v-else-if="!loading && results.length" class="product-grid results-grid">
        <article v-for="product in results" :key="product.id" class="product-card">
          <div class="product-image" :style="{ '--product-color': product.color }">
            <span>{{ product.emoji }}</span>
            <small>{{ product.category }}</small>
          </div>
          <div class="product-info">
            <div>
              <h2 v-html="highlighted(product.title)"></h2>
              <p v-html="highlighted(product.description)"></p>
              <div class="tags">
                <span v-for="tag in product.tags" :key="tag" v-html="highlighted(tag)"></span>
              </div>
              <button
                class="delete-model-button"
                type="button"
                :disabled="deletingId === product.id"
                @click="removeModel(product)"
              >
                {{ deletingId === product.id ? 'Suppression...' : 'Supprimer' }}
              </button>
            </div>
            <span v-if="product.score !== undefined" class="match-score">
              {{ Math.round(product.score * 100) }}%
            </span>
          </div>
        </article>
      </div>

      <div v-else-if="!loading" class="empty-state">
        <span class="empty-icon" aria-hidden="true">⌕</span>
        <h2>Aucun modèle trouvé</h2>
        <p>Essayez une autre description ou recherchez par catégorie, couleur ou objet.</p>
        <button @click="query = ''; search()">Voir tous les modèles</button>
      </div>
    </div>
  </main>
</template>
