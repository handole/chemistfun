<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
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
  AlertCircle,
  Play,
  Pause,
  RefreshCw,
  Check,
  Droplets,
  ChevronLeft
} from 'lucide-vue-next'
import { api } from '@/api/client'
import StoichiometryLab from '@/views/virtual-lab/StoichiometryLab.vue'
import StudentQuizTake from '@/views/student/StudentQuizTake.vue'
import { typesetMath } from '@/utils/mathjax'

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
    const mods = await api.content.listModules({
      grade_level: cls.grade_level || null,
      class_id: cls.id
    })
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

    nextTick(() => {
      typesetMath()
    })
  } catch (err) {
    console.error('Gagal memuat materi:', err)
  }
}

// Stage navigation for modules & materials
const currentModuleIndex = computed(() => {
  if (!selectedModule.value || modules.value.length === 0) return -1
  return modules.value.findIndex(m => m.id === selectedModule.value.id)
})

const prevModule = computed(() => {
  const idx = currentModuleIndex.value
  return idx > 0 ? modules.value[idx - 1] : null
})

const nextModule = computed(() => {
  const idx = currentModuleIndex.value
  return idx >= 0 && idx < modules.value.length - 1 ? modules.value[idx + 1] : null
})

const goToPrevModule = () => {
  if (prevModule.value) {
    selectModule(prevModule.value)
  }
}

const goToNextModule = () => {
  if (nextModule.value) {
    selectModule(nextModule.value)
  }
}

const currentMaterialIndex = computed(() => {
  if (!selectedMaterial.value || materials.value.length === 0) return -1
  return materials.value.findIndex(m => m.id === selectedMaterial.value.id)
})

const prevMaterial = computed(() => {
  const idx = currentMaterialIndex.value
  return idx > 0 ? materials.value[idx - 1] : null
})

const nextMaterial = computed(() => {
  const idx = currentMaterialIndex.value
  return idx >= 0 && idx < materials.value.length - 1 ? materials.value[idx + 1] : null
})

const goToPrevMaterial = () => {
  if (prevMaterial.value) {
    selectedMaterial.value = prevMaterial.value
  }
}

