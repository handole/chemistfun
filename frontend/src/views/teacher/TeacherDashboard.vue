<script setup>
import { ref, onMounted } from 'vue'
import {
  Users,
  FlaskConical,
  CheckSquare,
  Plus,
  Copy,
  Check,
  ArrowRight,
  AlertTriangle,
  RefreshCw
} from 'lucide-vue-next'
import { api } from '@/api/client'

const props = defineProps({
  user: Object
})

const emit = defineEmits(['navigate'])

const loading = ref(true)
const error = ref(null)
const classesList = ref([])
const copiedCode = ref(null)

const stats = ref({
  totalClasses: 0,
  totalStudents: 0,
  totalModules: 0,
  totalAttempts: 0
})

const fetchDashboardData = async () => {
  loading.value = true
  error.value = null
  try {
    const [cls, modulesRes, attemptsRes] = await Promise.all([
      api.classes.list(null, true),
      api.content.listModules(),
      api.assessment.listAttempts()
    ])

    classesList.value = cls || []
    stats.value.totalClasses = classesList.value.length
    stats.value.totalModules = Array.isArray(modulesRes) ? modulesRes.length : 0
    stats.value.totalAttempts = Array.isArray(attemptsRes) ? attemptsRes.length : 0

    if (classesList.value.length > 0) {
      const studentResults = await Promise.allSettled(
        classesList.value.map((c) => api.classes.getStudents(c.uuid))
      )
      stats.value.totalStudents = studentResults.reduce((acc, curr) => {
        return acc + (curr.status === 'fulfilled' && Array.isArray(curr.value) ? curr.value.length : 0)
      }, 0)
    } else {
      stats.value.totalStudents = 0
    }
  } catch (err) {
    console.error('Failed to load dashboard data:', err)
    error.value = err.message || 'Server tidak mengirim data dashboard.'
  } finally {
    loading.value = false
  }
}

