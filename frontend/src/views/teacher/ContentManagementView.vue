<script setup>
import { ref, onMounted, watch } from 'vue'
import { 
  Plus, 
  BookOpen, 
  FileText, 
  CheckCircle, 
  Eye, 
  EyeOff, 
  Trash2, 
  Edit3, 
  FlaskConical, 
  AlertCircle,
  Sparkles,
  RefreshCw,
  Smartphone,
  Monitor,
  X,
  ArrowRight,
  ExternalLink,
  CheckSquare
} from 'lucide-vue-next'
import { api } from '@/api/client'
import { renderFormula } from '@/utils/formula'

const props = defineProps({
  user: Object
})

const emit = defineEmits(['open-lab'])

// Level filter: 'X' | 'XI' | 'XII'
const selectedGradeLevel = ref('X')
const gradeLevels = ['X', 'XI', 'XII']
const modules = ref([])
const selectedModule = ref(null)
const materials = ref([])

const loadingModules = ref(false)
const loadingMaterials = ref(false)

// Modals
const showModuleModal = ref(false)
const newModuleTitle = ref('')
const newModuleOrder = ref(1)

const showMaterialModal = ref(false)
const materialForm = ref({
  uuid: null,
  title: '',
  content_html: '',
  order_index: 1,
  is_published: false
})
const isEditingMaterial = ref(false)

// AI Material Generator State
const aiMaterialTopic = ref('')
const isGeneratingMaterialAI = ref(false)
const aiMaterialError = ref('')

// Student View Preview State
const showPreviewModal = ref(false)
const previewMaterial = ref(null)
const previewDeviceMode = ref('desktop') // 'desktop' | 'mobile'

const openPreviewMaterial = (mat) => {
  previewMaterial.value = mat
  showPreviewModal.value = true
}

const openPreviewModule = () => {
  previewMaterial.value = materials.value.length > 0 ? materials.value[0] : null
  showPreviewModal.value = true
}

const stripHtml = (html) => {
  if (!html) return ''
  return html.replace(/<[^>]*>?/gm, ' ').replace(/\s+/g, ' ').trim()
}

// Map of configured virtual labs by material_id
const labsMap = ref({})

const loadLabs = async () => {
  try {
    const labs = await api.content.listLabs()
    const map = {}
    for (const l of labs || []) {
      if (l.material_id) map[l.material_id] = l
    }
    labsMap.value = map
  } catch (e) {
    console.warn('Gagal mengambil daftar lab virtual:', e)
  }
}

const loadModules = async () => {
  loadingModules.value = true
  try {
    const res = await api.content.listModulesByGrade(selectedGradeLevel.value)
    modules.value = res || []
    if (modules.value.length > 0) {
      selectModule(modules.value[0])
    } else {
      selectedModule.value = null
      materials.value = []
    }
  } catch (err) {
    console.error('Gagal mengambil modul:', err)
  } finally {
    loadingModules.value = false
  }
}

const selectModule = async (mod) => {
  selectedModule.value = mod
  loadingMaterials.value = true
  try {
    const res = await api.content.listMaterials(mod.id)
    materials.value = res || []
    await loadLabs()
  } catch (err) {
    console.error('Gagal mengambil materi:', err)
  } finally {
    loadingMaterials.value = false
  }
}

watch(selectedGradeLevel, () => {
  loadModules()
  loadLabs()
})

// Module Actions
const handleCreateModule = async () => {
  if (!newModuleTitle.value.trim()) return
  try {
    const res = await api.content.createModule({
      grade_level: selectedGradeLevel.value,
      title: newModuleTitle.value.trim(),
      order_index: Number(newModuleOrder.value) || 1
    })
    modules.value.push(res)
    newModuleTitle.value = ''
    showModuleModal.value = false
    selectModule(res)
  } catch (err) {
    alert('Gagal membuat modul: ' + err.message)
  }
}

const handleDeleteModule = async (mod) => {
  if (!confirm(`Hapus modul "${mod.title}" beserta seluruh materinya?`)) return
  try {
    await api.content.deleteModule(mod.uuid)
    modules.value = modules.value.filter(m => m.id !== mod.id)
    if (selectedModule.value?.id === mod.id) {
      selectedModule.value = modules.value[0] || null
      if (selectedModule.value) selectModule(selectedModule.value)
      else materials.value = []
    }
  } catch (err) {
    alert('Gagal menghapus modul: ' + err.message)
  }
}

