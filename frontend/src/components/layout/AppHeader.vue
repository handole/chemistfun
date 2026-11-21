<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { Bell, LogOut, UserRound, RefreshCw, Menu, CheckCircle2, AlertTriangle } from 'lucide-vue-next'

const props = defineProps({
  user: {
    type: Object,
    default: () => ({})
  },
  backendOnline: {
    type: Boolean,
    default: true
  },
  mobileMenuOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['logout', 'open-auth', 'refresh', 'toggle-sidebar'])

const showUserMenu = ref(false)
const showNotifications = ref(false)

const getInitials = (name) => {
  if (!name) return 'KF'
  return name
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .join('')
    .substring(0, 2)
    .toUpperCase()
}

const roleLabel = computed(() => (props.user?.role === 'teacher' ? 'Guru' : 'Siswa'))

const connectionLabel = computed(() => (props.backendOnline ? 'Terhubung ke server' : 'Server tidak merespons'))

const closePanels = () => {
  showUserMenu.value = false
  showNotifications.value = false
}

const handleKeydown = (event) => {
  if (event.key === 'Escape') closePanels()
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <header class="sticky top-0 z-30 h-16 border-b border-line bg-surface px-3 sm:px-5">
    <div class="mx-auto flex h-full max-w-[1600px] items-center justify-between gap-3">
      <!-- Brand -->
      <div class="flex items-center gap-2">
        <button
          type="button"
          @click="emit('toggle-sidebar')"
          class="grid h-11 w-11 place-items-center rounded-lg text-ink-muted transition-colors hover:bg-sunken hover:text-ink md:hidden"
          aria-label="Buka menu navigasi"
          :aria-expanded="mobileMenuOpen"
        >
          <Menu class="h-5 w-5" aria-hidden="true" />
        </button>

        <div class="flex items-center gap-2.5">
          <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-ink">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5 text-accent-300"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.75"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M6 3h12" />
              <path d="M8 3v13a4 4 0 0 0 4 4h0a4 4 0 0 0 4-4V3" />
              <path d="M8 13h8" />
            </svg>
          </span>
          <div class="leading-tight">
            <p class="text-sm font-semibold tracking-tight text-ink">KimiFun</p>
            <p class="text-[11px] text-ink-faint">Lab kimia virtual</p>
          </div>
        </div>
      </div>

      <!-- Account and system -->
      <div class="flex items-center gap-1.5 sm:gap-2">
        <!-- Server state: reflects the real health probe from App.vue -->
        <span
          class="hidden items-center gap-1.5 rounded-md border border-line px-2 py-1 text-[11px] font-medium text-ink-muted sm:inline-flex"
          :title="connectionLabel"
        >
          <span
            class="h-1.5 w-1.5 rounded-full"
            :class="backendOnline ? 'bg-success-600' : 'bg-danger-600'"
            aria-hidden="true"
          ></span>
          {{ backendOnline ? 'Terhubung' : 'Luring' }}
        </span>

        <!-- Notifications -->
        <div class="relative">
          <button
            type="button"
            @click="showNotifications = !showNotifications; showUserMenu = false"
            class="grid h-11 w-11 place-items-center rounded-lg text-ink-muted transition-colors hover:bg-sunken hover:text-ink"
            aria-label="Lihat notifikasi"
            :aria-expanded="showNotifications"
            aria-haspopup="true"
          >
            <Bell class="h-[1.15rem] w-[1.15rem]" aria-hidden="true" />
            <span
              v-if="!backendOnline"
              class="absolute right-2.5 top-2.5 h-1.5 w-1.5 rounded-full bg-danger-600"
              aria-hidden="true"
            ></span>
          </button>

          <div
            v-if="showNotifications"
            class="absolute right-0 z-50 mt-2 w-[min(20rem,calc(100vw-1.5rem))] overflow-hidden rounded-xl border border-line bg-surface shadow-sheet"
            role="region"
            aria-label="Panel notifikasi"
          >
            <div class="flex items-center justify-between border-b border-line px-4 py-3">
              <span class="text-[11px] font-semibold uppercase tracking-[0.04em] text-ink-faint">Notifikasi</span>
              <span
                class="inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[11px] font-semibold"
                :class="backendOnline ? 'bg-success-50 text-success-700' : 'bg-danger-50 text-danger-700'"
              >
                <component :is="backendOnline ? CheckCircle2 : AlertTriangle" class="h-3 w-3" aria-hidden="true" />
                {{ backendOnline ? 'Server normal' : 'Server luring' }}
              </span>
            </div>
            <p class="px-4 py-5 text-xs leading-relaxed text-ink-muted">
              {{
                backendOnline
                  ? 'Tidak ada aktivitas yang menunggu tindakan. Notifikasi tugas dan pengumuman kelas akan muncul di sini.'
                  : 'Server backend tidak merespons. Periksa koneksi lalu muat ulang status dari menu akun.'
              }}
            </p>
          </div>
        </div>

        <!-- Account -->
        <div class="relative">
          <button
            type="button"
            @click="showUserMenu = !showUserMenu; showNotifications = false"
            class="flex h-11 items-center gap-2.5 rounded-lg border border-transparent px-1.5 pr-2.5 text-left transition-colors hover:border-line hover:bg-sunken"
            aria-label="Menu akun"
            :aria-expanded="showUserMenu"
            aria-haspopup="true"
          >
            <span class="grid h-8 w-8 shrink-0 place-items-center rounded-md bg-ink text-[11px] font-semibold text-white">
              {{ getInitials(user?.full_name) }}
            </span>
            <span class="hidden leading-tight sm:block">
              <span class="block max-w-[9rem] truncate text-xs font-semibold text-ink">
                {{ user?.full_name || 'Akun KimiFun' }}
              </span>
              <span class="block text-[11px] text-ink-faint">{{ roleLabel }}</span>
            </span>
          </button>

          <div
            v-if="showUserMenu"
            class="absolute right-0 z-50 mt-2 w-[min(16rem,calc(100vw-1.5rem))] overflow-hidden rounded-xl border border-line bg-surface py-1 shadow-sheet"
            role="menu"
            aria-label="Pilihan akun"
          >
            <div class="border-b border-line px-4 py-3">
              <p class="truncate text-sm font-semibold text-ink">{{ user?.full_name || 'Akun KimiFun' }}</p>
              <p class="truncate text-xs text-ink-muted">{{ user?.email || 'Email belum tersedia' }}</p>
            </div>

            <button
              type="button"
              @click="emit('open-auth'); closePanels()"
              class="flex min-h-[44px] w-full items-center gap-2.5 px-4 py-2.5 text-left text-xs font-medium text-ink-soft transition-colors hover:bg-sunken focus-visible:bg-sunken"
              role="menuitem"
            >
              <UserRound class="h-4 w-4 text-ink-faint" aria-hidden="true" />
              Ganti akun
            </button>
            <button
              type="button"
              @click="emit('refresh'); closePanels()"
              class="flex min-h-[44px] w-full items-center gap-2.5 px-4 py-2.5 text-left text-xs font-medium text-ink-soft transition-colors hover:bg-sunken focus-visible:bg-sunken"
              role="menuitem"
            >
              <RefreshCw class="h-4 w-4 text-ink-faint" aria-hidden="true" />
              Muat ulang status
            </button>

            <div class="mt-1 border-t border-line pt-1">
              <button
                type="button"
                @click="emit('logout'); closePanels()"
                class="flex min-h-[44px] w-full items-center gap-2.5 px-4 py-2.5 text-left text-xs font-semibold text-danger-700 transition-colors hover:bg-danger-50 focus-visible:bg-danger-50"
                role="menuitem"
              >
                <LogOut class="h-4 w-4" aria-hidden="true" />
                Keluar dari akun
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>