const goToNextMaterial = () => {
  if (nextMaterial.value) {
    selectedMaterial.value = nextMaterial.value
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

// Interactive Student Custom Lab State
const studentLabVolume = ref(0)
const studentIsTitrating = ref(false)
let studentTitrationTimer = null
const studentNotes = ref('')
const studentNotesSaved = ref(false)

const studentEqVolume = computed(() => {
  if (!customLabConfig.value?.config_data) return 25
  const cfg = customLabConfig.value.config_data
  const m1 = cfg.solution_molarity || 0.1
  const m2 = cfg.titrant_molarity || 0.1
  const v1 = 25
  return +((m1 * v1) / (m2 || 1)).toFixed(1)
})

const studentLiquidColor = computed(() => {
  if (!customLabConfig.value?.config_data) return 'rgba(224, 242, 254, 0.5)'
  const cfg = customLabConfig.value.config_data
  if (studentLabVolume.value >= studentEqVolume.value) {
    return cfg.color_end || 'rgba(244, 114, 182, 0.8)'
  }
  return cfg.color_start || 'rgba(224, 242, 254, 0.5)'
})

const studentPhValue = computed(() => {
  const eq = studentEqVolume.value || 25
  const maxV = customLabConfig.value?.config_data?.max_volume_ml || 50
  if (studentLabVolume.value < eq) {
    const diff = (eq - studentLabVolume.value) / eq
    return (1.0 + (1 - diff) * 6.0).toFixed(1)
  } else if (Math.abs(studentLabVolume.value - eq) < 0.2) {
    return '7.0'
  } else {
    const diff = (studentLabVolume.value - eq) / maxV
    return Math.min(14.0, +(7.0 + diff * 7.0)).toFixed(1)
  }
})

const studentReactionStatus = computed(() => {
  const eq = studentEqVolume.value || 25
  if (studentLabVolume.value < eq) return 'Asam Berlebih (Belum Netral)'
  if (Math.abs(studentLabVolume.value - eq) < 0.2) return 'Titik Ekuivalen Netral'
  return 'Basa Berlebih (Lewat Titik Akhir)'
})

const toggleStudentTitration = () => {
  studentIsTitrating.value = !studentIsTitrating.value
  if (studentIsTitrating.value) {
    studentTitrationTimer = setInterval(() => {
      const maxV = customLabConfig.value?.config_data?.max_volume_ml || 50
      if (!studentIsTitrating.value || studentLabVolume.value >= maxV) {
        clearInterval(studentTitrationTimer)
        studentIsTitrating.value = false
      } else {
        studentLabVolume.value = +(studentLabVolume.value + 0.5).toFixed(1)
      }
    }, 150)
  } else {
    clearInterval(studentTitrationTimer)
  }
}

const addStudentDrop = () => {
  const maxV = customLabConfig.value?.config_data?.max_volume_ml || 50
  if (studentLabVolume.value < maxV) {
    studentLabVolume.value = +(studentLabVolume.value + 0.5).toFixed(1)
  }
}

const resetStudentSimulation = () => {
  if (studentTitrationTimer) clearInterval(studentTitrationTimer)
  studentIsTitrating.value = false
  studentLabVolume.value = 0
}

const saveStudentNotes = () => {
  studentNotesSaved.value = true
  setTimeout(() => (studentNotesSaved.value = false), 3000)
}

const openVirtualLab = async (mat = null) => {
  resetStudentSimulation()
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

      <!-- Active Class Badge / Selector (Jika punya kelas) -->
      <div v-if="classes.length > 0" class="w-full md:w-auto bg-slate-50 border border-slate-200/80 p-3 rounded-2xl flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-chemist-primary/10 text-chemist-primary flex items-center justify-center font-bold shrink-0">
          <BookOpen class="w-5 h-5" />
        </div>
        <div>
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Kelas Terdaftar</span>
          <select
            v-if="classes.length > 1"
            :value="selectedClass?.id"
            @change="(e) => selectClass(classes.find(c => c.id === parseInt(e.target.value)))"
            class="bg-transparent font-bold text-slate-900 text-sm outline-none cursor-pointer pr-4"
          >
            <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
          <span v-else class="text-sm font-bold text-slate-900 block">{{ selectedClass?.name || classes[0].name }}</span>
          <span class="text-[11px] text-emerald-600 font-semibold flex items-center gap-1 mt-0.5">
            <CheckCircle2 class="w-3 h-3" />
            <span>Kelas {{ selectedClass?.grade_level || classes[0].grade_level }} Kimia Aktif</span>
          </span>
        </div>
      </div>

      <!-- Quick Action: Join Class by Code (Hanya tampil jika belum punya kelas) -->
      <div v-else class="w-full md:w-80 bg-slate-50 border border-slate-200/80 p-4 rounded-2xl space-y-2.5">
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
      <div v-else class="space-y-4">
        <!-- Materials Content -->
        <div class="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-5">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 flex-wrap gap-3">
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-[10px] font-bold uppercase tracking-wider bg-blue-50 text-chemist-primary px-2.5 py-1 rounded-md">
                  Kelas {{ selectedClass?.grade_level || classes[0]?.grade_level }}
                </span>
                <span v-if="modules.length > 0" class="text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700 px-2.5 py-1 rounded-md">
                  Modul {{ currentModuleIndex + 1 }} dari {{ modules.length }}
                </span>
                <span v-if="materials.length > 0" class="text-[10px] font-semibold text-slate-400">
                  {{ materials.length }} Materi
                </span>
              </div>
              <h3 class="text-lg font-bold text-slate-900 mt-2">{{ selectedModule?.title || 'Pilih Modul' }}</h3>
              <p class="text-xs text-slate-400">Materi teori dan panduan praktikum laboratorium</p>
            </div>

            <!-- Quick Module Navigation & Actions -->
            <div class="flex items-center gap-2 flex-wrap">
              <div v-if="modules.length > 1" class="flex items-center gap-1 bg-slate-50 border border-slate-200 p-1 rounded-xl">
                <button
                  @click="goToPrevModule"
                  :disabled="!prevModule"
                  class="p-1.5 hover:bg-white rounded-lg text-slate-600 disabled:opacity-30 disabled:hover:bg-transparent transition-all"
                  title="Modul Sebelumnya"
                >
                  <ChevronLeft class="w-4 h-4" />
                </button>
                <span class="text-xs font-semibold px-2 text-slate-700">
                  Modul {{ currentModuleIndex + 1 }}/{{ modules.length }}
                </span>
                <button
                  @click="goToNextModule"
                  :disabled="!nextModule"
                  class="p-1.5 hover:bg-white rounded-lg text-slate-600 disabled:opacity-30 disabled:hover:bg-transparent transition-all"
                  title="Modul Selanjutnya"
                >
                  <ChevronRight class="w-4 h-4" />
                </button>
              </div>

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

          <!-- Materials list with stage progression -->
          <div v-if="materials.length > 0" class="space-y-4">
            <div
              v-for="(mat, matIdx) in materials"
              :key="mat.id"
              :class="[
                'border rounded-xl p-4 space-y-2 transition-all',
                selectedMaterial?.id === mat.id
                  ? 'border-chemist-primary/60 bg-blue-50/20 ring-1 ring-chemist-primary/30'
                  : 'border-slate-100 bg-slate-50/50'
              ]"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span 
                    class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold"
                    :class="selectedMaterial?.id === mat.id ? 'bg-chemist-primary text-white' : 'bg-slate-200 text-slate-600'"
                  >
                    {{ matIdx + 1 }}
                  </span>
                  <h4 class="text-sm font-bold text-slate-800">{{ mat.title }}</h4>
                </div>
                <div class="flex items-center gap-3">
                  <button
                    v-if="selectedMaterial?.id !== mat.id"
                    @click="selectedMaterial = mat"
                    class="text-xs text-slate-500 hover:text-slate-800 font-semibold"
                  >
                    Buka Rincian
                  </button>
                  <button
                    @click="openVirtualLab(mat)"
                    class="text-xs text-chemist-primary hover:underline font-semibold flex items-center gap-1"
                  >
                    <span>Mulai Praktikum</span>
                    <ArrowRight class="w-3 h-3" />
                  </button>
                </div>
              </div>

              <div 
                v-if="mat.content_html"
                class="text-xs text-slate-600 leading-relaxed prose prose-sm max-w-none pt-2 border-t border-slate-200/50"
                v-html="mat.content_html"
              ></div>
              <p v-else class="text-xs text-slate-400 italic">Belum ada penjelasan tertulis pada materi ini.</p>
            </div>

            <!-- Material Stage Navigation Controls -->
            <div class="pt-2 flex items-center justify-between bg-slate-50 p-3 rounded-xl border border-slate-200/70">
              <button
                @click="goToPrevMaterial"
                :disabled="!prevMaterial"
                class="px-3 py-1.5 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:hover:bg-white border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 flex items-center gap-1.5 transition-all shadow-2xs"
              >
                <ChevronLeft class="w-3.5 h-3.5" />
                <span>Materi Sebelumnya</span>
              </button>

              <span class="text-xs font-medium text-slate-500">
                Materi <b>{{ currentMaterialIndex + 1 }}</b> dari <b>{{ materials.length }}</b>
              </span>

              <button
                v-if="nextMaterial"
                @click="goToNextMaterial"
                class="px-3.5 py-1.5 bg-chemist-primary hover:bg-blue-600 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-2xs"
              >
                <span>Materi Selanjutnya</span>
                <ChevronRight class="w-3.5 h-3.5" />
              </button>

              <button
                v-else-if="nextModule"
                @click="goToNextModule"
                class="px-3.5 py-1.5 bg-chemist-dark hover:bg-slate-900 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-2xs"
              >
                <span>Lanjut ke Modul Berikutnya</span>
                <ChevronRight class="w-3.5 h-3.5" />
              </button>

              <button
                v-else-if="activeQuiz"
                @click="startTakingQuiz(activeQuiz)"
                class="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-2xs"
              >
                <CheckSquare class="w-3.5 h-3.5" />
                <span>Selesai Belajar, Ikuti Kuis</span>
              </button>
              <div v-else class="text-xs font-bold text-emerald-600">
                ✓ Selesai Semua Materi
              </div>
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

      <!-- Custom Lab Simulation (Configured by Teacher) -->
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

        <!-- Student Interaction Titration Canvas -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <!-- Left: Simulation Canvas (7 Cols) -->
          <div class="lg:col-span-7 bg-slate-50 rounded-2xl border border-slate-200/80 p-5 space-y-4">
            <div class="flex items-center justify-between text-xs">
              <span class="font-bold text-slate-700">Simulasi Titrasi Langsung</span>
              <button 
                @click="resetStudentSimulation"
                class="p-1.5 text-slate-500 hover:text-slate-800 rounded-lg hover:bg-slate-200/60 transition-colors flex items-center gap-1 font-semibold"
                title="Reset Percobaan"
              >
                <RefreshCw class="w-3.5 h-3.5" />
                <span>Reset</span>
              </button>
            </div>

            <!-- Beaker & Titration Apparatus Canvas -->
            <div class="h-72 bg-gradient-to-b from-slate-100 to-slate-50 rounded-2xl border border-slate-200 relative flex items-center justify-center overflow-hidden">
              <!-- Buret tip above -->
              <div class="absolute top-2 w-3.5 h-20 bg-slate-300 rounded-b flex flex-col justify-end items-center shadow-xs">
                <span v-if="studentIsTitrating" class="w-1.5 h-1.5 rounded-full bg-blue-500 animate-ping mb-1"></span>
              </div>

              <!-- Erlenmeyer Flask Simulation -->
              <div class="w-40 h-48 relative flex flex-col items-center justify-end">
                <!-- Flask Neck -->
                <div class="w-10 h-14 border-l-2 border-r-2 border-slate-400 bg-transparent z-10"></div>
                
                <!-- Flask Body (Triangular Trapeze) -->
                <div 
                  class="w-40 h-34 border-2 border-slate-400 rounded-b-2xl relative overflow-hidden flex flex-col justify-end p-1 transition-colors duration-500 shadow-inner"
                  :style="{ backgroundColor: studentLiquidColor }"
                >
                  <!-- Liquid level wave -->
                  <div 
                    class="w-full rounded-b-xl transition-all duration-300 relative"
                    :style="{ 
                      height: `${Math.min(25 + studentLabVolume * 1.3, 92)}%`, 
                      backgroundColor: studentLiquidColor 
                    }"
                  >
                    <div v-if="studentIsTitrating" class="absolute inset-0 bg-white/20 animate-pulse"></div>
                  </div>

                  <!-- Measurement Lines -->
                  <div class="absolute left-2 top-4 text-[9px] font-mono text-slate-400 space-y-2 pointer-events-none">
                    <div>- 50ml</div>
                    <div>- 25ml</div>
                    <div>- 10ml</div>
                  </div>
                </div>
              </div>

              <!-- Floating Telemetry Card -->
              <div class="absolute right-3 bottom-3 bg-white/95 backdrop-blur-md p-3 rounded-xl border border-slate-200 shadow-sm text-xs space-y-1.5 max-w-[180px]">
                <div class="flex items-center justify-between gap-2">
                  <span class="text-slate-400 text-[11px]">pH Larutan:</span>
                  <span class="font-mono font-bold text-slate-900 text-sm">{{ studentPhValue }}</span>
                </div>
                <div class="flex items-center justify-between gap-2">
                  <span class="text-slate-400 text-[11px]">Titran Masuk:</span>
                  <span class="font-mono font-bold text-chemist-primary text-sm">{{ studentLabVolume }} mL</span>
                </div>
                <div class="pt-1 border-t border-slate-100">
                  <span 
                    class="text-[10px] font-bold px-1.5 py-0.5 rounded block text-center truncate"
                    :class="studentLabVolume >= studentEqVolume ? 'bg-pink-100 text-pink-700' : 'bg-blue-100 text-blue-700'"
                  >
                    {{ studentReactionStatus }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Controls for Student -->
            <div class="space-y-3 pt-1">
              <div class="flex items-center justify-between text-xs font-semibold text-slate-700">
                <span>Aliran Kran Buret (Volume Titran):</span>
                <span class="font-mono font-bold text-slate-900">{{ studentLabVolume }} / {{ customLabConfig.config_data?.max_volume_ml || 50 }} mL</span>
              </div>

              <input 
                type="range" 
                min="0" 
                :max="customLabConfig.config_data?.max_volume_ml || 50" 
                step="0.5"
                v-model.number="studentLabVolume"
                class="w-full accent-chemist-primary cursor-pointer"
              />

              <div class="flex items-center gap-2 pt-1 flex-wrap sm:flex-nowrap">
                <button 
                  @click="toggleStudentTitration"
                  class="flex-1 py-2 px-3 rounded-xl text-xs font-bold text-white transition-all flex items-center justify-center gap-2 shadow-2xs"
                  :class="studentIsTitrating ? 'bg-rose-500 hover:bg-rose-600' : 'bg-chemist-primary hover:bg-blue-600'"
                >
                  <Pause v-if="studentIsTitrating" class="w-3.5 h-3.5" />
                  <Play v-else class="w-3.5 h-3.5" />
                  <span>{{ studentIsTitrating ? 'Tutup Kran Buret' : 'Buka Kran Otomatis' }}</span>
                </button>

                <button 
                  @click="addStudentDrop"
                  class="py-2 px-3 rounded-xl text-xs font-bold bg-white text-slate-700 border border-slate-200 hover:bg-slate-100 flex items-center gap-1.5 shadow-2xs"
                  title="Tambah tetesan 0.5 mL"
                >
                  <Droplets class="w-3.5 h-3.5 text-sky-500" />
                  <span>+0.5 mL</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Right: Observation & Analysis Sheet (5 Cols) -->
          <div class="lg:col-span-5 bg-white border border-slate-200/80 rounded-2xl p-5 space-y-4">
            <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
              <span>Lembar Data Pengamatan Praktikum</span>
            </h4>

            <div class="space-y-3 text-xs">
              <div class="grid grid-cols-2 gap-2">
                <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                  <span class="text-[10px] text-slate-400 block font-medium">Warna Awal</span>
                  <div class="flex items-center gap-1.5 mt-1">
                    <span 
                      class="w-3.5 h-3.5 rounded-full border border-slate-300"
                      :style="{ backgroundColor: customLabConfig.config_data?.color_start || '#F8FAFC' }"
                    ></span>
                    <span class="font-mono text-[11px] text-slate-700 font-semibold truncate">{{ customLabConfig.config_data?.color_start || '#F8FAFC' }}</span>
                  </div>
                </div>

                <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                  <span class="text-[10px] text-slate-400 block font-medium">Warna Titik Akhir</span>
                  <div class="flex items-center gap-1.5 mt-1">
                    <span 
                      class="w-3.5 h-3.5 rounded-full border border-slate-300"
                      :style="{ backgroundColor: customLabConfig.config_data?.color_end || '#F472B6' }"
                    ></span>
                    <span class="font-mono text-[11px] text-slate-700 font-semibold truncate">{{ customLabConfig.config_data?.color_end || '#F472B6' }}</span>
                  </div>
                </div>
              </div>

              <div class="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-1">
                <span class="text-[10px] text-slate-400 block font-medium">Indikator Terpasang</span>
                <span class="font-semibold text-slate-800">{{ customLabConfig.config_data?.indicator_type || 'Phenolphthalein (PP)' }}</span>
              </div>

              <!-- Titration Telemetry Data -->
              <div class="p-3 bg-blue-50/50 border border-blue-200/60 rounded-xl space-y-2">
                <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Hasil Pengamatan Buret</span>
                <div class="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span class="text-[10px] text-slate-400 block">Volume Terukur</span>
                    <span class="font-mono font-bold text-slate-900 text-sm">{{ studentLabVolume }} mL</span>
                  </div>
                  <div>
                    <span class="text-[10px] text-slate-400 block">pH Larutan</span>
                    <span class="font-mono font-bold text-slate-900 text-sm">{{ studentPhValue }}</span>
                  </div>
                </div>
                <div class="pt-1.5 border-t border-blue-200/40">
                  <span class="text-[11px] font-medium text-slate-700">
                    Status: <b :class="studentLabVolume >= studentEqVolume ? 'text-pink-600' : 'text-blue-600'">{{ studentReactionStatus }}</b>
                  </span>
                </div>
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