// Material Actions
const openCreateMaterial = () => {
  isEditingMaterial.value = false
  aiMaterialTopic.value = ''
  aiMaterialError.value = ''
  materialForm.value = {
    uuid: null,
    title: '',
    content_html: '',
    order_index: (materials.value.length + 1),
    is_published: true
  }
  showMaterialModal.value = true
}

const handleGenerateMaterialAI = async () => {
  if (!aiMaterialTopic.value.trim()) return
  isGeneratingMaterialAI.value = true
  aiMaterialError.value = ''

  try {
    const res = await api.content.generateMaterialWithAI(
      aiMaterialTopic.value.trim(),
      selectedModule.value?.id
    )
    if (res) {
      if (res.title) materialForm.value.title = res.title
      if (res.content_html) materialForm.value.content_html = res.content_html
    }
  } catch (err) {
    aiMaterialError.value = err.message || 'Gagal generate materi dengan AI.'
  } finally {
    isGeneratingMaterialAI.value = false
  }
}

const openEditMaterial = (mat) => {
  isEditingMaterial.value = true
  materialForm.value = {
    uuid: mat.uuid,
    title: mat.title,
    content_html: mat.content_html || '',
    order_index: mat.order_index,
    is_published: mat.is_published
  }
  showMaterialModal.value = true
}

const saveMaterial = async () => {
  if (!materialForm.value.title.trim()) return
  try {
    if (isEditingMaterial.value) {
      const res = await api.content.updateMaterial(materialForm.value.uuid, {
        title: materialForm.value.title,
        content_html: materialForm.value.content_html,
        order_index: materialForm.value.order_index,
        is_published: materialForm.value.is_published
      })
      const idx = materials.value.findIndex(m => m.uuid === res.uuid)
      if (idx !== -1) materials.value[idx] = res
    } else {
      const res = await api.content.createMaterial({
        module_id: selectedModule.value.id,
        title: materialForm.value.title,
        content_html: materialForm.value.content_html,
        order_index: materialForm.value.order_index,
        is_published: materialForm.value.is_published
      })
      materials.value.push(res)
    }
    showMaterialModal.value = false
  } catch (err) {
    alert('Gagal menyimpan materi: ' + err.message)
  }
}

const togglePublish = async (mat) => {
  try {
    const updated = await api.content.updateMaterial(mat.uuid, {
      is_published: !mat.is_published
    })
    mat.is_published = updated.is_published
  } catch (err) {
    alert('Gagal mengubah status publikasi: ' + err.message)
  }
}

const handleDeleteMaterial = async (mat) => {
  if (!confirm(`Hapus materi "${mat.title}"?`)) return
  try {
    await api.content.deleteMaterial(mat.uuid)
    materials.value = materials.value.filter(m => m.id !== mat.id)
  } catch (err) {
    alert('Gagal menghapus materi: ' + err.message)
  }
}

