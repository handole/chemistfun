<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { 
  BookOpen, 
  FlaskConical, 
  CheckSquare, 
  ChevronRight, 
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Play,
  Pause,
  RefreshCw,
  Droplets,
  ChevronLeft
} from 'lucide-vue-next'
import { api } from '@/api/client'
import StoichiometryLab from '@/views/virtual-lab/StoichiometryLab.vue'
import StudentQuizTake from '@/views/student/StudentQuizTake.vue'
import { renderFormula } from '@/utils/formula'

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

const getAttemptMetrics = (att) => {
  if (att.radar_chart_data?.metrics && Array.isArray(att.radar_chart_data.metrics)) {
    return att.radar_chart_data.metrics.map(m => ({
      name: m.metric_name,
      val: Math.round(m.score_percentage || 0)
    }))
  }
  if (att.radar_snapshot && typeof att.radar_snapshot === 'object') {
    return Object.entries(att.radar_snapshot).map(([k, val]) => ({
      name: k.replace(/_/g, ' '),
      val: Number(val) || 0
    }))
  }
  return []
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
    <!-- Student header: quiet label, name as the heading, one next action -->
    <div class="flex flex-col items-start justify-between gap-5 rounded-xl border border-line bg-surface p-5 sm:p-6 md:flex-row md:items-center">
      <div class="max-w-xl">
        <p class="text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Portal belajar</p>
        <h1 class="mt-1.5 text-xl font-semibold leading-snug tracking-tight text-ink sm:text-2xl">
          {{ user?.full_name || 'Siswa' }}
        </h1>
        <p class="mt-2 text-sm leading-relaxed text-ink-muted">
          Baca modul, coba praktikum di laboratorium maya tanpa risiko bahan kimia, lalu kerjakan kuis modul untuk
          melihat capaianmu.
        </p>
      </div>

      <!-- Active Class Badge / Selector (Jika punya kelas) -->
      <div v-if="classes.length > 0" class="w-full rounded-lg border border-line bg-paper p-3 md:w-auto">
        <div class="flex items-center gap-2.5">
          <span class="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-accent-50 text-accent">
            <BookOpen class="h-4 w-4" aria-hidden="true" />
          </span>
          <div class="min-w-0">
            <label for="student-class-select" class="block text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">
              Kelas terdaftar
            </label>
            <select
              v-if="classes.length > 1"
              id="student-class-select"
              :value="selectedClass?.id"
              @change="(e) => selectClass(classes.find(c => c.id === parseInt(e.target.value)))"
              class="max-w-full cursor-pointer truncate rounded-sm bg-transparent pr-4 text-sm font-semibold text-ink outline-none"
            >
              <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
            <span v-else class="block truncate text-sm font-semibold text-ink">{{ selectedClass?.name || classes[0].name }}</span>
          </div>
        </div>
        <p class="mt-2 flex items-center gap-1 text-[11px] font-medium text-success-700">
          <CheckCircle2 class="h-3 w-3" aria-hidden="true" />
          Aktif, kelas {{ selectedClass?.grade_level || classes[0].grade_level }}
        </p>
      </div>

      <!-- Quick Action: Join Class by Code (Hanya tampil jika belum punya kelas) -->
      <div v-else class="w-full space-y-2.5 rounded-lg border border-line bg-paper p-4 md:w-80">
        <label for="student-enroll-code" class="block text-xs font-semibold text-ink-soft">Gabung kelas</label>
        <div class="flex gap-2">
          <input
            id="student-enroll-code"
            v-model="enrollCode"
            type="text"
            placeholder="Contoh: CHEM-7X"
            class="min-w-0 flex-1 rounded-md border border-line bg-surface px-3 py-2 font-mono text-xs uppercase text-ink outline-none transition-colors placeholder:font-sans placeholder:normal-case placeholder:text-ink-faint focus:border-accent"
          />
          <button
            type="button"
            @click="handleEnrollByCode"
            :disabled="enrollLoading || !enrollCode"
            class="min-h-[38px] rounded-md bg-ink px-3.5 text-xs font-semibold text-white transition-colors hover:bg-ink-soft disabled:opacity-50"
          >
            {{ enrollLoading ? 'Memproses' : 'Gabung' }}
          </button>
        </div>

        <p v-if="enrollMessage.text" :class="enrollMessage.type === 'success' ? 'text-success-700' : 'text-danger-700'" class="flex items-center gap-1.5 text-[11px] font-medium">
          <component :is="enrollMessage.type === 'success' ? CheckCircle2 : AlertCircle" class="h-3.5 w-3.5" aria-hidden="true" />
          {{ enrollMessage.text }}
        </p>
      </div>
    </div>

    <!-- Section tabs: current state marked by rule and weight, not colour alone -->
    <div class="flex flex-wrap items-center gap-1 border-b border-line" role="tablist" aria-label="Bagian portal belajar">
      <button
        v-for="tab in [
          { id: 'overview', label: 'Modul & materi', icon: BookOpen },
          { id: 'lab', label: 'Laboratorium', icon: FlaskConical },
          { id: 'quiz', label: 'Kuis & asesmen', icon: CheckSquare }
        ]"
        :key="tab.id"
        type="button"
        role="tab"
        :aria-selected="activeTab === tab.id"
        @click="activeTab = tab.id; if (tab.id === 'quiz') takingQuiz = false"
        class="-mb-px flex min-h-[44px] items-center gap-2 border-b-2 px-3 text-xs transition-colors"
        :class="
          activeTab === tab.id
            ? 'border-accent font-semibold text-ink'
            : 'border-transparent font-medium text-ink-muted hover:border-line-strong hover:text-ink'
        "
      >
        <component :is="tab.icon" class="h-4 w-4" :class="activeTab === tab.id ? 'text-accent' : 'text-ink-faint'" aria-hidden="true" />
        {{ tab.label }}
      </button>
    </div>

    <!-- VIEW 1: Overview & Learning Content -->
    <div v-if="activeTab === 'overview'" class="space-y-6">
      <!-- Empty state if student has no classes -->
      <div v-if="classes.length === 0" class="space-y-3 rounded-xl border border-line bg-surface p-10 text-center">
        <BookOpen class="mx-auto h-10 w-10 text-ink-faint" aria-hidden="true" />
        <h2 class="text-sm font-semibold text-ink">Belum terdaftar di kelas mana pun</h2>
        <p class="mx-auto max-w-sm text-xs leading-relaxed text-ink-muted">
          Minta kode pendaftaran dari gurumu, lalu masukkan pada formulir gabung kelas di bagian atas halaman.
        </p>
      </div>

      <!-- Class & Modules Grid -->
      <div v-else class="space-y-4">
        <!-- Materials Content -->
        <div class="space-y-5 rounded-xl border border-line bg-surface p-5">
          <div class="flex flex-wrap items-end justify-between gap-3 border-b border-line pb-3">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <span class="rounded-sm bg-accent-50 px-2 py-0.5 text-[11px] font-semibold text-accent-700">
                  Kelas {{ selectedClass?.grade_level || classes[0]?.grade_level }}
                </span>
                <span v-if="modules.length > 0" class="kf-readout rounded-sm bg-sunken px-2 py-0.5 text-[11px] font-medium text-ink-muted">
                  Modul {{ currentModuleIndex + 1 }} / {{ modules.length }}
                </span>
                <span v-if="materials.length > 0" class="text-[11px] text-ink-faint">
                  {{ materials.length }} materi
                </span>
              </div>
              <h2 class="mt-2 text-base font-semibold text-ink">{{ selectedModule?.title || 'Pilih modul' }}</h2>
              <p class="mt-0.5 text-xs text-ink-muted">Materi teori dan panduan praktikum laboratorium</p>
            </div>

            <!-- Module step and the two actions available for this module -->
            <div class="flex flex-wrap items-center gap-2">
              <div v-if="modules.length > 1" class="flex items-center rounded-md border border-line bg-paper">
                <button
                  type="button"
                  @click="goToPrevModule"
                  :disabled="!prevModule"
                  class="grid h-9 w-9 place-items-center rounded-l-md text-ink-muted transition-colors hover:bg-sunken disabled:opacity-40"
                  aria-label="Modul sebelumnya"
                >
                  <ChevronLeft class="h-4 w-4" aria-hidden="true" />
                </button>
                <span class="kf-readout border-x border-line px-2 text-[11px] font-medium text-ink-muted">
                  {{ currentModuleIndex + 1 }}/{{ modules.length }}
                </span>
                <button
                  type="button"
                  @click="goToNextModule"
                  :disabled="!nextModule"
                  class="grid h-9 w-9 place-items-center rounded-r-md text-ink-muted transition-colors hover:bg-sunken disabled:opacity-40"
                  aria-label="Modul selanjutnya"
                >
                  <ChevronRight class="h-4 w-4" aria-hidden="true" />
                </button>
              </div>

              <button
                v-if="activeQuiz"
                type="button"
                @click="startTakingQuiz(activeQuiz)"
                class="inline-flex min-h-[38px] items-center gap-1.5 rounded-md border border-line bg-surface px-3 text-xs font-semibold text-ink-soft transition-colors hover:bg-sunken"
              >
                <CheckSquare class="h-3.5 w-3.5" aria-hidden="true" />
                Kerjakan kuis
              </button>

              <button
                type="button"
                @click="openVirtualLab(selectedMaterial)"
                class="inline-flex min-h-[38px] items-center gap-1.5 rounded-md bg-accent px-3 text-xs font-semibold text-white transition-colors hover:bg-accent-700"
              >
                <FlaskConical class="h-3.5 w-3.5" aria-hidden="true" />
                Buka lab
              </button>
            </div>
          </div>

          <!-- Materials list with stage progression -->
          <div v-if="materials.length > 0" class="space-y-4">
            <div
              v-for="(mat, matIdx) in materials"
              :key="mat.id"
              :class="[
                'space-y-2 rounded-lg border p-4 transition-colors',
                selectedMaterial?.id === mat.id
                  ? 'border-accent bg-accent-50/60'
                  : 'border-line bg-paper hover:bg-sunken'
              ]"
            >
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="flex min-w-0 items-center gap-2.5">
                  <span
                    class="grid h-6 w-6 shrink-0 place-items-center rounded-full text-[10px] font-semibold"
                    :class="selectedMaterial?.id === mat.id ? 'bg-accent text-white' : 'bg-sunken text-ink-muted'"
                  >
                    {{ matIdx + 1 }}
                  </span>
                  <h3 class="truncate text-sm font-semibold text-ink">{{ mat.title }}</h3>
                </div>
                <div class="flex shrink-0 items-center gap-3">
                  <button
                    v-if="selectedMaterial?.id !== mat.id"
                    type="button"
                    @click="selectedMaterial = mat"
                    class="min-h-[32px] text-xs font-semibold text-ink-muted transition-colors hover:text-ink"
                  >
                    Buka rincian
                  </button>
                  <button
                    type="button"
                    @click="openVirtualLab(mat)"
                    class="flex min-h-[32px] items-center gap-1 text-xs font-semibold text-accent transition-colors hover:underline"
                  >
                    Mulai praktikum
                    <ArrowRight class="h-3 w-3" aria-hidden="true" />
                  </button>
                </div>
              </div>

              <div
                v-if="mat.content_html"
                class="border-t border-line/70 pt-2 text-xs leading-relaxed text-ink-soft"
                v-html="renderFormula(mat.content_html)"
              ></div>
              <p v-else class="text-xs italic text-ink-faint">Belum ada penjelasan tertulis pada materi ini.</p>
            </div>

            <!-- Step controls: previous, position, next -->
            <div class="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-line bg-paper p-3">
              <button
                type="button"
                @click="goToPrevMaterial"
                :disabled="!prevMaterial"
                class="inline-flex min-h-[36px] items-center gap-1.5 rounded-md border border-line bg-surface px-2.5 text-xs font-semibold text-ink-soft transition-colors hover:bg-sunken disabled:opacity-40"
              >
                <ChevronLeft class="h-3.5 w-3.5" aria-hidden="true" />
                Materi sebelumnya
              </button>

              <span class="kf-readout text-[11px] font-medium text-ink-muted">
                {{ currentMaterialIndex + 1 }} / {{ materials.length }}
              </span>

              <button
                v-if="nextMaterial"
                type="button"
                @click="goToNextMaterial"
                class="inline-flex min-h-[36px] items-center gap-1.5 rounded-md bg-accent px-3 text-xs font-semibold text-white transition-colors hover:bg-accent-700"
              >
                Materi selanjutnya
                <ChevronRight class="h-3.5 w-3.5" aria-hidden="true" />
              </button>

              <button
                v-else-if="nextModule"
                type="button"
                @click="goToNextModule"
                class="inline-flex min-h-[36px] items-center gap-1.5 rounded-md bg-ink px-3 text-xs font-semibold text-white transition-colors hover:bg-ink-soft"
              >
                Modul berikutnya
                <ChevronRight class="h-3.5 w-3.5" aria-hidden="true" />
              </button>

              <button
                v-else-if="activeQuiz"
                type="button"
                @click="startTakingQuiz(activeQuiz)"
                class="inline-flex min-h-[36px] items-center gap-1.5 rounded-md bg-accent px-3 text-xs font-semibold text-white transition-colors hover:bg-accent-700"
              >
                <CheckSquare class="h-3.5 w-3.5" aria-hidden="true" />
                Lanjut ke kuis
              </button>
              <span v-else class="inline-flex items-center gap-1.5 text-xs font-semibold text-success-700">
                <CheckCircle2 class="h-3.5 w-3.5" aria-hidden="true" />
                Semua materi selesai
              </span>
            </div>
          </div>

          <p v-else class="py-8 text-center text-xs text-ink-muted">
            Modul ini belum punya materi. Hubungi gurumu untuk mempublikasikan materinya.
          </p>
        </div>
      </div>
    </div>

    <!-- VIEW 2: Virtual Lab Student View -->
    <div v-else-if="activeTab === 'lab'" class="space-y-4">
      <div class="flex flex-col justify-between gap-3 rounded-xl border border-line bg-surface p-4 sm:flex-row sm:items-center">
        <div class="flex flex-wrap items-center gap-3">
          <div class="min-w-0">
            <p class="text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Laboratorium</p>
            <h2 class="mt-0.5 truncate text-sm font-semibold text-ink">
              {{ selectedMaterial ? selectedMaterial.title : 'Praktikum kimia mandiri' }}
            </h2>
          </div>
          <!-- Two labs can exist for one material; the switch marks which is live -->
          <div v-if="customLabConfig" class="flex gap-1 rounded-md border border-line bg-paper p-1 text-xs" role="tablist" aria-label="Pilih laboratorium">
            <button
              type="button"
              role="tab"
              :aria-selected="labMode === 'custom'"
              @click="labMode = 'custom'"
              class="min-h-[32px] max-w-[11rem] truncate rounded-sm px-2 font-medium transition-colors"
              :class="labMode === 'custom' ? 'bg-surface font-semibold text-ink shadow-2xs' : 'text-ink-muted hover:text-ink'"
            >
              {{ customLabConfig.config_data?.lab_title || 'Lab dari guru' }}
            </button>
            <button
              type="button"
              role="tab"
              :aria-selected="labMode === 'stoichiometry'"
              @click="labMode = 'stoichiometry'"
              class="min-h-[32px] rounded-sm px-2 font-medium transition-colors"
              :class="labMode === 'stoichiometry' ? 'bg-surface font-semibold text-ink shadow-2xs' : 'text-ink-muted hover:text-ink'"
            >
              Stoikiometri
            </button>
          </div>
        </div>

        <button
          type="button"
          @click="activeTab = 'overview'"
          class="inline-flex min-h-[36px] items-center gap-1.5 self-start rounded-md border border-line px-2.5 text-xs font-semibold text-ink-soft transition-colors hover:bg-sunken sm:self-center"
        >
          <ChevronLeft class="h-3.5 w-3.5" aria-hidden="true" />
          Kembali ke materi
        </button>
      </div>

      <!-- Custom lab configured by the teacher: live measurement sheet -->
      <div v-if="labMode === 'custom' && customLabConfig" class="space-y-5 rounded-xl border border-line bg-surface p-5">
        <div class="flex flex-col justify-between gap-4 border-b border-line pb-4 md:flex-row md:items-center">
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Praktikum titrasi</p>
            <h2 class="mt-0.5 text-base font-semibold text-ink">{{ customLabConfig.config_data?.lab_title }}</h2>
            <p class="mt-1 text-xs leading-relaxed text-ink-muted">
              {{ customLabConfig.config_data?.instructions || 'Ikuti petunjuk praktikum untuk menyelesaikan simulasi.' }}
            </p>
          </div>

          <div class="flex flex-wrap gap-2">
            <div class="rounded-md border border-line bg-paper px-3 py-2">
              <span class="block text-[10px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Analit</span>
              <span class="block text-xs font-semibold text-ink">{{ customLabConfig.config_data?.solution_name }} ({{ customLabConfig.config_data?.solution_molarity }}M)</span>
            </div>
            <div class="rounded-md border border-line bg-paper px-3 py-2">
              <span class="block text-[10px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Titran</span>
              <span class="block text-xs font-semibold text-ink">{{ customLabConfig.config_data?.titrant_name }} ({{ customLabConfig.config_data?.titrant_molarity }}M)</span>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 items-start gap-5 lg:grid-cols-12">
          <!-- Simulation canvas -->
          <div class="space-y-4 rounded-lg border border-line bg-paper p-5 lg:col-span-7">
            <div class="flex items-center justify-between text-xs">
              <span class="font-semibold text-ink">Simulasi titrasi</span>
              <button
                type="button"
                @click="resetStudentSimulation"
                class="inline-flex min-h-[32px] items-center gap-1 rounded-md px-1.5 text-xs font-semibold text-ink-muted transition-colors hover:bg-sunken hover:text-ink"
              >
                <RefreshCw class="h-3.5 w-3.5" aria-hidden="true" />
                Reset
              </button>
            </div>

            <!-- Flat apparatus area; the liquid colour is the only gradient in the sheet -->
            <div class="relative flex h-72 items-center justify-center overflow-hidden rounded-lg border border-line bg-sunken">
              <div class="absolute left-1/2 top-0 h-16 w-2.5 -translate-x-1/2 rounded-b-sm bg-ink-faint" aria-hidden="true"></div>

              <div class="relative flex h-48 w-40 flex-col items-center justify-end">
                <div class="z-10 h-14 w-10 border-l-2 border-r-2 border-ink-faint bg-transparent" aria-hidden="true"></div>
                <div
                  class="relative flex h-32 w-40 flex-col justify-end overflow-hidden rounded-b-lg border-2 border-ink-faint transition-colors duration-500"
                  :style="{ backgroundColor: studentLiquidColor }"
                  role="img"
                  :aria-label="'Labu erlenmeyer terisi larutan, pH ' + studentPhValue"
                >
                  <div
                    class="w-full rounded-b-md transition-all duration-300"
                    :style="{
                      height: Math.min(25 + studentLabVolume * 1.3, 92) + '%',
                      backgroundColor: studentLiquidColor
                    }"
                  ></div>
                  <div class="kf-readout absolute left-2 top-3 space-y-2 text-[9px] text-ink-faint">
                    <p>50 mL</p>
                    <p>25 mL</p>
                    <p>10 mL</p>
                  </div>
                </div>
              </div>

              <!-- Live readings pinned to the apparatus -->
              <div class="absolute bottom-3 right-3 max-w-[11.5rem] space-y-1.5 rounded-md border border-line bg-surface p-2.5 text-xs shadow-card">
                <div class="flex items-center justify-between gap-2">
                  <span class="text-[11px] text-ink-muted">pH larutan</span>
                  <span class="kf-readout text-sm font-semibold text-ink">{{ studentPhValue }}</span>
                </div>
                <div class="flex items-center justify-between gap-2">
                  <span class="text-[11px] text-ink-muted">Titran masuk</span>
                  <span class="kf-readout text-sm font-semibold text-accent">{{ studentLabVolume }} mL</span>
                </div>
                <div class="border-t border-line pt-1.5">
                  <span
                    class="block truncate rounded-sm px-1.5 py-0.5 text-center text-[10px] font-semibold"
                    :class="studentLabVolume >= studentEqVolume ? 'bg-success-50 text-success-700' : 'bg-accent-50 text-accent-700'"
                  >
                    {{ studentReactionStatus }}
                  </span>
                </div>
              </div>
            </div>

            <div class="space-y-3">
              <div class="flex items-center justify-between text-xs">
                <label for="student-buret-range" class="font-semibold text-ink">Volume titran</label>
                <span class="kf-readout text-xs font-semibold text-ink">
                  {{ studentLabVolume }} / {{ customLabConfig.config_data?.max_volume_ml || 50 }} mL
                </span>
              </div>

              <input
                id="student-buret-range"
                type="range"
                min="0"
                :max="customLabConfig.config_data?.max_volume_ml || 50"
                step="0.5"
                v-model.number="studentLabVolume"
                class="w-full accent-accent"
              />

              <div class="flex flex-wrap gap-2 pt-1 sm:flex-nowrap">
                <button
                  type="button"
                  @click="toggleStudentTitration"
                  class="flex min-h-[44px] flex-1 items-center justify-center gap-2 rounded-md text-xs font-semibold text-white transition-colors"
                  :class="studentIsTitrating ? 'bg-danger-600 hover:bg-danger-700' : 'bg-accent hover:bg-accent-700'"
                  :aria-pressed="studentIsTitrating"
                >
                  <component :is="studentIsTitrating ? Pause : Play" class="h-3.5 w-3.5" aria-hidden="true" />
                  {{ studentIsTitrating ? 'Tutup kran buret' : 'Buka kran buret' }}
                </button>

                <button
                  type="button"
                  @click="addStudentDrop"
                  class="inline-flex min-h-[44px] items-center gap-1.5 rounded-md border border-line bg-surface px-3 text-xs font-semibold text-ink-soft transition-colors hover:bg-sunken"
                >
                  <Droplets class="h-3.5 w-3.5 text-accent" aria-hidden="true" />
                  Tambah 0,5 mL
                </button>
              </div>
            </div>
          </div>

          <!-- Observation sheet -->
          <div class="space-y-4 rounded-lg border border-line bg-surface p-5 lg:col-span-5">
            <h4 class="text-xs font-semibold uppercase tracking-[0.04em] text-ink-faint">
              Lembar data pengamatan
            </h4>

            <div class="space-y-3 text-xs">
              <div class="grid grid-cols-2 gap-2">
                <div class="rounded-md border border-line bg-paper p-2.5">
                  <span class="block text-[10px] font-medium text-ink-muted">Warna awal</span>
                  <div class="mt-1 flex items-center gap-1.5">
                    <span
                      class="h-3.5 w-3.5 rounded-full border border-line-strong"
                      :style="{ backgroundColor: customLabConfig.config_data?.color_start || '#F8FAFC' }"
                      aria-hidden="true"
                    ></span>
                    <span class="kf-readout truncate text-[11px] font-medium text-ink-soft">{{ customLabConfig.config_data?.color_start || 'Larutan tanpa warna' }}</span>
                  </div>
                </div>

                <div class="rounded-md border border-line bg-paper p-2.5">
                  <span class="block text-[10px] font-medium text-ink-muted">Warna titik akhir</span>
                  <div class="mt-1 flex items-center gap-1.5">
                    <span
                      class="h-3.5 w-3.5 rounded-full border border-line-strong"
                      :style="{ backgroundColor: customLabConfig.config_data?.color_end || '#F472B6' }"
                      aria-hidden="true"
                    ></span>
                    <span class="kf-readout truncate text-[11px] font-medium text-ink-soft">{{ customLabConfig.config_data?.color_end || '#F472B6' }}</span>
                  </div>
                </div>
              </div>

              <div class="space-y-1 rounded-md border border-line bg-paper p-3">
                <span class="block text-[10px] font-medium text-ink-muted">Indikator terpasang</span>
                <span class="font-semibold text-ink">{{ customLabConfig.config_data?.indicator_type || 'Phenolphthalein (PP)' }}</span>
              </div>

              <!-- Live readings, same values as the apparatus -->
              <div class="space-y-2 rounded-md border border-accent-line bg-accent-50/60 p-3">
                <span class="block text-[10px] font-semibold uppercase tracking-[0.04em] text-ink-muted">Hasil pengamatan buret</span>
                <div class="grid grid-cols-2 gap-2">
                  <div>
                    <span class="block text-[10px] text-ink-muted">Volume terukur</span>
                    <span class="kf-readout text-sm font-semibold text-ink">{{ studentLabVolume }} mL</span>
                  </div>
                  <div>
                    <span class="block text-[10px] text-ink-muted">pH larutan</span>
                    <span class="kf-readout text-sm font-semibold text-ink">{{ studentPhValue }}</span>
                  </div>
                </div>
                <p class="border-t border-accent-line pt-1.5 text-[11px] text-ink-soft">
                  Status:
                  <b :class="studentLabVolume >= studentEqVolume ? 'text-success-700' : 'text-accent-700'">{{ studentReactionStatus }}</b>
                </p>
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
        <!-- Available quiz for the selected module -->
        <div class="space-y-4 rounded-xl border border-line bg-surface p-5">
          <div class="flex flex-col justify-between gap-4 border-b border-line pb-4 sm:flex-row sm:items-center">
            <div>
              <p class="text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Asesmen modul</p>
              <h2 class="mt-1 text-base font-semibold text-ink">
                {{ selectedModule ? selectedModule.title : 'Pilih modul pembelajaran' }}
              </h2>
              <p class="mt-1 text-xs leading-relaxed text-ink-muted">
                Uji pemahaman konsep, hitungan reaksi, dan keterampilan praktikum kimia.
              </p>
            </div>

            <button
              v-if="activeQuiz"
              type="button"
              @click="startTakingQuiz(activeQuiz)"
              class="inline-flex min-h-[44px] shrink-0 items-center gap-2 rounded-md bg-ink px-4 text-xs font-semibold text-white transition-colors hover:bg-ink-soft"
            >
              <CheckSquare class="h-4 w-4 text-accent-300" aria-hidden="true" />
              {{ activeQuiz.title || 'Mulai kerjakan kuis' }}
            </button>
            <p v-else class="shrink-0 rounded-md border border-line bg-paper px-3 py-2 text-xs italic text-ink-muted">
              Belum ada kuis yang diterbitkan untuk modul ini.
            </p>
          </div>

          <!-- Only fields the quiz record actually carries -->
          <div v-if="activeQuiz" class="grid grid-cols-1 gap-2 text-xs sm:grid-cols-3">
            <div class="rounded-md border border-line bg-paper p-3">
              <span class="block text-[10px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Batas waktu</span>
              <span class="kf-readout mt-0.5 block font-semibold text-ink">
                {{ activeQuiz.time_limit_minutes ? activeQuiz.time_limit_minutes + ' menit' : 'Tanpa batas' }}
              </span>
            </div>
            <div class="rounded-md border border-line bg-paper p-3">
              <span class="block text-[10px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Penilaian</span>
              <span class="mt-0.5 block font-semibold text-ink">Radar kompetensi</span>
            </div>
            <div class="rounded-md border border-line bg-paper p-3">
              <span class="block text-[10px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Status</span>
              <span class="mt-0.5 block font-semibold" :class="activeQuiz.is_active ? 'text-success-700' : 'text-ink-muted'">
                {{ activeQuiz.is_active ? 'Terbuka' : 'Ditutup' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Attempt history -->
        <div class="overflow-hidden rounded-xl border border-line bg-surface">
          <div class="flex flex-wrap items-center justify-between gap-2 border-b border-line px-5 py-3.5">
            <div>
              <h2 class="text-sm font-semibold text-ink">Riwayat pengerjaan</h2>
              <p class="mt-0.5 text-xs text-ink-muted">Skor dan capaian radar dari kuis yang sudah kamu selesaikan.</p>
            </div>
            <button
              type="button"
              @click="loadStudentAttempts"
              class="inline-flex min-h-[36px] items-center gap-1.5 rounded-md px-2 text-xs font-semibold text-accent transition-colors hover:bg-accent-50"
            >
              <RefreshCw class="h-3.5 w-3.5" aria-hidden="true" />
              Segarkan
            </button>
          </div>

          <p v-if="loadingQuiz" class="flex items-center gap-2 px-5 py-8 text-xs text-ink-muted">
            <RefreshCw class="h-3.5 w-3.5 animate-spin text-accent" aria-hidden="true" />
            Memuat riwayat kuis
          </p>
          <p v-else-if="quizHistory.length === 0" class="px-5 py-8 text-xs leading-relaxed text-ink-muted">
            Belum ada riwayat. Setelah kamu mengerjakan kuis modul, hasilnya muncul di sini.
          </p>
          <div v-else class="overflow-x-auto">
            <table class="w-full min-w-[42rem] text-left text-xs">
              <thead>
                <tr class="border-b border-line bg-paper text-[11px] font-semibold text-ink-muted">
                  <th scope="col" class="px-4 py-2.5 font-semibold">Kuis</th>
                  <th scope="col" class="px-4 py-2.5 font-semibold">Mulai</th>
                  <th scope="col" class="px-4 py-2.5 font-semibold">Selesai</th>
                  <th scope="col" class="px-4 py-2.5 font-semibold">Skor</th>
                  <th scope="col" class="px-4 py-2.5 font-semibold">Capaian radar</th>
                  <th scope="col" class="px-4 py-2.5 text-right font-semibold">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-line">
                <tr v-for="att in quizHistory" :key="att.id" class="text-ink-soft transition-colors hover:bg-paper">
                  <td class="kf-readout px-4 py-3 font-semibold text-ink">#{{ att.quiz_id }}</td>
                  <td class="kf-readout px-4 py-3 text-ink-muted">{{ new Date(att.started_at).toLocaleString('id-ID') }}</td>
                  <td class="kf-readout px-4 py-3 text-ink-muted">
                    {{ att.completed_at ? new Date(att.completed_at).toLocaleString('id-ID') : 'Belum selesai' }}
                  </td>
                  <td class="px-4 py-3">
                    <span v-if="att.completed_at" class="kf-readout rounded-sm bg-sunken px-1.5 py-0.5 text-[11px] font-semibold text-ink">
                      {{ att.total_score }} / 100
                    </span>
                    <span v-else class="text-[11px] italic text-ink-muted">Berjalan</span>
                  </td>
                  <td class="px-4 py-3">
                    <div v-if="getAttemptMetrics(att).length > 0" class="flex max-w-xs flex-wrap gap-1">
                      <span
                        v-for="item in getAttemptMetrics(att)"
                        :key="item.name"
                        class="rounded-sm bg-accent-50 px-1.5 py-0.5 text-[10px] font-medium text-accent-700"
                      >
                        {{ item.name }} {{ item.val }}%
                      </span>
                    </div>
                    <span v-else class="text-[11px] text-ink-faint">Belum ada</span>
                  </td>
                  <td class="px-4 py-3 text-right text-[11px] font-semibold">
                    <span v-if="att.completed_at" class="text-success-700">Selesai</span>
                    <span v-else class="text-ink-muted">Belum dikirim</span>
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
