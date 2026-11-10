<script setup lang="ts">
import { defineAsyncComponent, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getModel, getModelFile, type GalleryModelDetail } from '../services/galleryApi'
import './ModelDetailView.css'

const ModelViewer = defineAsyncComponent(() => import('../components/ModelViewer.vue'))

const route = useRoute()
const model = ref<GalleryModelDetail | null>(null)
const modelFile = ref<File | null>(null)
const loading = ref(true)
const error = ref('')
const previewError = ref('')
let requestGeneration = 0

async function loadModel(id: string) {
  const generation = ++requestGeneration
  model.value = null
  modelFile.value = null
  loading.value = true
  error.value = ''
  previewError.value = ''

  try {
    const detail = await getModel(id)
    if (generation !== requestGeneration) return
    model.value = detail

    if (detail.fichier_3d_disponible) {
      try {
        const file = await getModelFile(id)
        if (generation === requestGeneration) modelFile.value = file
      } catch (cause) {
        if (generation === requestGeneration) {
          previewError.value =
            cause instanceof Error ? cause.message : 'Impossible de charger le fichier 3D.'
        }
      }
    }
  } catch (cause) {
    if (generation === requestGeneration) {
      error.value = cause instanceof Error ? cause.message : 'Impossible de charger ce modèle.'
    }
  } finally {
    if (generation === requestGeneration) loading.value = false
  }
}

watch(
  () => route.params.id,
  (id) => {
    if (typeof id === 'string') void loadModel(id)
  },
  { immediate: true },
)
</script>

<template>
  <main class="model-detail-page">
    <div class="model-detail-container">
      <RouterLink class="detail-back-link" :to="{ name: 'search', query: { q: '' } }">
        ← Retour au catalogue
      </RouterLink>

      <p v-if="loading" class="detail-status" role="status">Chargement du modèle...</p>
      <section v-else-if="error" class="detail-status detail-error" role="alert">
        <h1>Modèle indisponible</h1>
        <p>{{ error }}</p>
      </section>

      <article v-else-if="model" class="model-detail">
        <header class="detail-header">
          <div>
            <p class="eyebrow">{{ model.category }}</p>
            <h1>{{ model.title }}</h1>
            <p class="detail-description">{{ model.description }}</p>
          </div>
          <span class="detail-state">{{ model.fichier_3d_disponible ? 'Aperçu 3D' : 'Fiche modèle' }}</span>
        </header>

        <section
          v-if="model.fichier_3d_disponible"
          class="detail-preview"
          aria-labelledby="preview-title"
        >
          <h2 id="preview-title">Modèle 3D</h2>
          <ModelViewer v-if="modelFile" :file="modelFile" />
          <p v-else-if="previewError" class="detail-status detail-error" role="alert">
            {{ previewError }}
          </p>
          <p v-else class="detail-status" role="status">Chargement de l’aperçu 3D...</p>
        </section>

        <section class="detail-section" aria-labelledby="views-title">
          <h2 id="views-title">Descriptions par vue</h2>
          <div class="view-description-list">
            <article v-for="view in model.par_vue" :key="view.nom" class="view-description">
              <h3>{{ view.nom }}</h3>
              <p>{{ view.description }}</p>
            </article>
          </div>
        </section>

        <section class="detail-section" aria-labelledby="divergences-title">
          <h2 id="divergences-title">Divergences entre les vues</h2>
          <ul v-if="model.divergences_entre_vues.length">
            <li v-for="(divergence, index) in model.divergences_entre_vues" :key="index">
              {{ divergence }}
            </li>
          </ul>
          <p v-else class="detail-muted">Aucune divergence signalée entre les vues.</p>
        </section>
      </article>
    </div>
  </main>
</template>
