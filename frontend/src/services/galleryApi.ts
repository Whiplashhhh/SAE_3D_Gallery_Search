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

/** Uniformise accents et casse avant de comparer les termes de recherche. */
function normalize(value: string) {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase()
}

/** Adapte les noms du contrat français de l'API au modèle consommé par Vue. */
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

/** Centralise les GET JSON et transforme les réponses HTTP en erreurs lisibles. */
async function request<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`L'API a répondu avec le statut ${response.status}.`)
  }
  return response.json() as Promise<T>
}

/** Envoie le fichier en multipart et privilégie le détail d'erreur renvoyé par l'API. */
export async function uploadModel(file: File): Promise<ApiModelInfo> {
  const formData = new FormData()
  formData.append('fichier', file)

  const response = await fetch('/api/models/upload', {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) {
    let detail = `L'API a répondu avec le statut ${response.status}.`
    try {
      const body = (await response.json()) as { detail?: string }
      if (body.detail) detail = body.detail
    } catch {
      // Le message de statut reste utile si l'API ne renvoie pas de JSON.
    }
    throw new Error(detail)
  }
  return response.json() as Promise<ApiModelInfo>
}

/** Supprime un modèle via son identifiant encodé dans l'URL. */
export async function deleteModel(id: string): Promise<void> {
  const response = await fetch(`/api/modeles/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    let detail = `L'API a répondu avec le statut ${response.status}.`
    try {
      const body = (await response.json()) as { detail?: string }
      if (body.detail) detail = body.detail
    } catch {
      // Le message de statut reste utile si l'API ne renvoie pas de JSON.
    }
    throw new Error(detail)
  }
}

/** Charge le catalogue complet et convertit chaque réponse au format frontend. */
export async function listModels(): Promise<GalleryModel[]> {
  const models = await request<ApiModelInfo[]>('/api/models')
  return models.map((model) => toModel(model))
}

/**
 * Recherche dans l'API en conservant son classement par score.
 * Un texte vide charge le catalogue ; sinon, un filtre local exige que chaque
 * terme normalisé figure dans les champs affichables du modèle.
 */
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
