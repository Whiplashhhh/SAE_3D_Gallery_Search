<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { products } from '../data/products'

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
  <main class="home-page">
    <section class="hero">
      <div class="hero-content">
        <p class="eyebrow">GALERIE DE MODÈLES 3D</p>
        <h1>Trouvez le modèle<br /><em>qui vous inspire.</em></h1>
        <p class="hero-text">
          Décrivez ce que vous cherchez, en quelques mots. Notre collection de modèles 3D est là
          pour donner vie à vos idées.
        </p>
        <form class="hero-search" role="search" @submit.prevent="search">
          <span class="search-icon" aria-hidden="true">⌕</span>
          <input
            v-model="query"
            type="search"
            placeholder="Ex. chaise de bureau rouge"
            aria-label="Décrire le modèle à rechercher"
          />
          <button type="submit">Rechercher <span aria-hidden="true">→</span></button>
        </form>
        <p class="suggestion">
          Essayez : <button @click="query = 'chaise'">chaise</button> ·
          <button @click="query = 'maison'">maison</button> ·
          <button @click="query = 'voiture'">voiture</button>
        </p>
      </div>
      <div class="hero-art" aria-hidden="true">
        <div class="orb orb-large"></div>
        <div class="orb orb-small"></div>
        <div class="cube">◈</div>
      </div>
    </section>

    <section id="catalogue" class="featured-section">
      <div class="section-heading">
        <div>
          <p class="eyebrow">À DÉCOUVRIR</p>
          <h2>Modèles populaires</h2>
        </div>
        <RouterLink class="text-link" :to="{ name: 'search', query: { q: '' } }">
          Voir le catalogue <span aria-hidden="true">→</span>
        </RouterLink>
      </div>
      <div class="product-grid">
        <article v-for="product in products.slice(0, 3)" :key="product.id" class="product-card">
          <div class="product-image" :style="{ '--product-color': product.color }">
            <span>{{ product.emoji }}</span>
            <small>{{ product.category }}</small>
          </div>
          <div class="product-info">
            <div>
              <h3>{{ product.title }}</h3>
              <p>{{ product.description }}</p>
            </div>
            <span class="match-score">{{ product.score }}%</span>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>
