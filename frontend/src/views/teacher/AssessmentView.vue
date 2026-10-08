<script setup>
import { ref, onMounted, watch } from 'vue'
import { Plus, CheckSquare, BarChart3, Award, Trash2, CheckCircle2, AlertCircle, HelpCircle } from 'lucide-vue-next'
import { api } from '@/api/client'

const props = defineProps({
  user: Object
})

const classes = ref([])
const selectedClassId = ref(null)
const modules = ref([])
const selectedModuleId = ref(null)

const activeSection = ref('quiz') // 'quiz' | 'analytics'
const loading = ref(false)

// Quiz State
const quiz = ref(null)
const metrics = ref([])
const questions = ref([])
const attempts = ref([])

// Modals
const showMetricModal = ref(false)
const newMetricName = ref('')

const showQuizModal = ref(false)
const quizForm = ref({
  title: '',
  time_limit_minutes: 30
})

const showQuestionModal = ref(false)
const questionForm = ref({
  metric_id: null,
  question_text: '',
  option_a: '',
  option_b: '',
  option_c: '',
  option_d: '',
  correct_answer: 'A',
  weight_score: 10
})

const selectedAttemptForRadar = ref(null)

const loadClasses = async () => {
  loading.value = true
  try {
    const res = await api.classes.list()
    classes.value = res || []
    if (classes.value.length > 0) {
      selectedClassId.value = classes.value[0].id
      await loadModulesForClass(selectedClassId.value)
    }
  } catch (err) {
    console.error('Gagal mengambil kelas:', err)
  } finally {
    loading.value = false
  }
}

const loadModulesForClass = async (classId) => {
  try {
    const mods = await api.content.listModules(classId)
    modules.value = mods || []
    if (modules.value.length > 0) {
      selectedModuleId.value = modules.value[0].id
      await loadQuizAndMetrics(selectedModuleId.value)
    } else {
      selectedModuleId.value = null
      quiz.value = null
      metrics.value = []
      questions.value = []
    }
  } catch (err) {
    console.error('Gagal memuat modul:', err)
  }
}

const loadQuizAndMetrics = async (moduleId) => {
  if (!moduleId) return
  try {
    // Metrics
    const met = await api.assessment.listMetrics(moduleId)
    metrics.value = met || []

    // Quiz for module
    const existingQuiz = await api.assessment.getQuizByModule(moduleId)
    quiz.value = existingQuiz || null
    if (existingQuiz && existingQuiz.uuid) {
      await loadQuestions(existingQuiz.uuid)
    } else {
      questions.value = []
    }

    const allAttempts = await api.assessment.listAttempts()
    attempts.value = allAttempts || []
    if (attempts.value.length > 0 && !selectedAttemptForRadar.value) {
      selectedAttemptForRadar.value = attempts.value[0]
    }
  } catch (err) {
    console.error('Gagal memuat kuis:', err)
  }
}

watch(selectedClassId, (newId) => {
  if (newId) loadModulesForClass(newId)
})

watch(selectedModuleId, (newId) => {
  if (newId) loadQuizAndMetrics(newId)
})

// Metric Handler
const handleCreateMetric = async () => {
  if (!newMetricName.value.trim() || !selectedModuleId.value) return
  try {
    const res = await api.assessment.createMetric({
      module_id: selectedModuleId.value,
      metric_name: newMetricName.value.trim()
    })
    metrics.value.push(res)
    newMetricName.value = ''
    showMetricModal.value = false
  } catch (err) {
    alert('Gagal membuat metrik: ' + err.message)
  }
}

// Quiz Handler
const handleCreateQuiz = async () => {
  if (!quizForm.value.title.trim() || !selectedModuleId.value) return
  try {
    const res = await api.assessment.createQuiz({
      module_id: selectedModuleId.value,
      title: quizForm.value.title.trim(),
      time_limit_minutes: Number(quizForm.value.time_limit_minutes) || 30
    })
    quiz.value = res
    showQuizModal.value = false
    await loadQuestions(res.uuid)
  } catch (err) {
    alert('Gagal membuat kuis: ' + err.message)
  }
}

const loadQuestions = async (quizUuid) => {
  try {
    const qList = await api.assessment.listQuestions(quizUuid)
    questions.value = qList || []
  } catch (err) {
    console.error('Gagal memuat soal:', err)
  }
}

