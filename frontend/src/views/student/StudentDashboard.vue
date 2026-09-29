<script setup>
import { ref, onMounted, computed } from 'vue'
import { 
  BookOpen, 
  FlaskConical, 
  CheckSquare, 
  Plus, 
  Search, 
  ChevronRight, 
  Sparkles, 
  ArrowRight,
  UserCheck,
  CheckCircle2,
  AlertCircle
} from 'lucide-vue-next'
import { api } from '@/api/client'
import StoichiometryLab from '@/views/virtual-lab/StoichiometryLab.vue'

const props = defineProps({
  user: Object
})

const emit = defineEmits(['navigate'])

// Tab: 'overview' | 'lab' | 'quiz'
const activeTab = ref('overview')

const classes = ref([])
const selectedClass = ref(null)
const modules = ref([])
const selectedModule = ref(null)
const materials = ref([])
const selectedMaterial = ref(null)

const loading = ref(false)
const enrollCode = ref('')
const enrollLoading = ref(false)
const enrollMessage = ref({ type: '', text: '' })

// Load classes for student
const loadStudentClasses = async () => {
  loading.value = true
  try {
    const res = await api.classes.list(null, true)
    classes.value = res || []
    if (classes.value.length > 0) {
      await selectClass(classes.value[0])
    }
  } catch (err) {
    console.error('Gagal memuat kelas siswa:', err)
  } finally {
    loading.value = false
  }
}

const selectClass = async (cls) => {
  selectedClass.value = cls
  try {
    const mods = await api.content.listModules(cls.id)
    modules.value = mods || []
    if (modules.value.length > 0) {
      await selectModule(modules.value[0])
    } else {
      materials.value = []
      selectedMaterial.value = null
    }
  } catch (err) {
    console.error('Gagal memuat modul:', err)
  }
}

const selectModule = async (mod) => {
  selectedModule.value = mod
  try {
    const mats = await api.content.listMaterials(mod.id)
    materials.value = mats || []
    if (materials.value.length > 0) {
      selectedMaterial.value = materials.value[0]
    } else {
      selectedMaterial.value = null
    }
  } catch (err) {
    console.error('Gagal memuat materi:', err)
  }
}

const handleEnrollByCode = async () => {
  if (!enrollCode.value.trim()) return
  enrollLoading.value = true
  enrollMessage.value = { type: '', text: '' }

  try {
    await api.classes.enrollByCode(enrollCode.value.trim().toUpperCase(), props.user?.id)
    enrollMessage.value = { type: 'success', text: 'Berhasil bergabung ke kelas!' }
    enrollCode.value = ''
    await loadStudentClasses()
  } catch (err) {
    enrollMessage.value = { type: 'error', text: err.message || 'Kode kelas tidak ditemukan.' }
  } finally {
    enrollLoading.value = false
  }
}

const openVirtualLab = (mat = null) => {
  if (mat) selectedMaterial.value = mat
  activeTab.value = 'lab'
}

