<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  AmbientLight,
  Box3,
  Color,
  DirectionalLight,
  GridHelper,
  Group,
  LoadingManager,
  Mesh,
  MeshStandardMaterial,
  PerspectiveCamera,
  Scene,
  SRGBColorSpace,
  Texture,
  Vector3,
  WebGLRenderer,
  type Material,
  type Object3D,
} from 'three'
import { MTLLoader } from 'three/addons/loaders/MTLLoader.js'
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { STLLoader } from 'three/addons/loaders/STLLoader.js'
import './ModelViewer.css'

const props = defineProps<{
  file: File
  resources?: File[]
}>()

const container = ref<HTMLDivElement | null>(null)
const loading = ref(true)
const error = ref('')

let renderer: WebGLRenderer | undefined
let scene: Scene | undefined
let camera: PerspectiveCamera | undefined
let controls: OrbitControls | undefined
let resizeObserver: ResizeObserver | undefined
let animationFrame = 0
let currentModel: Object3D | undefined
let generation = 0
let objectUrls: string[] = []

function disposeMaterial(material: Material) {
  for (const value of Object.values(material)) {
    if (value instanceof Texture) value.dispose()
  }
  material.dispose()
}

function disposeModel(model: Object3D) {
  model.traverse((object) => {
    if (!(object instanceof Mesh)) return
    object.geometry.dispose()
    if (Array.isArray(object.material)) object.material.forEach(disposeMaterial)
    else disposeMaterial(object.material)
  })
}

function fitModel(model: Object3D) {
  const bounds = new Box3().setFromObject(model)
  const size = bounds.getSize(new Vector3())
  const center = bounds.getCenter(new Vector3())
  const maxDimension = Math.max(size.x, size.y, size.z)

  if (!Number.isFinite(maxDimension) || maxDimension <= 0) {
    throw new Error('Le fichier ne contient pas de géométrie 3D exploitable.')
  }

  model.position.sub(center)
  model.scale.multiplyScalar(2.4 / maxDimension)
}

function createLoadingManager(files: File[]) {
  const manager = new LoadingManager()
  const resourceUrls = new Map<string, string>()
  objectUrls = files.map((file) => {
    const url = URL.createObjectURL(file)
    resourceUrls.set(file.name.toLocaleLowerCase(), url)
    return url
  })
  manager.setURLModifier((url) => {
    const filename = decodeURIComponent(url.split(/[?#]/, 1)[0] || '')
      .split('/')
      .pop()
      ?.toLocaleLowerCase()
    return (filename && resourceUrls.get(filename)) || url
  })
  return manager
}

async function loadModel(file: File, resources: File[]): Promise<Object3D> {
  const extension = file.name.split('.').pop()?.toLocaleLowerCase()
  const manager = createLoadingManager([file, ...resources])

  if (extension === 'gltf') {
    const loader = new GLTFLoader(manager)
    const data = await file.arrayBuffer()
    return new Promise((resolve, reject) => {
      loader.parse(data, '', (gltf) => resolve(gltf.scene), reject)
    })
  }

  if (extension === 'obj') {
    const content = await file.text()
    const materialFile = resources.find((resource) =>
      resource.name.toLocaleLowerCase().endsWith('.mtl'),
    )
    const loader = new OBJLoader(manager)
    if (materialFile) {
      const materialLoader = new MTLLoader(manager)
      loader.setMaterials(materialLoader.parse(await materialFile.text(), ''))
    }
    return loader.parse(content)
  }

  if (extension === 'stl') {
    const geometry = new STLLoader(manager).parse(await file.arrayBuffer())
    geometry.computeVertexNormals()
    const mesh = new Mesh(geometry, new MeshStandardMaterial({ color: 0x8795d8 }))
    const model = new Group()
    model.add(mesh)
    return model
  }

  throw new Error('Ce format de fichier ne peut pas être prévisualisé.')
}

function resize() {
  if (!container.value || !renderer || !camera) return
  const { width, height } = container.value.getBoundingClientRect()
  if (!width || !height) return
  renderer.setSize(width, height, false)
  camera.aspect = width / height
  camera.updateProjectionMatrix()
}

async function renderFile() {
  const currentGeneration = ++generation
  loading.value = true
  error.value = ''

  if (currentModel) {
    disposeModel(currentModel)
    scene?.remove(currentModel)
    currentModel = undefined
  }
  objectUrls.forEach(URL.revokeObjectURL)
  objectUrls = []

  try {
    const model = await loadModel(props.file, props.resources || [])
    if (currentGeneration !== generation) {
      disposeModel(model)
      return
    }

    fitModel(model)
    currentModel = model
    scene?.add(model)
    if (camera) camera.position.set(3.3, 2.5, 3.3)
    controls?.target.set(0, 0, 0)
    controls?.update()
  } catch (cause) {
    if (currentGeneration === generation) {
      error.value =
        cause instanceof Error
          ? cause.message
          : 'Impossible de lire ce modèle. Vérifiez son format et ses fichiers associés.'
    }
  } finally {
    if (currentGeneration === generation) loading.value = false
  }
}

onMounted(() => {
  if (!container.value) return

  try {
    scene = new Scene()
    scene.background = new Color('#f8f9ff')
    camera = new PerspectiveCamera(40, 1, 0.01, 1000)
    camera.position.set(3.3, 2.5, 3.3)
    renderer = new WebGLRenderer({ antialias: true })
    renderer.outputColorSpace = SRGBColorSpace
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    container.value.appendChild(renderer.domElement)

    scene.add(new AmbientLight(0xffffff, 2))
    const keyLight = new DirectionalLight(0xffffff, 2.5)
    keyLight.position.set(4, 6, 5)
    scene.add(keyLight)
    scene.add(new GridHelper(4, 20, 0xc6cbe0, 0xe2e5f0))

    controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    resizeObserver = new ResizeObserver(resize)
    resizeObserver.observe(container.value)
    resize()

    const animate = () => {
      animationFrame = requestAnimationFrame(animate)
      controls?.update()
      if (scene && camera && renderer) renderer.render(scene, camera)
    }
    animate()
    void renderFile()
  } catch (cause) {
    error.value =
      cause instanceof Error ? cause.message : 'Le visualiseur 3D ne peut pas être initialisé.'
    loading.value = false
  }
})

watch(
  () => [props.file, props.resources],
  () => void renderFile(),
)

onBeforeUnmount(() => {
  generation += 1
  cancelAnimationFrame(animationFrame)
  resizeObserver?.disconnect()
  controls?.dispose()
  if (currentModel) disposeModel(currentModel)
  objectUrls.forEach(URL.revokeObjectURL)
  renderer?.dispose()
  renderer?.domElement.remove()
})
</script>

<template>
  <div ref="container" class="model-viewer" aria-label="Aperçu interactif du modèle 3D">
    <p v-if="loading" class="viewer-status">Chargement de l’aperçu 3D…</p>
    <p v-else-if="error" class="viewer-status viewer-error" role="alert">{{ error }}</p>
    <p v-else class="viewer-hint">Faites glisser pour tourner · molette pour zoomer</p>
  </div>
</template>