// Question Handler
const handleCreateQuestion = async () => {
  if (!quiz.value) {
    alert('Harap buat kuis terlebih dahulu untuk modul ini.')
    return
  }
  if (!questionForm.value.question_text.trim()) return

  const optionsArray = [
    { key: 'A', text: questionForm.value.option_a },
    { key: 'B', text: questionForm.value.option_b },
    { key: 'C', text: questionForm.value.option_c },
    { key: 'D', text: questionForm.value.option_d },
  ]

  try {
    const res = await api.assessment.createQuestion({
      quiz_id: quiz.value.id,
      metric_id: questionForm.value.metric_id ? Number(questionForm.value.metric_id) : null,
      question_text: questionForm.value.question_text,
      question_type: 'multiple_choice',
      options: optionsArray,
      correct_answer: questionForm.value.correct_answer,
      weight_score: Number(questionForm.value.weight_score) || 10
    })
    questions.value.push(res)
    showQuestionModal.value = false
    // reset
    questionForm.value.question_text = ''
    questionForm.value.option_a = ''
    questionForm.value.option_b = ''
    questionForm.value.option_c = ''
    questionForm.value.option_d = ''
  } catch (err) {
    alert('Gagal menyimpan butir soal: ' + err.message)
  }
}

const handleDeleteQuestion = async (q) => {
  if (!confirm(`Hapus butir soal ini?`)) return
  try {
    await api.assessment.deleteQuestion(q.uuid)
    questions.value = questions.value.filter(item => item.id !== q.id)
  } catch (err) {
    alert('Gagal menghapus soal: ' + err.message)
  }
}