onMounted(() => {
  loadModules()
  loadLabs()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header with Grade Level Selector -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-extrabold text-slate-900 tracking-tight">Kurikulum & Modul Pembelajaran</h2>
        <p class="text-xs text-slate-500 font-medium mt-1">Susun materi kimia per tingkatan level (X, XI, XII) yang otomatis dibagikan ke seluruh sub-kelas terkait.</p>
      </div>

      <!-- Grade Level Switcher Pills -->
      <div class="flex items-center gap-1.5 bg-slate-100 p-1.5 rounded-2xl border border-slate-200 self-start sm:self-auto shadow-2xs">
        <span class="text-[11px] font-bold text-slate-500 px-2 uppercase">Level:</span>
        <button
          v-for="lvl in gradeLevels"
          :key="lvl"
          @click="selectedGradeLevel = lvl"
          :class="[
            'px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all',
            selectedGradeLevel === lvl
              ? 'bg-chemist-dark text-white shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-white/60'
          ]"
        >
          Kelas {{ lvl }}
        </button>
      </div>
    </div>

    <!-- Main Content Layout (Split Module & Materials) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <!-- Left: Modules Column (4 Cols) -->
      <div class="lg:col-span-4 space-y-3">
        <div class="flex items-center justify-between px-1">
          <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Topik / Modul ({{ modules.length }})</h4>
          <button 
            @click="showModuleModal = true"
            class="text-xs font-bold text-chemist-primary hover:underline flex items-center gap-1"
          >
            <Plus class="w-3.5 h-3.5" />
            <span>Tambah Topik</span>
          </button>
        </div>

        <div v-if="loadingModules" class="p-8 bg-white rounded-2xl border border-slate-100 text-center text-xs text-slate-400">
          Memuat topik modul...
        </div>

        <div v-else-if="modules.length === 0" class="p-8 bg-white rounded-2xl border border-dashed border-slate-200 text-center space-y-2">
          <BookOpen class="w-8 h-8 text-slate-300 mx-auto" />
          <p class="text-xs font-bold text-slate-700">Belum Ada Topik di Kelas Ini</p>
          <button 
            @click="showModuleModal = true"
            class="text-xs font-bold text-chemist-primary underline"
          >
            + Buat Topik Pertama
          </button>
        </div>

        <!-- Modules List -->
        <div 
          v-for="(mod, idx) in modules" 
          :key="mod.id"
          @click="selectModule(mod)"
          class="p-4 rounded-2xl border transition-all cursor-pointer text-left relative"
          :class="selectedModule?.id === mod.id 
            ? 'bg-white border-chemist-primary ring-2 ring-chemist-primary/15 shadow-card' 
            : 'bg-white/80 border-slate-100 hover:border-slate-300 hover:bg-white'"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex items-start gap-3">
              <span class="w-6 h-6 rounded-lg bg-slate-100 text-slate-600 font-mono font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                {{ idx + 1 }}
              </span>
              <div>
                <h5 class="font-bold text-sm text-slate-900 leading-tight">{{ mod.title }}</h5>
                <span class="text-[11px] text-slate-400 font-medium">Urutan ke-{{ mod.order_index }}</span>
              </div>
            </div>

            <button 
              @click.stop="handleDeleteModule(mod)"
              class="p-1 text-slate-400 hover:text-rose-600 transition-colors"
              title="Hapus Modul"
            >
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      <!-- Right: Materials of Selected Module (8 Cols) -->
      <div class="lg:col-span-8 bg-white rounded-3xl border border-slate-100 p-6 shadow-card space-y-6">
        <div v-if="!selectedModule" class="text-center py-16 text-slate-400 text-sm">
          Pilih salah satu topik modul di sebelah kiri untuk melihat materi pembelajaran.
        </div>

        <template v-else>
          <!-- Module Header -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-100">
            <div>
              <span class="text-[10px] font-bold uppercase tracking-wider text-chemist-primary bg-blue-50 px-2 py-0.5 rounded">Modul Aktif</span>
              <h3 class="text-xl font-bold text-slate-900 mt-1">{{ selectedModule.title }}</h3>
            </div>

            <div class="flex items-center gap-2 self-start sm:self-auto flex-wrap">
              <button 
                v-if="materials.length > 0"
                @click="openPreviewModule"
                class="inline-flex items-center gap-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold px-3.5 py-2.5 rounded-xl border border-indigo-200 transition-all shadow-2xs active:scale-95"
                title="Lihat seluruh materi modul ini sebagaimana tampilan siswa"
              >
                <BookOpen class="w-4 h-4 text-indigo-600" />
                <span>Lihat Tampilan Siswa</span>
              </button>

              <button 
                @click="openCreateMaterial"
                class="inline-flex items-center gap-2 bg-chemist-dark hover:bg-slate-900 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow-sm transition-all active:scale-95"
              >
                <Plus class="w-4 h-4 text-emerald-400" />
                <span>Tambah Materi</span>
              </button>
            </div>
          </div>

          <!-- Materials List -->
          <div v-if="loadingMaterials" class="text-center py-10 text-slate-400 text-xs">
            Memuat materi pembelajaran...
          </div>

          <div v-else-if="materials.length === 0" class="text-center py-12 bg-slate-50/60 rounded-2xl border border-dashed border-slate-200 space-y-2">
            <FileText class="w-8 h-8 text-slate-300 mx-auto" />
            <p class="text-xs font-bold text-slate-700">Belum ada materi di modul ini</p>
            <p class="text-xs text-slate-400">Tambahkan materi teori atau hubungkan ke simulasi Lab Virtual.</p>
          </div>

          <div v-else class="space-y-3">
            <div 
              v-for="mat in materials" 
              :key="mat.id"
              class="p-4 rounded-2xl border border-slate-100 bg-slate-50/50 hover:bg-white hover:border-indigo-100 transition-all space-y-3"
            >
              <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div class="space-y-1 flex-1">
                  <div class="flex items-center gap-2 flex-wrap">
                    <h5 class="font-bold text-slate-900 text-sm">{{ mat.title }}</h5>
                    <!-- Publish Badge -->
                    <span 
                      class="text-[10px] font-bold px-2 py-0.5 rounded-full"
                      :class="mat.is_published ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'"
                    >
                      {{ mat.is_published ? 'Terkirim ke Siswa' : 'Draft Guru' }}
                    </span>

                    <!-- Virtual Lab Attached Badge -->
                    <span 
                      v-if="labsMap[mat.id]"
                      class="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-sky-50 text-sky-700 border border-sky-200"
                    >
                      <FlaskConical class="w-3 h-3 text-sky-600" />
                      <span>Lab Virtual Siap</span>
                    </span>
                  </div>

                  <p class="text-xs text-slate-500 line-clamp-2 leading-relaxed" v-if="mat.content_html">
                    {{ stripHtml(mat.content_html) }}
                  </p>
                  <p class="text-xs text-slate-400 italic" v-else>Belum ada isi materi.</p>
                </div>

                <!-- Actions Button Group -->
                <div class="flex items-center gap-1.5 shrink-0 flex-wrap justify-end">
                  <!-- Direct Virtual Lab Creator/Editor Button -->
                  <button 
                    @click="emit('open-lab', mat)"
                    class="px-2.5 py-1.5 rounded-xl text-xs font-bold transition-all shadow-2xs flex items-center gap-1.5"
                    :class="labsMap[mat.id] 
                      ? 'bg-sky-50 text-sky-700 hover:bg-sky-100 border border-sky-200' 
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200'"
                    :title="labsMap[mat.id] ? 'Ubah Konfigurasi Lab Virtual untuk Materi Ini' : 'Buat Lab Virtual untuk Materi Ini'"
                  >
                    <FlaskConical class="w-3.5 h-3.5" :class="labsMap[mat.id] ? 'text-sky-600' : 'text-slate-500'" />
                    <span>{{ labsMap[mat.id] ? 'Edit Lab' : '+ Buat Lab' }}</span>
                  </button>

                  <!-- View Student Page for this Material -->
                  <button 
                    @click="openPreviewMaterial(mat)"
                    class="px-2.5 py-1.5 rounded-xl text-xs font-bold text-chemist-primary bg-blue-50 hover:bg-blue-100 border border-blue-200 flex items-center gap-1.5 transition-all shadow-2xs"
                    title="Pratinjau tampilan materi ini sebagaimana dilihat siswa"
                  >
                    <BookOpen class="w-3.5 h-3.5" />
                    <span>Lihat Siswa</span>
                  </button>

                  <!-- Toggle Publish Button -->
                  <button 
                    @click="togglePublish(mat)"
                    class="p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-white border border-transparent hover:border-slate-200 transition-colors"
                    :title="mat.is_published ? 'Sembunyikan dari Siswa' : 'Publikasikan ke Siswa'"
                  >
                    <component :is="mat.is_published ? Eye : EyeOff" class="w-4 h-4" />
                  </button>

                  <!-- Edit Material -->
                  <button 
                    @click="openEditMaterial(mat)"
                    class="p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-white border border-transparent hover:border-slate-200 transition-colors"
                    title="Edit Materi"
                  >
                    <Edit3 class="w-4 h-4" />
                  </button>

                  <!-- Delete -->
                  <button 
                    @click="handleDeleteMaterial(mat)"
                    class="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                    title="Hapus Materi"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Modal Tambah Topik Modul -->
    <div v-if="showModuleModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-elevated space-y-4">
        <h3 class="text-base font-bold text-slate-900">Tambah Topik Modul Baru</h3>
        
        <div class="space-y-3 text-sm">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Judul Modul / Topik</label>
            <input 
              v-model="newModuleTitle"
              type="text" 
              placeholder="Contoh: Larutan Asam Basa & Titrasi"
              class="w-full bg-slate-50 focus:bg-white text-sm px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Urutan Indeks Bab</label>
            <input 
              v-model="newModuleOrder"
              type="number" 
              class="w-full bg-slate-50 focus:bg-white text-sm px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none"
            />
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
          <button @click="showModuleModal = false" class="px-4 py-2 rounded-xl text-xs font-bold text-slate-600">Batal</button>
          <button @click="handleCreateModule" class="px-5 py-2 rounded-xl text-xs font-bold bg-chemist-dark text-white shadow-md">Simpan Modul</button>
        </div>
      </div>
    </div>

    <!-- Modal Form Materi Pembelajaran -->
    <div v-if="showMaterialModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-elevated space-y-4">
        <h3 class="text-base font-bold text-slate-900">
          {{ isEditingMaterial ? 'Edit Materi Pembelajaran' : 'Tambah Materi Baru' }}
        </h3>

        <!-- AI Generator Assistant for Material Content -->
        <div class="bg-slate-50 border border-slate-200/80 rounded-2xl p-3.5 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-800 flex items-center gap-1.5">
              <Sparkles class="w-3.5 h-3.5 text-chemist-primary" />
              <span>Generate Draf Materi</span>
            </span>
          </div>
          <div class="flex gap-2">
            <input 
              v-model="aiMaterialTopic"
              type="text"
              placeholder="Ketik topik materi, cth: Konsep Mol dan Massa Molar..."
              @keyup.enter="handleGenerateMaterialAI"
              class="flex-1 bg-white border border-slate-200 focus:border-chemist-primary rounded-xl px-3 py-2 text-xs text-slate-800 outline-none"
            />
            <button 
              @click="handleGenerateMaterialAI"
              :disabled="isGeneratingMaterialAI || !aiMaterialTopic.trim()"
              class="bg-chemist-dark hover:bg-slate-900 disabled:opacity-50 text-white px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all shadow-2xs shrink-0"
            >
              <RefreshCw v-if="isGeneratingMaterialAI" class="w-3.5 h-3.5 animate-spin" />
              <Sparkles v-else class="w-3.5 h-3.5 text-sky-400" />
              <span>{{ isGeneratingMaterialAI ? 'Memproses...' : 'Generate' }}</span>
            </button>
          </div>
          <p v-if="aiMaterialError" class="text-[11px] text-rose-600 font-semibold">{{ aiMaterialError }}</p>
        </div>

        <div class="space-y-3 text-sm">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Judul Materi</label>
            <input 
              v-model="materialForm.title"
              type="text" 
              placeholder="Contoh: Teori Arrhenius dan Bronsted-Lowry"
              class="w-full bg-slate-50 focus:bg-white text-sm px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Konten Materi (Teks / Ringkasan Teori)</label>
            <textarea 
              v-model="materialForm.content_html"
              rows="5"
              placeholder="Tulis ringkasan rumus, reaksi, dan penjelasan konsep kimia untuk siswa di sini..."
              class="w-full bg-slate-50 focus:bg-white text-sm px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none font-sans"
            ></textarea>
          </div>

          <div class="flex items-center justify-between pt-1">
            <div class="flex items-center gap-2">
              <input 
                id="is_pub"
                type="checkbox" 
                v-model="materialForm.is_published"
                class="w-4 h-4 text-chemist-primary rounded border-slate-300 focus:ring-chemist-primary"
              />
              <label for="is_pub" class="text-xs font-semibold text-slate-700 cursor-pointer">
                Publikasikan ke Siswa
              </label>
            </div>

            <div class="flex items-center gap-2">
              <label class="text-xs text-slate-400 font-medium">Urutan:</label>
              <input 
                type="number" 
                v-model="materialForm.order_index"
                class="w-16 bg-slate-50 text-xs px-2 py-1 rounded-lg border border-slate-200 text-center font-bold"
              />
            </div>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
          <button @click="showMaterialModal = false" class="px-4 py-2 rounded-xl text-xs font-bold text-slate-600">Batal</button>
          <button @click="saveMaterial" class="px-5 py-2 rounded-xl text-xs font-bold bg-chemist-dark text-white shadow-md">Simpan Materi</button>
        </div>
      </div>
    </div>

    <!-- Modal Pratinjau Tampilan Siswa (Student View Simulator) -->
    <div 
      v-if="showPreviewModal" 
      class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-2 sm:p-4 md:p-6"
    >
      <div 
        class="bg-white rounded-3xl w-full flex flex-col shadow-2xl border border-slate-200 max-h-[92vh] overflow-hidden transition-all duration-200"
        :class="previewDeviceMode === 'mobile' ? 'max-w-[400px]' : 'max-w-4xl'"
      >
        <!-- Modal Top Bar -->
        <div class="px-5 py-3 border-b border-slate-100 bg-slate-50 flex items-center justify-between gap-3 shrink-0">
          <div class="flex items-center gap-2">
            <span class="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider bg-indigo-100 text-indigo-800 px-2.5 py-0.5 rounded-full">
              <BookOpen class="w-3 h-3 text-indigo-700" />
              <span>Pratinjau Siswa</span>
            </span>
            <span class="text-xs text-slate-500 font-medium hidden sm:inline">
              Modul: <strong class="text-slate-800">{{ selectedModule?.title }}</strong>
            </span>
          </div>

          <!-- Device Mode Switcher (Desktop vs Mobile) & Close -->
          <div class="flex items-center gap-2">
            <div class="flex items-center bg-white border border-slate-200 rounded-xl p-0.5 shadow-2xs">
              <button 
                @click="previewDeviceMode = 'desktop'"
                class="px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center gap-1 transition-all"
                :class="previewDeviceMode === 'desktop' ? 'bg-chemist-dark text-white shadow-2xs' : 'text-slate-500 hover:text-slate-800'"
                title="Tampilan Desktop / Laptop"
              >
                <Monitor class="w-3.5 h-3.5" />
                <span class="hidden sm:inline">Desktop</span>
              </button>
              <button 
                @click="previewDeviceMode = 'mobile'"
                class="px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center gap-1 transition-all"
                :class="previewDeviceMode === 'mobile' ? 'bg-chemist-dark text-white shadow-2xs' : 'text-slate-500 hover:text-slate-800'"
                title="Tampilan Hape / Smartphone"
              >
                <Smartphone class="w-3.5 h-3.5" />
                <span class="hidden sm:inline">Hape</span>
              </button>
            </div>

            <button 
              @click="showPreviewModal = false"
              class="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors"
              title="Tutup Pratinjau"
            >
              <X class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- Material Switcher Pill Bar -->
        <div v-if="materials.length > 1" class="px-5 py-2.5 bg-slate-100/70 border-b border-slate-200/60 flex items-center gap-2 overflow-x-auto shrink-0">
          <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider shrink-0">Materi:</span>
          <button 
            @click="previewMaterial = null"
            class="text-xs px-3 py-1 rounded-xl font-semibold whitespace-nowrap transition-all shrink-0"
            :class="previewMaterial === null 
              ? 'bg-chemist-dark text-white shadow-2xs' 
              : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200/70'"
          >
            Semua ({{ materials.length }})
          </button>
          <button 
            v-for="mat in materials" 
            :key="mat.id"
            @click="previewMaterial = mat"
            class="text-xs px-3 py-1 rounded-xl font-semibold whitespace-nowrap transition-all shrink-0"
            :class="previewMaterial?.id === mat.id 
              ? 'bg-chemist-dark text-white shadow-2xs' 
              : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200/70'"
          >
            {{ mat.title }}
          </button>
        </div>

        <!-- Scrollable Student Perspective Content -->
        <div class="flex-1 overflow-y-auto p-4 sm:p-6 bg-[#F6F8FC] space-y-4">
          <!-- Draft Notice (if viewing a draft material) -->
          <div 
            v-if="previewMaterial && !previewMaterial.is_published" 
            class="bg-amber-50 border border-amber-200 rounded-2xl p-3 text-xs text-amber-800 flex items-center gap-2 shadow-2xs"
          >
            <AlertCircle class="w-4 h-4 text-amber-600 shrink-0" />
            <span>Materi ini berstatus <strong>Draft Guru</strong>. Siswa tidak dapat membacanya sebelum dipublikasikan.</span>
          </div>

          <!-- Student Page Representation (Matches StudentDashboard.vue) -->
          <div class="bg-white rounded-2xl border border-slate-200/80 p-5 sm:p-6 shadow-sm space-y-5">
            <!-- Header section as in StudentDashboard -->
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
              <div>
                <h3 class="text-base sm:text-lg font-bold text-slate-900">{{ selectedModule?.title }}</h3>
                <p class="text-xs text-slate-400">Materi teori dan panduan praktikum laboratorium</p>
              </div>

              <div class="flex items-center gap-2 self-start sm:self-auto flex-wrap">
                <button
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 text-white rounded-xl text-xs font-semibold shadow-2xs opacity-90 cursor-default"
                >
                  <CheckSquare class="w-3.5 h-3.5" />
                  <span>Kuis Modul</span>
                </button>

                <button
                  @click="emit('open-lab', previewMaterial || materials[0])"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-chemist-primary hover:bg-blue-600 text-white rounded-xl text-xs font-semibold shadow-2xs transition-all"
                >
                  <FlaskConical class="w-3.5 h-3.5" />
                  <span>Buka Lab Virtual</span>
                </button>
              </div>
            </div>

            <!-- List of materials in student layout -->
            <div v-if="materials.length > 0" class="space-y-4">
              <div 
                v-for="mat in (previewMaterial ? [previewMaterial] : materials)" 
                :key="mat.id"
                class="border border-slate-100 bg-slate-50/50 rounded-xl p-4 sm:p-5 space-y-2.5 transition-all"
              >
                <div class="flex items-center justify-between gap-3">
                  <div class="flex items-center gap-2">
                    <h4 class="text-sm sm:text-base font-bold text-slate-800">{{ mat.title }}</h4>
                    <span 
                      v-if="!mat.is_published"
                      class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200"
                    >
                      Draft
                    </span>
                  </div>

                  <button
                    @click="emit('open-lab', mat)"
                    class="text-xs text-chemist-primary hover:underline font-semibold flex items-center gap-1 shrink-0"
                  >
                    <span>Mulai Praktikum</span>
                    <ArrowRight class="w-3 h-3" />
                  </button>
                </div>

                <!-- Rich Rendered Material Content -->
                <div 
                  v-if="mat.content_html"
                  class="text-xs sm:text-sm text-slate-700 leading-relaxed prose prose-sm sm:prose-base max-w-none pt-2 border-t border-slate-200/50"
                  v-html="renderFormula(mat.content_html)"
                ></div>
                <p v-else class="text-xs text-slate-400 italic pt-2 border-t border-slate-200/50">
                  Belum ada penjelasan tertulis pada materi ini.
                </p>
              </div>
            </div>

            <div v-else class="text-center py-8 text-xs text-slate-400">
              Belum ada materi pada modul ini.
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="px-5 py-3 border-t border-slate-100 bg-slate-50 flex items-center justify-between gap-2 shrink-0">
          <span class="text-[11px] text-slate-500 hidden sm:inline">
            Tampilan persis yang dilihat siswa di dashboard mereka.
          </span>
          <div class="flex items-center gap-2 ml-auto">
            <button 
              v-if="previewMaterial"
              @click="openEditMaterial(previewMaterial); showPreviewModal = false"
              class="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 transition-all flex items-center gap-1.5"
            >
              <Edit3 class="w-3.5 h-3.5" />
              <span>Edit Materi</span>
            </button>
            <button 
              @click="showPreviewModal = false"
              class="px-4 py-1.5 rounded-xl text-xs font-bold bg-chemist-dark text-white hover:bg-slate-900 transition-all shadow-xs"
            >
              Tutup Pratinjau
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

