export interface Product {
  id: string
  title: string
  description: string
  category: string
  tags: string[]
  color: string
  emoji: string
  score: number
}

export const products: Product[] = [
  {
    id: 'office-chair',
    title: 'Chaise de bureau',
    description: 'Chaise ergonomique rouge à roulettes',
    category: 'Mobilier',
    tags: ['chaise', 'bureau', 'roulettes', 'rouge'],
    color: '#dce9ff',
    emoji: '🪑',
    score: 98,
  },
  {
    id: 'modern-house',
    title: 'Maison moderne',
    description: 'Maison contemporaine avec grandes fenêtres',
    category: 'Architecture',
    tags: ['maison', 'moderne', 'architecture'],
    color: '#e5e0f7',
    emoji: '🏠',
    score: 96,
  },
  {
    id: 'sport-car',
    title: 'Voiture de sport',
    description: 'Coupé rouge aux lignes aérodynamiques',
    category: 'Véhicules',
    tags: ['voiture', 'sport', 'rouge'],
    color: '#f9dfdf',
    emoji: '🏎️',
    score: 94,
  },
  {
    id: 'oak-tree',
    title: 'Grand chêne',
    description: 'Arbre feuillu avec un tronc détaillé',
    category: 'Nature',
    tags: ['arbre', 'nature', 'feuilles'],
    color: '#dff0e5',
    emoji: '🌳',
    score: 92,
  },
  {
    id: 'knight-sword',
    title: 'Épée de chevalier',
    description: 'Épée médiévale avec garde ouvragée',
    category: 'Objets',
    tags: ['épée', 'chevalier', 'médiéval'],
    color: '#eee8da',
    emoji: '⚔️',
    score: 90,
  },
]

function normalize(value: string) {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase()
}

export function searchProducts(query: string) {
  const terms = normalize(query).split(/\s+/).filter(Boolean)
  if (!terms.length) return products

  return products.filter((product) => {
    const searchableText = normalize(
      [product.title, product.description, product.category, ...product.tags].join(' '),
    )
    return terms.every((term) => searchableText.includes(term))
  })
}
