<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  Award, 
  Send, 
  ArrowLeft, 
  RefreshCw,
  HelpCircle,
  BarChart2
} from 'lucide-vue-next'
import { api } from '@/api/client'

const props = defineProps({
  quiz: Object,
  student: Object
})

const emit = defineEmits(['finish', 'back'])

const loading = ref(true)
const submitting = ref(false)
const error = ref('')

const questions = ref([])
const currentIndex = ref(0)
const selectedAnswers = ref({}) // { [questionId]: 'A' | 'B' | ... }
const currentAttempt = ref(null)

// Timer
const timeLeftSeconds = ref(0)
let timerInterval = null

const currentQuestion = computed(() => {
  if (questions.value.length === 0) return null
  return questions.value[currentIndex.value]
})

const progressPercent = computed(() => {
  if (questions.value.length === 0) return 0
  const answeredCount = Object.keys(selectedAnswers.value).length
  return Math.round((answeredCount / questions.value.length) * 100)
})

const formattedTime = computed(() => {
  const m = Math.floor(timeLeftSeconds.value / 60)
  const s = timeLeftSeconds.value % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

// Result View after submit
const quizResult = ref(null)

const startQuizSession = async () => {
  loading.value = true
  error.value = ''
  try {
    // 1. Fetch questions student view
    const qList = await api.assessment.listQuestionsStudent(props.quiz.uuid)
    questions.value = qList || []

    if (questions.value.length === 0) {
      error.value = 'Kuis ini belum memiliki daftar pertanyaan dari guru.'
      loading.value = false
      return
    }

    // 2. Start attempt
    const attempt = await api.assessment.startAttempt(props.quiz.id, props.student?.id)
    currentAttempt.value = attempt

    // 3. Initialize timer
    timeLeftSeconds.value = (props.quiz.time_limit_minutes || 15) * 60
    timerInterval = setInterval(() => {
      if (timeLeftSeconds.value > 0) {
        timeLeftSeconds.value--
      } else {
        clearInterval(timerInterval)
        handleSubmitQuiz(true) // Auto submit on timeout
      }
    }, 1000)

  } catch (err) {
    error.value = err.message || 'Gagal memulai sesi kuis.'
  } finally {
    loading.value = false
  }
}

const selectAnswer = async (questionId, optionLetter) => {
  if (quizResult.value) return
  selectedAnswers.value[questionId] = optionLetter

  // Auto-save to backend
  if (currentAttempt.value?.id) {
    try {
      await api.assessment.saveAnswer(currentAttempt.value.id, questionId, optionLetter)
    } catch (e) {
      console.warn('Gagal auto-save jawaban:', e)
    }
  }
}

const handleSubmitQuiz = async (isAuto = false) => {
  if (!currentAttempt.value?.uuid) return
  if (!isAuto) {
    const unanswered = questions.value.length - Object.keys(selectedAnswers.value).length
    if (unanswered > 0) {
      if (!confirm(`Masih ada ${unanswered} pertanyaan yang belum dijawab. Yakin ingin mengumpulkan kuis?`)) {
        return
      }
    }
  }

  submitting.value = true
  if (timerInterval) clearInterval(timerInterval)

  try {
    const res = await api.assessment.submitAttempt(currentAttempt.value.uuid)
    quizResult.value = res
  } catch (err) {
    alert('Gagal mengumpulkan kuis: ' + err.message)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  startQuizSession()
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header Back bar -->
    <div class="flex items-center justify-between">
      <button 
        @click="emit('back')"
        class="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-white px-3 py-2 rounded-xl border border-slate-200 transition-all shadow-2xs"
      >
        <ArrowLeft class="w-3.5 h-3.5" />
        <span>Kembali ke Daftar Kuis</span>
      </button>

      <div v-if="!quizResult && !loading && questions.length > 0" class="flex items-center gap-3">
        <!-- Timer Pill -->
        <div 
          :class="timeLeftSeconds < 120 ? 'bg-rose-50 text-rose-700 border-rose-200 animate-pulse' : 'bg-white text-slate-700 border-slate-200'"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-mono font-bold shadow-2xs"
        >
          <Clock class="w-3.5 h-3.5" />
          <span>{{ formattedTime }}</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-3xl border border-slate-200 p-12 text-center space-y-3">
      <RefreshCw class="w-8 h-8 animate-spin text-chemist-primary mx-auto" />
      <p class="text-xs font-semibold text-slate-500">Menyiapkan lembar soal asesmen...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-white rounded-3xl border border-slate-200 p-12 text-center space-y-4">
      <AlertCircle class="w-10 h-10 text-rose-500 mx-auto" />
      <h3 class="text-sm font-bold text-slate-800">Tidak Dapat Memulai Kuis</h3>
      <p class="text-xs text-slate-500 max-w-sm mx-auto">{{ error }}</p>
      <button 
        @click="emit('back')" 
        class="px-4 py-2 bg-chemist-dark text-white rounded-xl text-xs font-bold"
      >
        Kembali
      </button>
    </div>

    <!-- RESULT VIEW AFTER SUBMIT -->
    <div v-else-if="quizResult" class="bg-white rounded-3xl border border-slate-200/80 p-8 shadow-sm space-y-6">
      <div class="text-center space-y-2 max-w-md mx-auto">
        <div class="w-16 h-16 rounded-3xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto shadow-inner">
          <Award class="w-8 h-8" />
        </div>
        <h2 class="text-xl font-extrabold text-slate-900 tracking-tight">Kuis Selesai Dikerjakan!</h2>
        <p class="text-xs text-slate-500">Nilai dan capaian kompetensi radar sains kamu telah direkam ke sistem.</p>
      </div>

      <!-- Score Box -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-xl mx-auto">
        <div class="bg-slate-50 border border-slate-200 rounded-2xl p-4 text-center">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Skor Akhir</span>
          <span class="text-3xl font-black text-chemist-dark">{{ quizResult.total_score }}</span>
          <span class="text-xs text-slate-400 block">/ 100</span>
        </div>

        <div class="bg-slate-50 border border-slate-200 rounded-2xl p-4 text-center">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Status</span>
          <span 
            :class="quizResult.total_score >= 70 ? 'text-emerald-600' : 'text-amber-600'"
            class="text-lg font-bold block mt-1"
          >
            {{ quizResult.total_score >= 70 ? 'Tuntas' : 'Perlu Remedial' }}
          </span>
          <span class="text-[11px] text-slate-400">KKM: 70</span>
        </div>

        <div class="bg-slate-50 border border-slate-200 rounded-2xl p-4 text-center">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Total Soal</span>
          <span class="text-2xl font-bold text-slate-800 block mt-0.5">{{ questions.length }}</span>
          <span class="text-[11px] text-slate-400">Pertanyaan</span>
        </div>
      </div>

      <!-- Radar Assessment Snapshot -->
      <div v-if="quizResult.radar_snapshot && Object.keys(quizResult.radar_snapshot).length > 0" class="max-w-xl mx-auto space-y-3">
        <h4 class="text-xs font-bold text-slate-700 flex items-center gap-1.5">
          <BarChart2 class="w-4 h-4 text-chemist-primary" />
          <span>Capaian Metrik Kompetensi Kimia:</span>
        </h4>
        <div class="space-y-2">
          <div 
            v-for="(val, metric) in quizResult.radar_snapshot" 
            :key="metric"
            class="bg-slate-50 border border-slate-200/80 rounded-xl p-3 flex items-center justify-between text-xs"
          >
            <span class="font-semibold text-slate-700 capitalize">{{ metric.replace('_', ' ') }}</span>
            <div class="flex items-center gap-3">
              <div class="w-32 bg-slate-200 rounded-full h-2 overflow-hidden hidden sm:block">
                <div class="bg-chemist-primary h-2 rounded-full" :style="{ width: `${Math.min(val, 100)}%` }"></div>
              </div>
              <span class="font-bold text-slate-900 w-8 text-right">{{ val }}%</span>
            </div>
          </div>
        </div>
      </div>

      <div class="pt-4 border-t border-slate-100 flex justify-center">
        <button 
          @click="emit('finish')" 
          class="px-6 py-2.5 bg-chemist-dark hover:bg-slate-900 text-white rounded-xl text-xs font-bold shadow-md transition-all"
        >
          Selesai & Kembali
        </button>
      </div>
    </div>

    <!-- ACTIVE QUESTION WORKSPACE -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <!-- Left: Question Card (8 Cols) -->
      <div class="lg:col-span-8 bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm space-y-6">
        <!-- Progress Bar & Question Counter -->
        <div class="space-y-2 pb-4 border-b border-slate-100">
          <div class="flex items-center justify-between text-xs font-semibold text-slate-500">
            <span>Soal No. {{ currentIndex + 1 }} dari {{ questions.length }}</span>
            <span>{{ progressPercent }}% Terjawab</span>
          </div>
          <div class="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
            <div 
              class="bg-chemist-primary h-1.5 rounded-full transition-all duration-300"
              :style="{ width: `${progressPercent}%` }"
            ></div>
          </div>
        </div>

        <!-- Question Text -->
        <div v-if="currentQuestion" class="space-y-4">
          <p class="text-sm sm:text-base font-bold text-slate-900 leading-relaxed">
            {{ currentQuestion.question_text }}
          </p>

          <!-- Options -->
          <div class="space-y-2.5 pt-2">
            <button
              v-for="opt in ['A', 'B', 'C', 'D']"
              :key="opt"
              v-show="currentQuestion[`option_${opt.toLowerCase()}`]"
              @click="selectAnswer(currentQuestion.id, opt)"
              :class="[
                'w-full text-left p-3.5 rounded-2xl border transition-all flex items-start gap-3 text-xs leading-relaxed',
                selectedAnswers[currentQuestion.id] === opt
                  ? 'border-chemist-primary bg-blue-50/70 text-slate-900 font-semibold shadow-2xs'
                  : 'border-slate-200 bg-white hover:bg-slate-50 text-slate-700'
              ]"
            >
              <span 
                :class="selectedAnswers[currentQuestion.id] === opt ? 'bg-chemist-primary text-white' : 'bg-slate-100 text-slate-600'"
                class="w-6 h-6 rounded-lg font-bold flex items-center justify-center shrink-0 text-xs"
              >
                {{ opt }}
              </span>
              <span class="pt-0.5">{{ currentQuestion[`option_${opt.toLowerCase()}`] }}</span>
            </button>
          </div>
        </div>

        <!-- Question Navigation Buttons -->
        <div class="pt-4 border-t border-slate-100 flex items-center justify-between">
          <button
            @click="currentIndex--"
            :disabled="currentIndex === 0"
            class="px-4 py-2 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-40 transition-all"
          >
            ← Sebelumnya
          </button>

          <button
            v-if="currentIndex < questions.length - 1"
            @click="currentIndex++"
            class="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition-all"
          >
            Selanjutnya →
          </button>

          <button
            v-else
            @click="handleSubmitQuiz(false)"
            :disabled="submitting"
            class="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shadow-md shadow-emerald-600/20"
          >
            <Send class="w-3.5 h-3.5" />
            <span>{{ submitting ? 'Mengirim...' : 'Kumpulkan Jawaban' }}</span>
          </button>
        </div>
      </div>

      <!-- Right: Question Number Grid Palette (4 Cols) -->
      <div class="lg:col-span-4 bg-white rounded-3xl border border-slate-200/80 p-5 shadow-sm space-y-4">
        <h4 class="text-xs font-bold text-slate-700">Navigasi Soal</h4>
        <div class="grid grid-cols-5 gap-2">
          <button
            v-for="(q, idx) in questions"
            :key="q.id"
            @click="currentIndex = idx"
            :class="[
              'h-9 rounded-xl text-xs font-bold transition-all flex items-center justify-center',
              currentIndex === idx
                ? 'ring-2 ring-chemist-primary ring-offset-1 font-black'
                : '',
              selectedAnswers[q.id]
                ? 'bg-chemist-primary text-white shadow-2xs'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            ]"
          >
            {{ idx + 1 }}
          </button>
        </div>

        <div class="pt-3 border-t border-slate-100 space-y-2 text-[11px] text-slate-500 font-medium">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-md bg-chemist-primary"></span>
            <span>Sudah dijawab</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-md bg-slate-100 border border-slate-200"></span>
            <span>Belum dijawab</span>
          </div>
        </div>

        <div class="pt-2">
          <button
            @click="handleSubmitQuiz(false)"
            :disabled="submitting"
            class="w-full py-2.5 bg-chemist-dark hover:bg-slate-900 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition-all shadow-md"
          >
            {{ submitting ? 'Memproses...' : 'Selesai & Kumpulkan' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
