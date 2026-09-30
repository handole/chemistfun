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
import StudentQuizTake from '@/views/student/StudentQuizTake.vue'

const props = defineProps({
  user: Object
})

const emit = defineEmits(['navigate'])

// Tab: 'overview' | 'lab' | 'quiz'
const activeTab = ref('overview')
const labMode = ref('stoichiometry') // 'stoichiometry' | 'custom'
const customLabConfig = ref(null)

const classes = ref([])
const selectedClass = ref(null)
const modules = ref([])
const selectedModule = ref(null)
const materials = ref([])
const selectedMaterial = ref(null)

// Quiz & Assessment State
const activeQuiz = ref(null)
const takingQuiz = ref(false)
const quizHistory = ref([])
const loadingQuiz = ref(false)

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

    // Load module quiz if exists
    try {
      const q = await api.assessment.getQuizByModule(mod.id)
      activeQuiz.value = q || null
    } catch (e) {
      activeQuiz.value = null
    }
  } catch (err) {
    console.error('Gagal memuat materi:', err)
  }
}

const loadStudentAttempts = async () => {
  loadingQuiz.value = true
  try {
    const attempts = await api.assessment.listAttempts()
    quizHistory.value = attempts || []
  } catch (e) {
    console.warn('Gagal memuat riwayat kuis:', e)
  } finally {
    loadingQuiz.value = false
  }
}

const startTakingQuiz = (quiz) => {
  activeQuiz.value = quiz
  takingQuiz.value = true
  activeTab.value = 'quiz'
}

