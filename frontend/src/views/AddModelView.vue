<script setup lang="ts">
import { computed, defineAsyncComponent, ref } from 'vue'
import { uploadModel } from '../services/galleryApi'
import './AddModelView.css'

const ModelViewer = defineAsyncComponent(() => import('../components/ModelViewer.vue'))

const acceptedFormats = ['.obj', '.gltf', '.stl']
const acceptedResourceFormats = ['.bin', '.mtl', '.png', '.jpg', '.jpeg', '.webp']
const selectedFiles = ref<File[]>([])
const uploading = ref(false)
const uploaded = ref(false)
const dragging = ref(false)
const error = ref('')
const success = ref('')

const selectedFile = computed(
  () =>
    selectedFiles.value.find((file) =>
      acceptedFormats.includes(`.${file.name.split('.').pop()?.toLocaleLowerCase()}`),
    ) || null,
)
const supportingFiles = computed(() =>
  selectedFiles.value.filter((file) => file !== selectedFile.value),
)
const fileLabel = computed(() => selectedFile.value?.name || 'Choisir un fichier 3D')

function setSelectedFiles(files: File[]) {
  error.value = ''
  success.value = ''
  uploaded.value = false

  const modelFile = files.find((file) =>
    acceptedFormats.includes(`.${file.name.split('.').pop()?.toLocaleLowerCase()}`),
  )
  if (!modelFile) {
    selectedFiles.value = []
    error.value = 'Sélectionnez un fichier .obj, .gltf ou .stl.'
    return
  }
  selectedFiles.value = [modelFile, ...files.filter((file) => file !== modelFile)]
}

function handleSelection(event: Event) {
  const input = event.target as HTMLInputElement
  setSelectedFiles(Array.from(input.files || []))
  input.value = ''
}

function handleDrop(event: DragEvent) {
  dragging.value = false
  if (event.dataTransfer?.files.length) {
    setSelectedFiles(Array.from(event.dataTransfer.files))
  }
}

/**
 * Envoie le modèle puis indique qu'il reste à traiter par les Lots A et B
 * avant que le Lot C puisse l'indexer et le rendre recherchable.
 */
async function submit() {
  if (!selectedFile.value) {
    error.value = 'Sélectionnez un fichier .obj, .gltf ou .stl.'
    return
  }

  uploading.value = true
  error.value = ''
  success.value = ''
  try {
    const model = await uploadModel(selectedFile.value)
    success.value = `${model.nom} a été ajouté. Il apparaîtra dans le catalogue après la génération de sa fiche par les Lots A et B.`
    uploaded.value = true
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "Impossible d'ajouter le modèle."
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <main class="add-model-page">
    <section class="add-model-card">
      <div class="add-model-intro">
        <p class="eyebrow">NOUVEAU MODÈLE</p>
        <h1>Ajoutez un modèle <em>à la galerie.</em></h1>
        <p>
          Importez un fichier 3D pour le transmettre au pipeline de la galerie. Le fichier sera
          ensuite traité par les Lots A et B avant de devenir recherchable.
        </p>
      </div>

      <form class="upload-form" @submit.prevent="submit">
        <label
          class="drop-zone"
          :class="{ 'drop-zone-active': dragging }"
          for="model-file"
          @dragover.prevent="dragging = true"
          @dragleave.prevent="dragging = false"
          @drop.prevent="handleDrop"
        >
          <span class="upload-icon" aria-hidden="true">↥</span>
          <strong>{{ fileLabel }}</strong>
          <small>Déposez votre modèle ou cliquez ici · OBJ, GLTF, STL · 50 Mo maximum</small>
          <small v-if="selectedFiles.length > 1">
            {{ supportingFiles.length }} fichier(s) associé(s) sélectionné(s) pour l’aperçu
          </small>
          <input
            id="model-file"
            type="file"
            :accept="[...acceptedFormats, ...acceptedResourceFormats].join(',')"
            multiple
            @change="handleSelection"
          />
        </label>

        <button
          class="upload-button"
          type="submit"
          :disabled="uploading || uploaded || !selectedFile"
        >
          {{ uploading ? 'Ajout en cours...' : uploaded ? 'Modèle ajouté' : 'Ajouter le modèle' }}
        </button>

        <p v-if="error" class="upload-message upload-error" role="alert">{{ error }}</p>
        <p v-if="success" class="upload-message upload-success" role="status">{{ success }}</p>
      </form>

      <section v-if="selectedFile" class="preview-section" aria-labelledby="preview-heading">
        <div class="preview-heading">
          <div>
            <p class="eyebrow">APERÇU LOCAL</p>
            <h2 id="preview-heading">{{ selectedFile.name }}</h2>
          </div>
          <span>Le fichier reste visible même si son envoi ou son traitement échoue.</span>
        </div>
        <ModelViewer :file="selectedFile" :resources="supportingFiles" />
        <p class="resource-note">
          Pour les fichiers OBJ et GLTF avec textures ou ressources séparées, sélectionnez aussi
          leurs fichiers associés. Seul le modèle principal est envoyé actuellement.
        </p>
      </section>

      <div class="pipeline-note">
        <span aria-hidden="true">i</span>
        <p>
          L’import sauvegarde le fichier, mais ne crée pas de fiche sémantique. Le modèle apparaîtra
          dans la recherche après son traitement par les Lots A et B et son indexation ChromaDB.
        </p>
      </div>
    </section>
  </main>
</template>