const copyEnrollmentCode = async (code) => {
  try {
    await navigator.clipboard.writeText(code)
    copiedCode.value = code
    setTimeout(() => {
      copiedCode.value = null
    }, 2000)
  } catch (err) {
    console.error('Clipboard tidak tersedia:', err)
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<template>
  <div class="space-y-5">
    <!-- Page header: one focal statement, quiet supporting copy -->
    <section class="rounded-xl border border-line bg-surface p-5 sm:p-6">
      <div class="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
        <div class="max-w-2xl">
          <p class="text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Ruang guru</p>
          <h1 class="mt-1.5 text-xl font-semibold leading-snug tracking-tight text-ink sm:text-2xl">
            {{ user?.full_name || 'Guru kimia' }}
          </h1>
          <p class="mt-2 text-sm leading-relaxed text-ink-muted">
            Mulai dari daftar kelas di bawah: bagikan kode pendaftaran, lalu siswa langsung masuk ke modul dan
            laboratorium yang kamu siapkan.
          </p>
        </div>

        <div class="flex shrink-0 flex-wrap gap-2">
            <button
              type="button"
              @click="emit('navigate', 'classes')"
              class="inline-flex min-h-[44px] items-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-ink-soft"
            >
              <Plus class="h-4 w-4 text-accent-300" aria-hidden="true" />
              Buat kelas
            </button>
            <button
              type="button"
              @click="emit('navigate', 'content')"
              class="inline-flex min-h-[44px] items-center gap-2 rounded-md border border-line bg-surface px-4 py-2.5 text-sm font-semibold text-ink-soft transition-colors hover:bg-sunken"
            >
              Kelola modul
            </button>
        </div>
      </div>
    </section>

    <!-- Supporting metrics: real counts only, no deltas -->
    <section class="grid grid-cols-1 gap-3 sm:grid-cols-3" aria-label="Ringkasan data">
      <div class="rounded-xl border border-line bg-surface px-4 py-3.5">
        <div class="flex items-center justify-between">
          <p class="text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Siswa tergabung</p>
          <Users class="h-4 w-4 text-ink-faint" aria-hidden="true" />
        </div>
        <p class="mt-1.5 font-mono text-2xl font-semibold tabular-nums text-ink">{{ stats.totalStudents }}</p>
        <p class="mt-0.5 text-xs text-ink-muted">Di {{ stats.totalClasses }} kelas aktif</p>
      </div>

      <div class="rounded-xl border border-line bg-surface px-4 py-3.5">
        <div class="flex items-center justify-between">
          <p class="text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Modul praktikum</p>
          <FlaskConical class="h-4 w-4 text-ink-faint" aria-hidden="true" />
        </div>
        <p class="mt-1.5 font-mono text-2xl font-semibold tabular-nums text-ink">{{ stats.totalModules }}</p>
        <p class="mt-0.5 text-xs text-ink-muted">Siap dipakai di kelas</p>
      </div>

      <div class="rounded-xl border border-line bg-surface px-4 py-3.5">
        <div class="flex items-center justify-between">
          <p class="text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Asesmen masuk</p>
          <CheckSquare class="h-4 w-4 text-ink-faint" aria-hidden="true" />
        </div>
        <p class="mt-1.5 font-mono text-2xl font-semibold tabular-nums text-ink">{{ stats.totalAttempts }}</p>
        <p class="mt-0.5 text-xs text-ink-muted">Pengerjaan kuis siswa</p>
      </div>
    </section>

    <!-- Focal block: the class roster -->
    <section class="overflow-hidden rounded-xl border border-line bg-surface">
      <div class="flex flex-wrap items-end justify-between gap-2 border-b border-line px-4 py-3.5">
        <div>
          <h2 class="text-sm font-semibold text-ink">Kelas kimia aktif</h2>
          <p class="mt-0.5 text-xs text-ink-muted">Bagikan kode pendaftaran agar siswa bergabung sendiri.</p>
        </div>
        <button
          type="button"
          @click="emit('navigate', 'classes')"
          class="inline-flex min-h-[36px] items-center gap-1.5 rounded-md px-2 text-xs font-semibold text-accent transition-colors hover:bg-accent-50"
        >
          Kelola semua kelas
          <ArrowRight class="h-3.5 w-3.5" aria-hidden="true" />
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex items-center gap-2 px-4 py-8 text-xs text-ink-muted">
        <RefreshCw class="h-3.5 w-3.5 animate-spin text-accent" aria-hidden="true" />
        Memuat daftar kelas dari server
      </div>

      <!-- Error -->
      <div v-else-if="error" class="px-4 py-8">
        <div class="flex items-start gap-2.5">
          <AlertTriangle class="mt-0.5 h-4 w-4 shrink-0 text-danger-600" aria-hidden="true" />
          <div>
            <p class="text-sm font-semibold text-ink">Daftar kelas gagal dimuat</p>
            <p class="mt-0.5 text-xs leading-relaxed text-ink-muted">{{ error }}</p>
            <button
              type="button"
              @click="fetchDashboardData"
              class="mt-3 inline-flex min-h-[36px] items-center gap-2 rounded-md border border-line px-3 text-xs font-semibold text-ink-soft transition-colors hover:bg-sunken"
            >
              <RefreshCw class="h-3.5 w-3.5" aria-hidden="true" />
              Coba lagi
            </button>
          </div>
        </div>
      </div>

      <!-- Empty -->
      <div v-else-if="classesList.length === 0" class="px-4 py-8">
        <p class="text-sm font-semibold text-ink">Belum ada kelas</p>
        <p class="mt-0.5 max-w-md text-xs leading-relaxed text-ink-muted">
          Kelas dibutuhkan sebelum siswa bisa menerima modul atau lab. Buat kelas pertama, lalu bagikan kodenya.
        </p>
        <button
          type="button"
          @click="emit('navigate', 'classes')"
          class="mt-3 inline-flex min-h-[36px] items-center gap-2 rounded-md bg-ink px-3 text-xs font-semibold text-white transition-colors hover:bg-ink-soft"
        >
          <Plus class="h-3.5 w-3.5 text-accent-300" aria-hidden="true" />
          Buat kelas
        </button>
      </div>

      <!-- Rows: the code is the action, the row opens the class -->
      <ul v-else class="divide-y divide-line">
        <li
          v-for="cls in classesList"
          :key="cls.id"
          class="flex flex-wrap items-center gap-3 px-4 py-3 transition-colors hover:bg-paper"
        >
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-ink">{{ cls.name }}</p>
            <p class="mt-0.5 text-xs text-ink-muted">
              Kode pendaftaran
              <span class="kf-readout ml-1.5 rounded-sm bg-sunken px-1.5 py-0.5 text-[11px] font-medium text-ink-soft">
                {{ cls.enrollment_code }}
              </span>
            </p>
          </div>

          <div class="flex items-center gap-1.5">
            <button
              type="button"
              @click="copyEnrollmentCode(cls.enrollment_code)"
              class="inline-flex min-h-[36px] items-center gap-1.5 rounded-md border px-2.5 text-xs font-semibold transition-colors"
              :class="
                copiedCode === cls.enrollment_code
                  ? 'border-success-200 bg-success-50 text-success-700'
                  : 'border-line bg-surface text-ink-soft hover:bg-sunken'
              "
              :aria-label="
                copiedCode === cls.enrollment_code
                  ? 'Kode berhasil disalin'
                  : 'Salin kode pendaftaran ' + cls.enrollment_code
              "
            >
              <component :is="copiedCode === cls.enrollment_code ? Check : Copy" class="h-3.5 w-3.5" aria-hidden="true" />
              {{ copiedCode === cls.enrollment_code ? 'Tersalin' : 'Salin' }}
            </button>

            <button
              type="button"
              @click="emit('navigate', 'classes')"
              class="inline-flex min-h-[36px] items-center gap-1.5 rounded-md px-2.5 text-xs font-semibold text-accent transition-colors hover:bg-accent-50"
              :aria-label="'Buka kelas ' + cls.name"
            >
              Buka
              <ArrowRight class="h-3.5 w-3.5" aria-hidden="true" />
            </button>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>
