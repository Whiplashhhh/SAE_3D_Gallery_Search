<script setup lang="ts">
import { computed, ref } from 'vue'
import { uploadModel } from '../services/galleryApi'
import './AddModelView.css'

const acceptedFormats = ['.obj', '.gltf', '.stl']
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const error = ref('')
const success = ref('')

const fileLabel = computed(() => selectedFile.value?.name || 'Choisir un fichier 3D')

function selectFile(event: Event) {
  const input = event.target as HTMLInputElement
  selectedFile.value = input.files?.[0] || null
  error.value = ''
  success.value = ''
}

async function submit() {
  if (!selectedFile.value) {
    error.value = 'Sélectionnez un fichier .obj, .gltf ou .stl.'
    return
  }

  uploading.value = true
  error.value = ''
  success.value = ''
  try {
    const uploaded = await uploadModel(selectedFile.value)
    success.value = `${uploaded.nom} a été ajouté. Il sera indexé après la génération de sa fiche par les Lots A et B.`
    selectedFile.value = null
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
        <label class="drop-zone" for="model-file">
          <span class="upload-icon" aria-hidden="true">↥</span>
          <strong>{{ fileLabel }}</strong>
          <small>Formats acceptés : OBJ, GLTF, STL · 50 Mo maximum</small>
          <input
            id="model-file"
            type="file"
            accept=".obj,.gltf,.stl"
            @change="selectFile"
          />
        </label>

        <button class="upload-button" type="submit" :disabled="uploading">
          {{ uploading ? 'Ajout en cours...' : 'Ajouter le modèle' }}
        </button>

        <p v-if="error" class="upload-message upload-error" role="alert">{{ error }}</p>
        <p v-if="success" class="upload-message upload-success" role="status">{{ success }}</p>
      </form>

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
