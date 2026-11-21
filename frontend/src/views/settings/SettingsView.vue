<script setup>
import { UserRound, Server, CheckCircle2, AlertTriangle, RotateCcw, LogOut } from 'lucide-vue-next'

const props = defineProps({
  user: Object,
  backendOnline: Boolean
})

const emit = defineEmits(['logout', 'refresh'])

const roleLabel = (role) => {
  if (role === 'teacher') return 'Guru'
  if (role === 'student') return 'Siswa'
  return 'Belum ditentukan'
}
</script>

<template>
  <div class="max-w-3xl space-y-4">
    <header>
      <h1 class="text-xl font-semibold tracking-tight text-ink">Pengaturan</h1>
      <p class="mt-1 text-xs leading-relaxed text-ink-muted">
        Data akun yang dipakai untuk masuk, dan status koneksi ke server KimiFun.
      </p>
    </header>

    <!-- Account -->
    <section class="rounded-xl border border-line bg-surface">
      <div class="flex items-center gap-2.5 border-b border-line px-5 py-3.5">
        <UserRound class="h-4 w-4 text-ink-faint" aria-hidden="true" />
        <h2 class="text-sm font-semibold text-ink">Akun</h2>
      </div>

      <dl class="grid grid-cols-1 gap-px bg-line sm:grid-cols-2">
        <div class="bg-surface px-5 py-3.5">
          <dt class="text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Nama lengkap</dt>
          <dd class="mt-1 text-sm font-semibold text-ink">{{ user?.full_name || 'Belum tersedia' }}</dd>
        </div>

        <div class="bg-surface px-5 py-3.5">
          <dt class="text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Email</dt>
          <dd class="mt-1 truncate text-sm font-semibold text-ink">{{ user?.email || 'Belum tersedia' }}</dd>
        </div>

        <div class="bg-surface px-5 py-3.5">
          <dt class="text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Peran</dt>
          <dd class="mt-1 text-sm font-semibold text-ink">{{ roleLabel(user?.role) }}</dd>
        </div>

        <div class="bg-surface px-5 py-3.5">
          <dt class="text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">ID akun</dt>
          <dd class="kf-readout mt-1 truncate text-xs text-ink-soft">{{ user?.uuid || 'Belum tersedia' }}</dd>
        </div>
      </dl>

      <div class="border-t border-line px-5 py-3.5">
        <button
          type="button"
          @click="emit('logout')"
          class="inline-flex min-h-[38px] items-center gap-1.5 rounded-md border border-line px-3 text-xs font-semibold text-danger-700 transition-colors hover:bg-danger-50"
        >
          <LogOut class="h-3.5 w-3.5" aria-hidden="true" />
          Keluar dari akun
        </button>
      </div>
    </section>

    <!-- Backend -->
    <section class="rounded-xl border border-line bg-surface">
      <div class="flex flex-wrap items-center justify-between gap-2 border-b border-line px-5 py-3.5">
        <div class="flex items-center gap-2.5">
          <Server class="h-4 w-4 text-ink-faint" aria-hidden="true" />
          <h2 class="text-sm font-semibold text-ink">Koneksi server</h2>
        </div>
        <button
          type="button"
          @click="emit('refresh')"
          class="inline-flex min-h-[36px] items-center gap-1.5 rounded-md px-2 text-xs font-semibold text-accent transition-colors hover:bg-accent-50"
        >
          <RotateCcw class="h-3.5 w-3.5" aria-hidden="true" />
          Periksa ulang
        </button>
      </div>

      <div class="px-5 py-4">
        <div
          class="flex items-start gap-2.5 rounded-lg border px-3.5 py-3"
          :class="backendOnline ? 'border-success-200 bg-success-50' : 'border-danger-200 bg-danger-50'"
          role="status"
        >
          <component
            :is="backendOnline ? CheckCircle2 : AlertTriangle"
            class="mt-0.5 h-4 w-4 shrink-0"
            :class="backendOnline ? 'text-success-700' : 'text-danger-700'"
            aria-hidden="true"
          />
          <div>
            <p class="text-xs font-semibold" :class="backendOnline ? 'text-success-700' : 'text-danger-700'">
              {{ backendOnline ? 'Server merespons' : 'Server tidak merespons' }}
            </p>
            <p class="mt-0.5 text-[11px] leading-relaxed text-ink-muted">
              {{ backendOnline
                ? 'Permintaan data kelas, modul, dan asesmen dapat dilayani.'
                : 'Data mungkin gagal dimuat. Periksa koneksi, lalu periksa ulang status.' }}
            </p>
            <p class="kf-readout mt-1.5 text-[11px] text-ink-faint">Endpoint: /api (relatif terhadap host ini)</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