const finishQuizSession = async () => {
  takingQuiz.value = false
  await loadStudentAttempts()
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

const openVirtualLab = async (mat = null) => {
  if (mat) {
    selectedMaterial.value = mat
    try {
      const lab = await api.content.getLab(mat.uuid)
      if (lab && lab.config_data && Object.keys(lab.config_data).length > 0) {
        customLabConfig.value = lab
        labMode.value = 'custom'
      } else {
        customLabConfig.value = null
        labMode.value = 'stoichiometry'
      }
    } catch (e) {
      customLabConfig.value = null
      labMode.value = 'stoichiometry'
    }
  }
  activeTab.value = 'lab'
}

onMounted(() => {
  loadStudentClasses()
  loadStudentAttempts()
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

      <button
        @click="activeTab = 'quiz'; takingQuiz = false"
        :class="[
          'px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-2',
          activeTab === 'quiz'
            ? 'bg-chemist-dark text-white shadow-sm'
            : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
        ]"
      >
        <CheckSquare class="w-4 h-4" />
        <span>Kuis & Asesmen Radar</span>
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

            <div class="flex items-center gap-2">
              <button
                v-if="activeQuiz"
                @click="startTakingQuiz(activeQuiz)"
                class="inline-flex items-center gap-1.5 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold transition-all shadow-2xs"
              >
                <CheckSquare class="w-3.5 h-3.5" />
                <span>Kerjakan Kuis</span>
              </button>

              <button
                @click="openVirtualLab(selectedMaterial)"
                class="inline-flex items-center gap-1.5 px-3.5 py-2 bg-chemist-primary hover:bg-blue-600 text-white rounded-xl text-xs font-semibold transition-all shadow-2xs"
              >
                <FlaskConical class="w-3.5 h-3.5" />
                <span>Buka Lab Virtual</span>
              </button>
            </div>
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
      <div class="bg-white rounded-2xl border border-slate-200/80 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm">
        <div class="flex items-center gap-3">
          <div>
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Laboratorium Siswa</span>
            <h3 class="text-sm font-bold text-slate-900">
              {{ selectedMaterial ? selectedMaterial.title : 'Praktikum Kimia Mandiri' }}
            </h3>
          </div>
          <!-- Switch mode badge if custom lab from teacher exists -->
          <div v-if="customLabConfig" class="flex gap-1 bg-slate-100 p-1 rounded-xl text-xs">
            <button
              @click="labMode = 'custom'"
              :class="labMode === 'custom' ? 'bg-white shadow-2xs font-bold text-slate-800' : 'text-slate-500'"
              class="px-2.5 py-1 rounded-lg transition-all"
            >
              Lab Guru: {{ customLabConfig.config_data?.lab_title || 'Titrasi' }}
            </button>
            <button
              @click="labMode = 'stoichiometry'"
              :class="labMode === 'stoichiometry' ? 'bg-white shadow-2xs font-bold text-slate-800' : 'text-slate-500'"
              class="px-2.5 py-1 rounded-lg transition-all"
            >
              Lab Standar Stoikiometri
            </button>
          </div>
        </div>

        <button
          @click="activeTab = 'overview'"
          class="text-xs font-semibold text-slate-600 hover:text-slate-900 px-3 py-1.5 border border-slate-200 rounded-lg hover:bg-slate-50 self-start sm:self-center"
        >
          ← Kembali ke Materi
        </button>
      </div>

      <!-- Custom Lab Simulation (Configured by Teacher/AI) -->
      <div v-if="labMode === 'custom' && customLabConfig" class="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-card space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[11px] font-semibold mb-1">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              <span>Eksperimen Aktif</span>
            </div>
            <h2 class="text-lg font-bold text-slate-900">{{ customLabConfig.config_data?.lab_title }}</h2>
            <p class="text-xs text-slate-500">{{ customLabConfig.config_data?.instructions || 'Ikuti petunjuk praktikum untuk menyelesaikan simulasi.' }}</p>
          </div>

          <div class="flex gap-2">
            <div class="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-center">
              <span class="block text-[10px] text-slate-400 font-bold uppercase">Analit</span>
              <span class="text-xs font-bold text-slate-800">{{ customLabConfig.config_data?.solution_name }} ({{ customLabConfig.config_data?.solution_molarity }}M)</span>
            </div>
            <div class="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-center">
              <span class="block text-[10px] text-slate-400 font-bold uppercase">Titran</span>
              <span class="text-xs font-bold text-slate-800">{{ customLabConfig.config_data?.titrant_name }} ({{ customLabConfig.config_data?.titrant_molarity }}M)</span>
            </div>
          </div>
        </div>

        <!-- Student Interaction Beaker Canvas -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
          <div class="flex flex-col items-center justify-center p-6 bg-slate-50 rounded-2xl border border-slate-200">
            <!-- Beaker Visual representation -->
            <div class="w-40 h-56 border-4 border-slate-400 border-t-0 rounded-b-3xl relative flex flex-col justify-end p-2 bg-white/70 overflow-hidden shadow-inner">
              <div 
                class="w-full transition-all duration-300 rounded-b-2xl relative"
                :style="{
                  height: '60%',
                  backgroundColor: customLabConfig.config_data?.color_end || '#F472B6'
                }"
              >
                <div class="absolute inset-0 bg-white/20 animate-pulse"></div>
              </div>
            </div>
            <span class="text-xs text-slate-500 font-medium mt-3">Indikator: <strong class="text-slate-800">{{ customLabConfig.config_data?.indicator_type || 'Phenolphthalein' }}</strong></span>
          </div>

          <div class="space-y-4">
            <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Lembar Catatan Pengamatan Siswa</h4>
            <div class="space-y-2 text-xs">
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Warna Awal Larutan</label>
                <input 
                  type="text" 
                  disabled 
                  :value="customLabConfig.config_data?.color_start || '#F8FAFC'"
                  class="w-full bg-slate-100 text-slate-600 px-3 py-2 rounded-xl border border-slate-200 font-mono text-xs"
                />
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Warna Titik Akhir Reaksi</label>
                <input 
                  type="text" 
                  disabled 
                  :value="customLabConfig.config_data?.color_end || '#F472B6'"
                  class="w-full bg-slate-100 text-slate-600 px-3 py-2 rounded-xl border border-slate-200 font-mono text-xs"
                />
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Catatan Analisis Siswa</label>
                <textarea 
                  rows="3" 
                  placeholder="Tuliskan kesimpulan perubahan warna dan konsentrasi hasil percobaan..." 
                  class="w-full bg-white px-3 py-2 rounded-xl border border-slate-200 outline-none text-xs text-slate-800"
                ></textarea>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Stoichiometry Lab Component with student interactions -->
      <StoichiometryLab v-else :material="selectedMaterial" :user="user" />
    </div>

    <!-- VIEW 3: Student Quiz & Assessment View -->
    <div v-else-if="activeTab === 'quiz'" class="space-y-6">
      <!-- Active Quiz Execution Component -->
      <StudentQuizTake 
        v-if="takingQuiz && activeQuiz"
        :quiz="activeQuiz"
        :student="user"
        @back="takingQuiz = false"
        @finish="finishQuizSession"
      />

      <!-- Quiz Listing & History Dashboard -->
      <div v-else class="space-y-6">
        <!-- Available Quiz Banner -->
        <div class="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm space-y-4">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <span class="text-[11px] font-bold text-chemist-primary bg-blue-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                Asesmen Modul Aktif
              </span>
              <h3 class="text-base font-bold text-slate-900 mt-1">
                {{ selectedModule ? selectedModule.title : 'Pilih Modul Pembelajaran' }}
              </h3>
              <p class="text-xs text-slate-500">Uji pemahaman konsep, hitungan reaksi, dan keterampilan praktikum kimia kamu.</p>
            </div>

            <div v-if="activeQuiz">
              <button
                @click="startTakingQuiz(activeQuiz)"
                class="inline-flex items-center gap-2 px-5 py-2.5 bg-chemist-dark hover:bg-slate-900 text-white rounded-xl text-xs font-bold transition-all shadow-md active:scale-95"
              >
                <CheckSquare class="w-4 h-4 text-emerald-400" />
                <span>{{ activeQuiz.title || 'Mulai Kerjakan Kuis' }}</span>
              </button>
            </div>
            <div v-else class="text-xs text-slate-400 italic bg-slate-50 px-3 py-2 rounded-xl border border-slate-200">
              Belum ada kuis yang diterbitkan untuk modul ini.
            </div>
          </div>

          <div v-if="activeQuiz" class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div class="bg-slate-50 border border-slate-200/80 rounded-xl p-3">
              <span class="text-[10px] font-bold text-slate-400 uppercase block">Batas Waktu</span>
              <span class="font-bold text-slate-800">{{ activeQuiz.time_limit_minutes }} Menit</span>
            </div>
            <div class="bg-slate-50 border border-slate-200/80 rounded-xl p-3">
              <span class="text-[10px] font-bold text-slate-400 uppercase block">Passing Grade (KKM)</span>
              <span class="font-bold text-slate-800">70 / 100</span>
            </div>
            <div class="bg-slate-50 border border-slate-200/80 rounded-xl p-3">
              <span class="text-[10px] font-bold text-slate-400 uppercase block">Tipe Penilaian</span>
              <span class="font-bold text-slate-800">Radar Kompetensi</span>
            </div>
            <div class="bg-slate-50 border border-slate-200/80 rounded-xl p-3">
              <span class="text-[10px] font-bold text-slate-400 uppercase block">Status Kuis</span>
              <span class="font-bold text-emerald-600">Aktif & Terbuka</span>
            </div>
          </div>
        </div>

        <!-- Student Quiz History Table -->
        <div class="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-sm font-bold text-slate-900">Riwayat Pengerjaan Kuis Siswa</h4>
              <p class="text-xs text-slate-400">Daftar rekam jejak nilai dan radar sains kamu.</p>
            </div>
            <button 
              @click="loadStudentAttempts" 
              class="text-xs text-chemist-primary hover:underline font-semibold"
            >
              Segarkan
            </button>
          </div>

          <!-- Attempts list -->
          <div v-if="loadingQuiz" class="text-center py-8 text-xs text-slate-400">
            Memuat riwayat kuis...
          </div>
          <div v-else-if="quizHistory.length === 0" class="text-center py-8 text-xs text-slate-400">
            Kamu belum pernah mengerjakan kuis. Klik "Mulai Kerjakan Kuis" di atas.
          </div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead>
                <tr class="border-b border-slate-100 text-slate-400 font-semibold">
                  <th class="pb-3">Kuis ID</th>
                  <th class="pb-3">Waktu Mulai</th>
                  <th class="pb-3">Waktu Selesai</th>
                  <th class="pb-3">Skor Akhir</th>
                  <th class="pb-3">Capaian Radar</th>
                  <th class="pb-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="att in quizHistory" :key="att.id" class="text-slate-700">
                  <td class="py-3 font-mono font-bold text-slate-900">#{{ att.quiz_id }}</td>
                  <td class="py-3 text-slate-500">{{ new Date(att.started_at).toLocaleString('id-ID') }}</td>
                  <td class="py-3 text-slate-500">
                    {{ att.completed_at ? new Date(att.completed_at).toLocaleString('id-ID') : '-' }}
                  </td>
                  <td class="py-3">
                    <span 
                      v-if="att.completed_at"
                      :class="att.total_score >= 70 ? 'text-emerald-600 bg-emerald-50 border-emerald-200' : 'text-amber-600 bg-amber-50 border-amber-200'"
                      class="px-2.5 py-0.5 rounded-full border font-bold text-[11px]"
                    >
                      {{ att.total_score }} / 100
                    </span>
                    <span v-else class="text-slate-400 italic">Sedang berjalan</span>
                  </td>
                  <td class="py-3">
                    <div v-if="att.radar_snapshot" class="flex flex-wrap gap-1 max-w-xs">
                      <span 
                        v-for="(val, k) in att.radar_snapshot" 
                        :key="k"
                        class="text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded"
                      >
                        {{ k }}: {{ val }}%
                      </span>
                    </div>
                    <span v-else class="text-slate-400 text-[10px]">-</span>
                  </td>
                  <td class="py-3 text-right font-semibold">
                    <span v-if="att.completed_at" class="text-emerald-600">Selesai</span>
                    <span v-else class="text-blue-600">Belum Disubmit</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
