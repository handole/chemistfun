<script setup>
import { ref, onMounted } from 'vue'
import { 
  Users, 
  BookOpen, 
  FlaskConical, 
  CheckSquare, 
  Plus, 
  Copy, 
  Check, 
  ArrowUpRight, 
  Sparkles,
  ChevronRight
} from 'lucide-vue-next'
import { api } from '@/api/client'

const props = defineProps({
  user: Object
})

const emit = defineEmits(['navigate'])

const loading = ref(true)
const classesList = ref([])
const copiedCode = ref(null)

const stats = ref({
  totalClasses: 0,
  totalStudents: 0,
  totalModules: 0,
  totalQuizzes: 0
})

const fetchDashboardData = async () => {
  loading.value = true
  try {
    const cls = await api.classes.list()
    classesList.value = cls || []
    stats.value.totalClasses = classesList.value.length

    // Count students from classes
    let totalStud = 0
    for (const c of classesList.value) {
      try {
        const students = await api.classes.getStudents(c.uuid)
        totalStud += students?.length || 0
      } catch (e) {
        // ignore
      }
    }
    stats.value.totalStudents = totalStud
  } catch (err) {
    console.error('Failed to load dashboard data:', err)
  } finally {
    loading.value = false
  }
}

const copyEnrollmentCode = (code) => {
  navigator.clipboard.writeText(code)
  copiedCode.value = code
  setTimeout(() => {
    copiedCode.value = null
  }, 2000)
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Hero Welcome Banner (Styling inspired by mockup) -->
    <div class="relative bg-gradient-to-r from-slate-50 via-indigo-50/40 to-blue-50/50 border border-indigo-100/60 rounded-3xl p-6 sm:p-8 overflow-hidden shadow-soft">
      <!-- Decorative background blur -->
      <div class="absolute -right-12 -top-12 w-64 h-64 bg-indigo-200/30 rounded-full blur-3xl pointer-events-none"></div>

      <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
        <div class="space-y-3 max-w-xl">
          <!-- Status pill -->
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100/80 text-emerald-800 text-xs font-bold">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
            <span>Ruang Guru ChemistFun Siap Digunakan</span>
          </div>

          <h2 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Halo, {{ user?.full_name || 'Guru Kimia' }}! 👋<br />
            <span class="text-chemist-primary">Pantau eksperimen kimia siswa hari ini.</span>
          </h2>

          <p class="text-sm text-slate-600 leading-relaxed font-medium">
            Kelola ruang kelas, bagikan materi interaktif, atur simulasi laboratorium virtual, dan lihat capaian radar pemahaman konsep kimia siswa.
          </p>

          <div class="flex flex-wrap items-center gap-3 pt-2">
            <button 
              @click="emit('navigate', 'classes')"
              class="inline-flex items-center gap-2 bg-chemist-dark hover:bg-slate-900 text-white text-xs sm:text-sm font-bold px-5 py-2.5 rounded-xl shadow-md transition-all active:scale-95"
            >
              <Plus class="w-4 h-4 text-emerald-400" />
              <span>Buat Kelas Baru</span>
            </button>
            <button 
              @click="emit('navigate', 'content')"
              class="inline-flex items-center gap-2 bg-white hover:bg-slate-100 text-slate-700 text-xs sm:text-sm font-bold px-4 py-2.5 rounded-xl border border-slate-200 shadow-2xs transition-all active:scale-95"
            >
              <span>Kelola Materi</span>
            </button>
          </div>
        </div>

        <!-- Right: Modern Lab Flask Illustration (From mockup design) -->
        <div class="hidden md:flex items-center gap-3 p-5 bg-white/80 backdrop-blur-md rounded-2xl border border-white shadow-card">
          <div class="w-16 h-20 bg-amber-100/80 border-2 border-amber-300 rounded-xl flex flex-col justify-end p-2 relative overflow-hidden">
            <div class="h-8 bg-amber-400/90 rounded-b-lg"></div>
            <div class="text-[9px] font-bold text-amber-900 absolute top-2 left-2">HCI</div>
          </div>
          <div class="w-16 h-20 bg-sky-100/80 border-2 border-sky-300 rounded-2xl flex flex-col justify-end p-2 relative overflow-hidden">
            <div class="h-10 bg-sky-400/90 rounded-b-xl"></div>
            <div class="text-[9px] font-bold text-sky-900 absolute top-2 left-2">NaOH</div>
          </div>
          <div class="w-12 h-12 bg-chemist-dark rounded-xl flex items-center justify-center text-white shadow-md">
            <Sparkles class="w-6 h-6 text-purple-400" />
          </div>
        </div>
      </div>
    </div>

    <!-- Stat Cards Row (4 cards matching mockup styling) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Card 1: Total Kelas -->
      <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-card hover:shadow-soft transition-all">
        <div class="flex items-center justify-between text-xs font-semibold text-slate-500 mb-3">
          <div class="w-8 h-8 rounded-lg bg-blue-50 text-chemist-primary flex items-center justify-center">
            <Users class="w-4 h-4" />
          </div>
          <span class="bg-blue-50 text-chemist-primary text-[10px] font-bold px-2 py-0.5 rounded-full">Aktif</span>
        </div>
        <p class="text-xs font-semibold text-slate-400">KELAS SAYA</p>
        <div class="flex items-baseline gap-2 mt-1">
          <span class="text-2xl font-extrabold text-slate-900">{{ stats.totalClasses }}</span>
          <span class="text-xs text-slate-500 font-medium">kelas aktif</span>
        </div>
      </div>

      <!-- Card 2: Total Siswa -->
      <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-card hover:shadow-soft transition-all">
        <div class="flex items-center justify-between text-xs font-semibold text-slate-500 mb-3">
          <div class="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
            <BookOpen class="w-4 h-4" />
          </div>
          <span class="bg-purple-50 text-purple-600 text-[10px] font-bold px-2 py-0.5 rounded-full">Terdaftar</span>
        </div>
        <p class="text-xs font-semibold text-slate-400">TOTAL SISWA</p>
        <div class="flex items-baseline gap-2 mt-1">
          <span class="text-2xl font-extrabold text-slate-900">{{ stats.totalStudents }}</span>
          <span class="text-xs text-slate-500 font-medium">siswa bergabung</span>
        </div>
      </div>

      <!-- Card 3: Modul Pembelajaran -->
      <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-card hover:shadow-soft transition-all">
        <div class="flex items-center justify-between text-xs font-semibold text-slate-500 mb-3">
          <div class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <FlaskConical class="w-4 h-4" />
          </div>
          <span class="bg-emerald-50 text-emerald-600 text-[10px] font-bold px-2 py-0.5 rounded-full">Silabus</span>
        </div>
        <p class="text-xs font-semibold text-slate-400">MATERI & LAB</p>
        <div class="flex items-baseline gap-2 mt-1">
          <span class="text-2xl font-extrabold text-slate-900">{{ stats.totalClasses * 3 || 3 }}</span>
          <span class="text-xs text-slate-500 font-medium">topik kimia</span>
        </div>
      </div>

      <!-- Card 4: Kuis & Radar -->
      <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-card hover:shadow-soft transition-all">
        <div class="flex items-center justify-between text-xs font-semibold text-slate-500 mb-3">
          <div class="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
            <CheckSquare class="w-4 h-4" />
          </div>
          <span class="bg-amber-50 text-amber-600 text-[10px] font-bold px-2 py-0.5 rounded-full">Radar</span>
        </div>
        <p class="text-xs font-semibold text-slate-400">ANALISIS ASESMEN</p>
        <div class="flex items-baseline gap-2 mt-1">
          <span class="text-2xl font-extrabold text-slate-900">100%</span>
          <span class="text-xs text-slate-500 font-medium">otomatis dihitung</span>
        </div>
      </div>
    </div>

    <!-- Active Classes Section -->
    <div class="bg-white rounded-3xl border border-slate-100 p-6 shadow-card">
      <div class="flex items-center justify-between mb-5">
        <div>
          <h3 class="text-lg font-bold text-slate-900 tracking-tight">Daftar Kelas Kimia Aktif</h3>
          <p class="text-xs text-slate-400 font-medium mt-0.5">Bagikan kode enrollment ke siswa untuk bergabung secara mandiri.</p>
        </div>
        <button 
          @click="emit('navigate', 'classes')"
          class="text-xs font-bold text-chemist-primary hover:text-blue-700 flex items-center gap-1"
        >
          <span>Lihat Semua</span>
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-12 text-center text-slate-400 text-sm">
        Memuat data kelas dari backend...
      </div>

      <!-- Empty State -->
      <div v-else-if="classesList.length === 0" class="py-12 text-center">
        <div class="w-12 h-12 rounded-2xl bg-blue-50 text-chemist-primary flex items-center justify-center mx-auto mb-3">
          <Users class="w-6 h-6" />
        </div>
        <h4 class="font-bold text-slate-800">Belum Ada Kelas yang Dibuat</h4>
        <p class="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">Buat kelas pertama Anda sekarang untuk mulai menambahkan modul dan mengundang siswa.</p>
        <button 
          @click="emit('navigate', 'classes')"
          class="inline-flex items-center gap-2 bg-chemist-dark hover:bg-slate-900 text-white text-xs font-bold px-4 py-2 rounded-xl shadow-sm"
        >
          <Plus class="w-4 h-4" />
          <span>Buat Kelas Sekarang</span>
        </button>
      </div>

      <!-- Classes Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div 
          v-for="cls in classesList" 
          :key="cls.id"
          class="p-5 rounded-2xl border border-slate-100 bg-slate-50/50 hover:bg-white hover:border-indigo-100 hover:shadow-soft transition-all space-y-4"
        >
          <div class="flex items-start justify-between">
            <div>
              <span class="text-[10px] font-bold px-2 py-0.5 bg-blue-100/70 text-blue-800 rounded-md uppercase">Kimia</span>
              <h4 class="font-bold text-slate-900 text-base mt-2">{{ cls.name }}</h4>
            </div>
            <button 
              @click="emit('navigate', 'classes')"
              class="w-8 h-8 rounded-lg bg-white border border-slate-200 text-slate-500 hover:text-slate-900 flex items-center justify-center shadow-2xs"
              title="Buka Kelas"
            >
              <ArrowUpRight class="w-4 h-4" />
            </button>
          </div>

          <!-- Code Badge -->
          <div class="bg-white p-3 rounded-xl border border-slate-200/70 flex items-center justify-between">
            <div>
              <p class="text-[10px] font-bold text-slate-400 uppercase">KODE ENROLLMENT</p>
              <span class="font-mono font-bold text-sm text-slate-800 tracking-wider">{{ cls.enrollment_code }}</span>
            </div>
            <button 
              @click="copyEnrollmentCode(cls.enrollment_code)"
              class="text-xs px-2.5 py-1.5 rounded-lg border font-semibold flex items-center gap-1.5 transition-colors"
              :class="copiedCode === cls.enrollment_code ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'"
            >
              <component :is="copiedCode === cls.enrollment_code ? Check : Copy" class="w-3.5 h-3.5" />
              <span>{{ copiedCode === cls.enrollment_code ? 'Tersalin' : 'Salin' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

