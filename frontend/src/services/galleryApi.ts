export interface GalleryModel {
  id: string
  title: string
  description: string
  category: string
  color: string
  format: string
  originalFilename: string
  dateCreated: string
  tags: string[]
  score?: number
  emoji: string
}

interface ApiModelInfo {
  id: string
  nom: string
  metadonnees: Record<string, string>
}

interface SearchResponse {
  resultats: Array<{
    id: string
    score: number
    metadonnees: Record<string, string>
  }>
  nb_total: number
  temps_ms: number
}

function getEmoji(category: string) {
  const value = category.toLocaleLowerCase()
  if (value.includes('mobil')) return '🪑'
  if (value.includes('architect')) return '🏠'
  if (value.includes('véhic') || value.includes('vehic')) return '🏎️'
  if (value.includes('nature')) return '🌳'
  return '◈'
}

function getColorValue(color: string) {
  const colorValues: Record<string, string> = {
    beige: '#eee2c8',
    gris: '#d9dde5',
    rouge: '#f2caca',
    vert: '#d7eadb',
    bleu: '#d4e2fa',
    jaune: '#f8e7ae',
    noir: '#d2d3d6',
    blanc: '#f1f2f3',
    marron: '#e5d2bd',
    orange: '#f8d4b2',
    violet: '#e3d7f4',
  }

  return colorValues[color.toLocaleLowerCase().trim()] || '#e5e8f7'
}

function normalize(value: string) {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase()
}

function toModel(
  model: ApiModelInfo | SearchResponse['resultats'][number],
  score?: number,
): GalleryModel {
  const metadata = model.metadonnees
  const category = metadata.categorie || 'Modèle 3D'

  return {
    id: model.id,
    title: 'nom' in model ? model.nom : metadata.nom || model.id,
    description: metadata.description || 'Modèle 3D disponible dans la galerie.',
    category,
    color: getColorValue(metadata.couleur || ''),
    format: metadata.format_fichier || '',
    originalFilename: metadata.nom_fichier_original || '',
    dateCreated: metadata.date_creation || '',
    tags: [category, metadata.couleur, metadata.format_fichier].filter(
      (tag): tag is string => Boolean(tag),
    ),
    score,
    emoji: getEmoji(category),
  }
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`L'API a répondu avec le statut ${response.status}.`)
  }
  return response.json() as Promise<T>
}

export async function listModels(): Promise<GalleryModel[]> {
  const models = await request<ApiModelInfo[]>('/api/models')
  return models.map((model) => toModel(model))
}

export async function searchModels(query: string): Promise<GalleryModel[]> {
  if (!query.trim()) return listModels()

  const response = await request<SearchResponse>(
    `/api/recherche?q=${encodeURIComponent(query.trim())}&k=12`,
  )
  const terms = normalize(query).split(/\s+/).filter(Boolean)

  return response.resultats
    .map((result) => toModel(result, result.score))
    .filter((model) => {
      const searchableText = normalize(
        [model.title, model.description, model.category, model.color, ...model.tags].join(' '),
      )
      return terms.every((term) => searchableText.includes(term))
    })
}