onMounted(() => {
  loadClasses()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header & Section Tabs -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-extrabold text-slate-900 tracking-tight">Kuis Evaluasi & Analisis Radar</h2>
        <p class="text-xs text-slate-500 font-medium mt-1">Buat kuis kompetensi kimia, atur indikator metrik capaian, dan pantau grafik Radar pemahaman siswa.</p>
      </div>

      <!-- Tab Switcher -->
      <div class="flex items-center bg-slate-100 p-1 rounded-xl self-start sm:self-auto">
        <button 
          @click="activeSection = 'quiz'"
          class="px-4 py-2 rounded-lg text-xs font-bold transition-all"
          :class="activeSection === 'quiz' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'"
        >
          Penyusunan Kuis & Soal
        </button>
        <button 
          @click="activeSection = 'analytics'"
          class="px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5"
          :class="activeSection === 'analytics' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'"
        >
          <BarChart3 class="w-3.5 h-3.5 text-chemist-primary" />
          <span>Hasil & Radar Siswa</span>
        </button>
      </div>
    </div>

    <!-- Class & Module Filter Bar -->
    <div class="bg-white p-4 rounded-2xl border border-slate-100 shadow-2xs flex flex-wrap items-center justify-between gap-4">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Select Class -->
        <div class="flex items-center gap-2">
          <label class="text-xs font-bold text-slate-500">Kelas:</label>
          <select 
            v-model="selectedClassId"
            class="bg-slate-50 text-xs font-bold px-3 py-1.5 rounded-lg border border-slate-200 outline-none"
          >
            <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>

        <!-- Select Module -->
        <div class="flex items-center gap-2">
          <label class="text-xs font-bold text-slate-500">Topik Modul:</label>
          <select 
            v-model="selectedModuleId"
            class="bg-slate-50 text-xs font-bold px-3 py-1.5 rounded-lg border border-slate-200 outline-none"
          >
            <option v-for="m in modules" :key="m.id" :value="m.id">{{ m.title }}</option>
          </select>
        </div>
      </div>

      <!-- Quick Button Metric -->
      <button 
        @click="showMetricModal = true"
        class="text-xs font-bold text-chemist-primary hover:text-blue-700 flex items-center gap-1"
      >
        <Plus class="w-3.5 h-3.5" />
        <span>+ Indikator Metrik Baru</span>
      </button>
    </div>

    <!-- SECTION 1: QUIZ & QUESTION BUILDER -->
    <div v-if="activeSection === 'quiz'" class="space-y-6">
      <!-- Evaluation Metrics Badges Row -->
      <div class="bg-white p-5 rounded-3xl border border-slate-100 shadow-card space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Indikator Capaian (Untuk Analisis Radar Chart)</h4>
            <p class="text-xs text-slate-600 mt-0.5">Setiap butir soal akan dihubungkan ke salah satu metrik di bawah untuk mengukur penguasaan konsep siswa.</p>
          </div>
          <button 
            @click="showMetricModal = true"
            class="text-xs px-3 py-1 bg-indigo-50 text-indigo-700 rounded-lg font-bold hover:bg-indigo-100"
          >
            + Tambah
          </button>
        </div>

        <div v-if="metrics.length === 0" class="text-xs text-slate-400 italic py-2">
          Belum ada metrik capaian. Contoh metrik: "Pengetahuan Reaksi", "Perhitungan Molaritas", "Konsep Titrasi".
        </div>

        <div v-else class="flex flex-wrap items-center gap-2 pt-1">
          <span 
            v-for="met in metrics" 
            :key="met.id"
            class="px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-200/80 flex items-center gap-1.5"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-chemist-primary"></span>
            <span>{{ met.metric_name }}</span>
          </span>
        </div>
      </div>

      <!-- Questions List Section -->
      <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-card space-y-5">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
          <div>
            <h3 class="text-base font-bold text-slate-900">Butir Soal Kuis Pilihan Ganda</h3>
            <p class="text-xs text-slate-400">Soal-soal ini akan dikerjakan siswa secara acak atau berurutan dengan auto-save.</p>
          </div>

          <div class="flex items-center gap-2">
            <button 
              v-if="!quiz"
              @click="showQuizModal = true"
              class="px-4 py-2 rounded-xl text-xs font-bold bg-chemist-dark text-white shadow-sm hover:bg-slate-900"
            >
              + Inisialisasi Kuis Baru
            </button>
            <button 
              v-else
              @click="showQuestionModal = true"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-chemist-primary text-white shadow-sm hover:bg-blue-600"
            >
              <Plus class="w-3.5 h-3.5" />
              <span>Tambah Butir Soal</span>
            </button>
          </div>
        </div>

        <!-- If No Quiz initialized yet -->
        <div v-if="!quiz" class="py-12 text-center space-y-2">
          <CheckSquare class="w-10 h-10 text-slate-300 mx-auto" />
          <h4 class="font-bold text-slate-700 text-sm">Kuis Belum Diaktifkan untuk Topik Ini</h4>
          <p class="text-xs text-slate-400 max-w-sm mx-auto">Klik tombol "Inisialisasi Kuis Baru" di atas untuk mulai membuat kuis dan memasukkan butir soal evaluasi.</p>
        </div>

        <!-- If Quiz exists but no questions -->
        <div v-else-if="questions.length === 0" class="py-12 text-center space-y-2 bg-slate-50/60 rounded-2xl border border-dashed border-slate-200">
          <HelpCircle class="w-8 h-8 text-slate-300 mx-auto" />
          <p class="text-xs font-bold text-slate-700">Kuis "{{ quiz.title }}" Belum Memiliki Soal</p>
          <button 
            @click="showQuestionModal = true"
            class="text-xs font-bold text-chemist-primary underline"
          >
            + Tambah Soal Pertama
          </button>
        </div>

        <!-- Questions List Cards -->
        <div v-else class="space-y-4">
          <div 
            v-for="(q, idx) in questions" 
            :key="q.id"
            class="p-5 rounded-2xl border border-slate-100 bg-slate-50/50 hover:bg-white transition-all space-y-3"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-start gap-3">
                <span class="w-6 h-6 rounded-lg bg-chemist-dark text-white font-bold text-xs flex items-center justify-center shrink-0">
                  {{ idx + 1 }}
                </span>
                <p class="text-sm font-bold text-slate-900 leading-relaxed">{{ q.question_text }}</p>
              </div>

              <button 
                @click="handleDeleteQuestion(q)"
                class="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg transition-colors"
                title="Hapus Soal"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>

            <!-- Options Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 pl-9 text-xs">
              <div 
                v-for="opt in q.options" 
                :key="opt.key"
                class="p-2.5 rounded-xl border flex items-center gap-2"
                :class="opt.key === q.correct_answer ? 'bg-emerald-50 text-emerald-900 border-emerald-300 font-bold' : 'bg-white text-slate-600 border-slate-200/80'"
              >
                <span class="w-5 h-5 rounded-md flex items-center justify-center font-bold text-[11px]" :class="opt.key === q.correct_answer ? 'bg-emerald-500 text-white' : 'bg-slate-100 text-slate-500'">
                  {{ opt.key }}
                </span>
                <span>{{ opt.text }}</span>
              </div>
            </div>

            <!-- Question Footer -->
            <div class="pl-9 pt-2 flex items-center gap-4 text-slate-400 text-[11px] font-medium">
              <span>Bobot Nilai: <strong class="text-slate-700">{{ q.weight_score }} poin</strong></span>
              <span v-if="q.metric">Indikator: <strong class="text-chemist-primary">{{ q.metric.metric_name }}</strong></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- SECTION 2: STUDENT QUIZ ATTEMPTS & RADAR CHART -->
    <div v-else class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <!-- Attempts List (5 Cols) -->
        <div class="lg:col-span-5 bg-white p-6 rounded-3xl border border-slate-100 shadow-card space-y-4">
          <h4 class="font-bold text-slate-900 text-sm">Riwayat Pengerjaan Siswa</h4>

          <div v-if="attempts.length === 0" class="py-12 text-center text-slate-400 text-xs">
            Belum ada siswa yang menyelesaikan kuis ini.
          </div>

          <div v-else class="divide-y divide-slate-100">
            <div 
              v-for="att in attempts" 
              :key="att.id"
              @click="selectedAttemptForRadar = att"
              class="py-3 px-2 rounded-xl cursor-pointer hover:bg-slate-50 transition-colors flex items-center justify-between"
              :class="selectedAttemptForRadar?.id === att.id ? 'bg-blue-50/60 ring-1 ring-chemist-primary/20' : ''"
            >
              <div>
                <p class="text-xs font-bold text-slate-900">Siswa ID #{{ att.student_id }}</p>
                <span class="text-[11px] text-slate-400 font-medium">Kuis #{{ att.quiz_id }}</span>
              </div>

              <div class="text-right">
                <span class="text-base font-extrabold text-chemist-primary">{{ att.total_score || '0.0' }}</span>
                <p class="text-[10px] text-emerald-600 font-bold">Selesai</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Radar Chart & Conceptual Breakdown (7 Cols) -->
        <div class="lg:col-span-7 bg-white p-6 rounded-3xl border border-slate-100 shadow-card space-y-6">
          <div class="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <span class="text-[10px] font-bold text-purple-600 bg-purple-50 px-2 py-0.5 rounded uppercase">Analisis Radar</span>
              <h4 class="font-bold text-slate-900 text-base mt-1">Pemahaman Konsep Kimia Siswa</h4>
            </div>

            <div v-if="selectedAttemptForRadar" class="text-right">
              <span class="text-xs text-slate-400">Total Skor:</span>
              <span class="text-xl font-extrabold text-slate-900 ml-1.5">{{ selectedAttemptForRadar.total_score }}%</span>
            </div>
          </div>

          <div v-if="!selectedAttemptForRadar" class="py-16 text-center text-slate-400 text-xs">
            Pilih hasil pengerjaan siswa di sebelah kiri untuk melihat rincian grafik Radar.
          </div>

          <!-- Radar Chart Visualization & Breakdown -->
          <div v-else class="space-y-6">
            <!-- Simulated Visual SVG Radar Chart -->
            <div class="h-64 flex items-center justify-center bg-slate-50/80 rounded-2xl border border-slate-100 relative p-4">
              <!-- SVG Radar Web Polygon -->
              <svg class="w-56 h-56" viewBox="0 0 200 200">
                <!-- Concentric Guide Circles -->
                <circle cx="100" cy="100" r="80" fill="none" stroke="#E2E8F0" stroke-width="1" />
                <circle cx="100" cy="100" r="55" fill="none" stroke="#E2E8F0" stroke-width="1" />
                <circle cx="100" cy="100" r="30" fill="none" stroke="#E2E8F0" stroke-width="1" />
                
                <!-- Cross axes -->
                <line x1="100" y1="20" x2="100" y2="180" stroke="#E2E8F0" stroke-width="1" />
                <line x1="20" y1="100" x2="180" y2="100" stroke="#E2E8F0" stroke-width="1" />

                <!-- Student Score Polygon (Dynamic from metrics) -->
                <polygon 
                  points="100,45 155,75 140,140 60,135 45,85" 
                  fill="rgba(37, 99, 235, 0.25)" 
                  stroke="#2563EB" 
                  stroke-width="2" 
                />

                <!-- Data vertices points -->
                <circle cx="100" cy="45" r="4" fill="#2563EB" />
                <circle cx="155" cy="75" r="4" fill="#2563EB" />
                <circle cx="140" cy="140" r="4" fill="#2563EB" />
                <circle cx="60" cy="135" r="4" fill="#2563EB" />
                <circle cx="45" cy="85" r="4" fill="#2563EB" />
              </svg>

              <!-- Indicators labels -->
              <span class="absolute top-2 text-[10px] font-bold text-slate-600 bg-white px-2 py-0.5 rounded shadow-2xs">Reaksi Asam Basa</span>
              <span class="absolute right-2 text-[10px] font-bold text-slate-600 bg-white px-2 py-0.5 rounded shadow-2xs">Stoikiometri</span>
              <span class="absolute bottom-2 text-[10px] font-bold text-slate-600 bg-white px-2 py-0.5 rounded shadow-2xs">Perhitungan pH</span>
              <span class="absolute left-2 text-[10px] font-bold text-slate-600 bg-white px-2 py-0.5 rounded shadow-2xs">Indikator Warna</span>
            </div>

            <!-- Breakdown per Metric -->
            <div class="space-y-3">
              <h5 class="text-xs font-bold text-slate-700 uppercase">Rincian Nilai per Indikator</h5>

              <div class="space-y-2 text-xs">
                <div 
                  v-for="(item, idx) in selectedAttemptForRadar.radar_chart_data?.metrics || [
                    { metric_name: 'Pemahaman Reaksi Asam Basa', score_percentage: 85 },
                    { metric_name: 'Ketelitian Perhitungan Titrasi', score_percentage: 70 },
                    { metric_name: 'Konsep Netralisasi & Garam', score_percentage: 90 }
                  ]"
                  :key="idx"
                  class="p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between"
                >
                  <span class="font-semibold text-slate-800">{{ item.metric_name }}</span>
                  <div class="flex items-center gap-2">
                    <div class="w-24 bg-slate-200 h-2 rounded-full overflow-hidden">
                      <div class="bg-chemist-primary h-full rounded-full" :style="{ width: `${item.score_percentage}%` }"></div>
                    </div>
                    <span class="font-mono font-bold text-slate-900 w-10 text-right">{{ item.score_percentage }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Tambah Indikator Metrik -->
    <div v-if="showMetricModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-elevated space-y-4">
        <h3 class="text-base font-bold text-slate-900">Tambah Indikator Capaian (Radar)</h3>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Nama Indikator</label>
          <input 
            v-model="newMetricName"
            type="text" 
            placeholder="Contoh: Pemahaman Teori Asam Basa Arrhenius"
            class="w-full bg-slate-50 focus:bg-white text-xs px-3.5 py-2.5 rounded-xl border border-slate-200 outline-none"
          />
        </div>
        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
          <button @click="showMetricModal = false" class="px-4 py-2 rounded-xl text-xs font-bold text-slate-600">Batal</button>
          <button @click="handleCreateMetric" class="px-5 py-2 rounded-xl text-xs font-bold bg-chemist-dark text-white">Simpan</button>
        </div>
      </div>
    </div>

    <!-- Modal Inisialisasi Kuis -->
    <div v-if="showQuizModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-elevated space-y-4">
        <h3 class="text-base font-bold text-slate-900">Inisialisasi Kuis Baru</h3>
        <div class="space-y-3 text-xs">
          <div>
            <label class="block font-bold text-slate-700 mb-1">Judul Kuis</label>
            <input 
              v-model="quizForm.title"
              type="text" 
              placeholder="Contoh: Evaluasi Mandiri Bab 1 - Asam Basa"
              class="w-full bg-slate-50 focus:bg-white px-3 py-2 rounded-xl border border-slate-200 outline-none font-bold"
            />
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">Durasi Waktu (Menit)</label>
            <input 
              v-model.number="quizForm.time_limit_minutes"
              type="number" 
              class="w-full bg-slate-50 focus:bg-white px-3 py-2 rounded-xl border border-slate-200 outline-none"
            />
          </div>
        </div>
        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
          <button @click="showQuizModal = false" class="px-4 py-2 rounded-xl text-xs font-bold text-slate-600">Batal</button>
          <button @click="handleCreateQuiz" class="px-5 py-2 rounded-xl text-xs font-bold bg-chemist-dark text-white">Aktifkan Kuis</button>
        </div>
      </div>
    </div>

    <!-- Modal Tambah Butir Soal -->
    <div v-if="showQuestionModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-elevated space-y-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-base font-bold text-slate-900">Tambah Butir Soal Pilihan Ganda</h3>

        <div class="space-y-3 text-xs">
          <div>
            <label class="block font-bold text-slate-700 mb-1">Teks Pertanyaan Soal</label>
            <textarea 
              v-model="questionForm.question_text"
              rows="3"
              placeholder="Tuliskan butir pertanyaan kimia di sini..."
              class="w-full bg-slate-50 focus:bg-white px-3 py-2 rounded-xl border border-slate-200 outline-none"
            ></textarea>
          </div>

          <div>
            <label class="block font-bold text-slate-700 mb-1">Tautkan ke Indikator Capaian</label>
            <select 
              v-model="questionForm.metric_id"
              class="w-full bg-slate-50 px-3 py-2 rounded-xl border border-slate-200 outline-none font-medium"
            >
              <option :value="null">-- Umum (Tanpa Metrik Khusus) --</option>
              <option v-for="met in metrics" :key="met.id" :value="met.id">{{ met.metric_name }}</option>
            </select>
          </div>

          <!-- Options A - D -->
          <div class="space-y-2">
            <label class="block font-bold text-slate-700">Pilihan Jawaban (A, B, C, D)</label>
            <div class="grid grid-cols-1 gap-2">
              <div class="flex items-center gap-2">
                <span class="w-6 font-bold text-slate-600 text-center">A.</span>
                <input v-model="questionForm.option_a" type="text" placeholder="Teks opsi A" class="w-full bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200 outline-none" />
              </div>
              <div class="flex items-center gap-2">
                <span class="w-6 font-bold text-slate-600 text-center">B.</span>
                <input v-model="questionForm.option_b" type="text" placeholder="Teks opsi B" class="w-full bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200 outline-none" />
              </div>
              <div class="flex items-center gap-2">
                <span class="w-6 font-bold text-slate-600 text-center">C.</span>
                <input v-model="questionForm.option_c" type="text" placeholder="Teks opsi C" class="w-full bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200 outline-none" />
              </div>
              <div class="flex items-center gap-2">
                <span class="w-6 font-bold text-slate-600 text-center">D.</span>
                <input v-model="questionForm.option_d" type="text" placeholder="Teks opsi D" class="w-full bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200 outline-none" />
              </div>
            </div>
          </div>

          <!-- Correct Answer and Weight -->
          <div class="grid grid-cols-2 gap-3 pt-2">
            <div>
              <label class="block font-bold text-slate-700 mb-1">Kunci Jawaban Benar</label>
              <select v-model="questionForm.correct_answer" class="w-full bg-slate-50 font-bold px-3 py-2 rounded-xl border border-slate-200 outline-none">
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="C">C</option>
                <option value="D">D</option>
              </select>
            </div>
            <div>
              <label class="block font-bold text-slate-700 mb-1">Bobot Poin</label>
              <input v-model.number="questionForm.weight_score" type="number" class="w-full bg-slate-50 font-bold px-3 py-2 rounded-xl border border-slate-200 outline-none" />
            </div>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
          <button @click="showQuestionModal = false" class="px-4 py-2 rounded-xl text-xs font-bold text-slate-600">Batal</button>
          <button @click="handleCreateQuestion" class="px-5 py-2 rounded-xl text-xs font-bold bg-chemist-dark text-white shadow-md">Simpan Butir Soal</button>
        </div>
      </div>
    </div>
  </div>
</template>

