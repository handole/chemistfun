<script setup>
import { ref, onMounted, watch } from 'vue'
import { Plus, BookOpen, FileText, CheckCircle, Eye, EyeOff, Trash2, Edit3, FlaskConical, AlertCircle } from 'lucide-vue-next'
import { api } from '@/api/client'

const props = defineProps({
  user: Object
})

const emit = defineEmits(['open-lab'])

const classes = ref([])
const selectedClassId = ref(null)
const modules = ref([])
const selectedModule = ref(null)
const materials = ref([])

const loadingClasses = ref(true)
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

const loadClasses = async () => {
  loadingClasses.value = true
  try {
    const res = await api.classes.list()
    classes.value = res || []
    if (classes.value.length > 0) {
      selectedClassId.value = classes.value[0].id
    }
  } catch (err) {
    console.error('Gagal mengambil kelas:', err)
  } finally {
    loadingClasses.value = false
  }
}

const loadModules = async () => {
  if (!selectedClassId.value) return
  loadingModules.value = true
  try {
    const res = await api.content.listModules(selectedClassId.value)
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
  } catch (err) {
    console.error('Gagal mengambil materi:', err)
  } finally {
    loadingMaterials.value = false
  }
}

watch(selectedClassId, () => {
  loadModules()
})

// Module Actions
const handleCreateModule = async () => {
  if (!newModuleTitle.value.trim()) return
  try {
    const res = await api.content.createModule({
      class_id: selectedClassId.value,
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
  materialForm.value = {
    uuid: null,
    title: '',
    content_html: '',
    order_index: (materials.value.length + 1),
    is_published: true
  }
  showMaterialModal.value = true
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
  loadClasses()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header with Class Selector -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-extrabold text-slate-900 tracking-tight">Kurikulum & Modul Pembelajaran</h2>
        <p class="text-xs text-slate-500 font-medium mt-1">Susun topik pembelajaran kimia, buat artikel materi teori, dan atur status publikasi untuk siswa.</p>
      </div>

      <!-- Class Select Box -->
      <div class="flex items-center gap-2 self-start sm:self-auto">
        <label class="text-xs font-bold text-slate-500 whitespace-nowrap">Pilih Kelas:</label>
        <select 
          v-model="selectedClassId"
          class="bg-white text-xs font-bold px-3 py-2 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none shadow-2xs"
        >
          <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
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

            <button 
              @click="openCreateMaterial"
              class="inline-flex items-center gap-2 bg-chemist-dark hover:bg-slate-900 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow-sm self-start transition-all active:scale-95"
            >
              <Plus class="w-4 h-4 text-emerald-400" />
              <span>Tambah Materi</span>
            </button>
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
              <div class="flex items-start justify-between gap-4">
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <h5 class="font-bold text-slate-900 text-sm">{{ mat.title }}</h5>
                    <!-- Publish Badge -->
                    <span 
                      class="text-[10px] font-bold px-2 py-0.5 rounded-full"
                      :class="mat.is_published ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'"
                    >
                      {{ mat.is_published ? 'Terkirim ke Siswa' : 'Draft Guru' }}
                    </span>
                  </div>

                  <p class="text-xs text-slate-500 line-clamp-2" v-if="mat.content_html">
                    {{ mat.content_html }}
                  </p>
                  <p class="text-xs text-slate-400 italic" v-else>Belum ada isi materi.</p>
                </div>

                <!-- Actions Button Group -->
                <div class="flex items-center gap-1.5 shrink-0">
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

                  <!-- Open Virtual Lab Config -->
                  <button 
                    @click="emit('open-lab', mat)"
                    class="p-2 rounded-xl text-sky-600 hover:bg-sky-50 border border-transparent hover:border-sky-200 transition-colors"
                    title="Konfigurasi Lab Virtual"
                  >
                    <FlaskConical class="w-4 h-4" />
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
  </div>
</template>