onMounted(() => {
  loadStudentClasses()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Student Header Banner -->
    <div class="bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold">
          <span class="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
          <span>Portal Belajar Siswa</span>
        </div>
        <h2 class="text-2xl font-bold text-slate-900 tracking-tight">
          Selamat Datang, {{ user?.full_name || 'Siswa' }}! 👋
        </h2>
        <p class="text-xs sm:text-sm text-slate-500 font-normal max-w-xl leading-relaxed">
          Akses modul belajar kimia, eksperimen di laboratorium maya tanpa risiko, dan selesaikan tugas guided inquiry.
        </p>
      </div>

      <!-- Quick Action: Join Class by Code -->
      <div class="w-full md:w-80 bg-slate-50 border border-slate-200/80 p-4 rounded-2xl space-y-2.5">
        <span class="text-xs font-bold text-slate-800 block">Gabung Kelas Baru</span>
        <div class="flex gap-2">
          <input
            v-model="enrollCode"
            type="text"
            placeholder="Kode kelas (cth: CHEM-7X)"
            class="flex-1 bg-white border border-slate-200 text-xs px-3 py-2 rounded-xl outline-none font-mono uppercase"
          />
          <button
            @click="handleEnrollByCode"
            :disabled="enrollLoading || !enrollCode"
            class="bg-chemist-dark hover:bg-slate-900 disabled:opacity-50 text-white text-xs font-semibold px-4 py-2 rounded-xl transition-all shadow-2xs"
          >
            {{ enrollLoading ? '...' : 'Gabung' }}
          </button>
        </div>

        <div v-if="enrollMessage.text" :class="enrollMessage.type === 'success' ? 'text-emerald-600' : 'text-rose-600'" class="text-[11px] font-medium flex items-center gap-1.5">
          <CheckCircle2 v-if="enrollMessage.type === 'success'" class="w-3.5 h-3.5" />
          <AlertCircle v-else class="w-3.5 h-3.5" />
          <span>{{ enrollMessage.text }}</span>
        </div>
      </div>
    </div>

    <!-- Student Navigation Tab -->
    <div class="flex items-center gap-2 border-b border-slate-200 pb-3">
      <button
        @click="activeTab = 'overview'"
        :class="[
          'px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-2',
          activeTab === 'overview'
            ? 'bg-chemist-dark text-white shadow-sm'
            : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
        ]"
      >
        <BookOpen class="w-4 h-4" />
        <span>Modul & Materi Pembelajaran</span>
      </button>

      <button
        @click="activeTab = 'lab'"
        :class="[
          'px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-2',
          activeTab === 'lab'
            ? 'bg-chemist-dark text-white shadow-sm'
            : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
        ]"
      >
        <FlaskConical class="w-4 h-4" />
        <span>Laboratorium Virtual (Praktikum Siswa)</span>
      </button>
    </div>

    <!-- VIEW 1: Overview & Learning Content -->
    <div v-if="activeTab === 'overview'" class="space-y-6">
      <!-- Empty state if student has no classes -->
      <div v-if="classes.length === 0" class="bg-white rounded-3xl border border-slate-200/80 p-12 text-center space-y-3">
        <BookOpen class="w-12 h-12 text-slate-300 mx-auto" />
        <h3 class="text-base font-bold text-slate-800">Kamu Belum Terdaftar di Kelas Manapun</h3>
        <p class="text-xs text-slate-500 max-w-sm mx-auto leading-relaxed">
          Minta kode kelas dari gurumu, lalu masukkan pada formulir "Gabung Kelas Baru" di atas.
        </p>
      </div>

      <!-- Class & Modules Grid -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <!-- Left: Class & Module Selector -->
        <div class="lg:col-span-4 bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1.5">Pilih Kelas</label>
            <select
              :value="selectedClass?.id"
              @change="(e) => selectClass(classes.find(c => c.id === parseInt(e.target.value)))"
              class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-semibold text-slate-800 outline-none"
            >
              <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>

          <div>
            <h4 class="text-xs font-bold text-slate-700 mb-2">Daftar Modul Belajar</h4>
            <div class="space-y-1.5 max-h-72 overflow-y-auto">
              <button
                v-for="mod in modules"
                :key="mod.id"
                @click="selectModule(mod)"
                :class="[
                  'w-full text-left px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all flex items-center justify-between',
                  selectedModule?.id === mod.id
                    ? 'bg-slate-100 text-slate-900 font-bold border border-slate-300'
                    : 'text-slate-600 hover:bg-slate-50 border border-transparent'
                ]"
              >
                <span>{{ mod.title }}</span>
                <ChevronRight class="w-3.5 h-3.5 text-slate-400" />
              </button>
            </div>
          </div>
        </div>

        <!-- Right: Materials Content -->
        <div class="lg:col-span-8 bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-5">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 class="text-base font-bold text-slate-900">{{ selectedModule?.title || 'Pilih Modul' }}</h3>
              <p class="text-xs text-slate-400">Materi teori dan panduan praktikum laboratorium</p>
            </div>

            <button
              @click="openVirtualLab(selectedMaterial)"
              class="inline-flex items-center gap-1.5 px-3.5 py-2 bg-chemist-primary hover:bg-blue-600 text-white rounded-xl text-xs font-semibold transition-all shadow-2xs"
            >
              <FlaskConical class="w-3.5 h-3.5" />
              <span>Buka Lab Virtual</span>
            </button>
          </div>

          <!-- Materials list -->
          <div v-if="materials.length > 0" class="space-y-4">
            <div
              v-for="mat in materials"
              :key="mat.id"
              class="border border-slate-100 bg-slate-50/50 rounded-xl p-4 space-y-2"
            >
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-slate-800">{{ mat.title }}</h4>
                <button
                  @click="openVirtualLab(mat)"
                  class="text-xs text-chemist-primary hover:underline font-semibold flex items-center gap-1"
                >
                  <span>Mulai Praktikum</span>
                  <ArrowRight class="w-3 h-3" />
                </button>
              </div>

              <div 
                v-if="mat.content_html"
                class="text-xs text-slate-600 leading-relaxed prose prose-sm max-w-none pt-2 border-t border-slate-200/50"
                v-html="mat.content_html"
              ></div>
              <p v-else class="text-xs text-slate-400 italic">Belum ada penjelasan tertulis pada materi ini.</p>
            </div>
          </div>

          <div v-else class="text-center py-8 text-xs text-slate-400">
            Belum ada materi pada modul ini.
          </div>
        </div>
      </div>
    </div>

    <!-- VIEW 2: Virtual Lab Student View -->
    <div v-else-if="activeTab === 'lab'" class="space-y-4">
      <div class="bg-white rounded-2xl border border-slate-200/80 p-4 flex items-center justify-between shadow-sm">
        <div>
          <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Laboratorium Siswa</span>
          <h3 class="text-sm font-bold text-slate-900">
            {{ selectedMaterial ? selectedMaterial.title : 'Praktikum Kimia Mandiri' }}
          </h3>
        </div>

        <button
          @click="activeTab = 'overview'"
          class="text-xs font-semibold text-slate-600 hover:text-slate-900 px-3 py-1.5 border border-slate-200 rounded-lg hover:bg-slate-50"
        >
          ← Kembali ke Materi
        </button>
      </div>

      <!-- Stoichiometry Lab Component with student interactions -->
      <StoichiometryLab :material="selectedMaterial" :user="user" />
    </div>
  </div>
</template>
