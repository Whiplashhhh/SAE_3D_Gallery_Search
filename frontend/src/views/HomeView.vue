<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import './HomeView.css'

type ModeleResultat = {
  id: string
  score: number
  metadonnees: Record<string, string>
}

const requete = ref('maison moderne')
const topK = ref(5)
const categorie = ref('')
const couleur = ref('')
const formatFichier = ref('')
const resultats = ref<ModeleResultat[]>([])
const chargement = ref(false)
const erreur = ref('')
const fichierModele = ref<File | null>(null)
const importationEnCours = ref(false)
const messageImportation = ref('')
const stats = ref({
  nb_modeles_indexes: 0,
  taille_collection: 0,
  ollama_actif: true,
})

const payload = computed(() => ({
  texte: requete.value,
  top_k: Number(topK.value) || 5,
  categorie: categorie.value || undefined,
  couleur: couleur.value || undefined,
  format_fichier: formatFichier.value || undefined,
}))

async function chargerStats() {
  try {
    const reponse = await fetch('/api/stats')
    if (!reponse.ok) {
      throw new Error('Impossible de charger les statistiques')
    }
    stats.value = await reponse.json()
  } catch (e) {
    console.error(e)
  }
}

async function rechercher() {
  chargement.value = true
  erreur.value = ''

  try {
    const reponse = await fetch('/api/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload.value),
    })

    if (!reponse.ok) {
      const details = await reponse.text()
      throw new Error(details || 'Erreur lors de la recherche')
    }

    const donnees = await reponse.json()
    resultats.value = donnees.resultats ?? []
  } catch (e) {
    erreur.value = e instanceof Error ? e.message : 'Recherche impossible.'
    resultats.value = []
  } finally {
    chargement.value = false
  }
}

function choisirFichier(event: Event) {
  const input = event.target as HTMLInputElement
  fichierModele.value = input.files?.[0] ?? null
  messageImportation.value = ''
}

async function importerModele() {
  if (!fichierModele.value) {
    messageImportation.value = 'Sélectionnez un fichier .obj, .gltf ou .stl avant de l’importer.'
    return
  }

  importationEnCours.value = true
  messageImportation.value = ''
  const formulaire = new FormData()
  formulaire.append('fichier', fichierModele.value)

  try {
    const reponse = await fetch('/api/models/upload', {
      method: 'POST',
      body: formulaire,
    })
    if (!reponse.ok) {
      const details = await reponse.json().catch(() => null)
      throw new Error(details?.detail || 'Import impossible.')
    }

    const modele = await reponse.json()
    messageImportation.value = `${modele.nom} a été ajouté au catalogue.`
    fichierModele.value = null
    await chargerStats()
    requete.value = modele.nom
    await rechercher()
  } catch (e) {
    messageImportation.value = e instanceof Error ? e.message : 'Import impossible.'
  } finally {
    importationEnCours.value = false
  }
}

onMounted(() => {
  chargerStats()
  rechercher()
})
</script>

<template>
  <section class="search-panel">
    <div class="hero">
      <div>
        <p class="eyebrow">Catalogue 3D</p>
        <h2>Trouvez le bon modèle en une phrase</h2>
      </div>

      <div class="stats-grid" aria-label="Statistiques du catalogue">
        <div class="stat-card">
          <span class="stat-label">Modèles indexés</span>
          <strong>{{ stats.nb_modeles_indexes }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">Collection</span>
          <strong>{{ stats.taille_collection }}</strong>
        </div>
      </div>
    </div>

    <form class="search-box" @submit.prevent="rechercher">
      <label class="field main-field">
        <span>Requête</span>
        <input v-model="requete" type="text" placeholder="Ex. voiture sport rouge" />
      </label>

      <div class="filters-grid">
        <label class="field">
          <span>Catégorie</span>
          <input v-model="categorie" type="text" placeholder="architecture" />
        </label>

        <label class="field">
          <span>Couleur</span>
          <input v-model="couleur" type="text" placeholder="rouge" />
        </label>

        <label class="field">
          <span>Format</span>
          <input v-model="formatFichier" type="text" placeholder="glb" />
        </label>

        <label class="field">
          <span>Top K</span>
          <input v-model.number="topK" type="number" min="1" max="20" />
        </label>
      </div>

      <div class="actions">
        <button type="submit" :disabled="chargement">
          {{ chargement ? 'Recherche…' : 'Rechercher' }}
        </button>
      </div>
    </form>

    <section class="import-box" aria-labelledby="import-title">
      <div>
        <p class="eyebrow">Ajouter un modèle</p>
        <h3 id="import-title">Importez votre fichier 3D</h3>
        <p class="import-help">Formats acceptés : OBJ, GLTF et STL. Le fichier est conservé localement puis indexé.</p>
      </div>
      <div class="import-actions">
        <label class="file-button">
          Choisir un fichier
          <input type="file" accept=".obj,.gltf,.stl,model/obj,model/gltf+json,model/stl" @change="choisirFichier" />
        </label>
        <span v-if="fichierModele" class="filename">{{ fichierModele.name }}</span>
        <button type="button" class="secondary-button" :disabled="importationEnCours" @click="importerModele">
          {{ importationEnCours ? 'Importation…' : 'Ajouter le modèle' }}
        </button>
      </div>
      <p v-if="messageImportation" class="import-message">{{ messageImportation }}</p>
    </section>

    <div v-if="erreur" class="error-box">
      {{ erreur }}
    </div>

    <section class="results" aria-live="polite">
      <div v-if="!resultats.length && !chargement" class="empty-state">
        Aucun résultat n’a été trouvé pour cette requête.
      </div>

      <article v-for="resultat in resultats" :key="resultat.id" class="result-card">
        <div class="result-head">
          <h3>{{ resultat.metadonnees.nom || resultat.id }}</h3>
          <span class="score">{{ resultat.score.toFixed(3) }}</span>
        </div>

        <dl class="meta-list">
          <div>
            <dt>ID</dt>
            <dd>{{ resultat.id }}</dd>
          </div>
          <div>
            <dt>Catégorie</dt>
            <dd>{{ resultat.metadonnees.categorie || '—' }}</dd>
          </div>
          <div>
            <dt>Couleur</dt>
            <dd>{{ resultat.metadonnees.couleur || '—' }}</dd>
          </div>
          <div>
            <dt>Format</dt>
            <dd>{{ resultat.metadonnees.format_fichier || '—' }}</dd>
          </div>
        </dl>

        <p class="description">
          {{ resultat.metadonnees.description || 'Aucune description ajoutée.' }}
        </p>
      </article>
    </section>
  </section>
</template>
