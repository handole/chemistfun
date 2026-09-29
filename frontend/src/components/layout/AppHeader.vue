<script setup>
import { ref } from 'vue'
import { Search, Bell, Flame, CheckCircle2, AlertCircle, LogOut, User, RefreshCw } from 'lucide-vue-next'

const props = defineProps({
  user: {
    type: Object,
    default: () => ({ full_name: 'Guru Kimia', email: 'guru@chemistfun.com', role: 'teacher' })
  },
  backendOnline: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['logout', 'open-auth', 'refresh'])

const showUserMenu = ref(false)

const getInitials = (name) => {
  if (!name) return 'GK'
  return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
}
</script>

<template>
  <header class="h-20 bg-white border-b border-slate-100 px-6 flex items-center justify-between sticky top-0 z-30 shadow-[0_2px_10px_-4px_rgba(0,0,0,0.02)]">
    <!-- Left: Logo and Brand (Desktop & Mobile) -->
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-chemist-dark flex items-center justify-center text-white shadow-md shadow-slate-900/10">
        <!-- Beaker Icon SVG -->
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-sky-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4.5 3h15"/>
          <path d="M6 3v16a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V3"/>
          <path d="M6 14h12"/>
        </svg>
      </div>
      <div>
        <h1 class="text-lg font-bold tracking-tight text-slate-900 leading-none">ChemistFun</h1>
        <p class="text-[10px] font-semibold text-slate-400 tracking-wider uppercase mt-1">LABS • AI POWERED</p>
      </div>
    </div>

    <!-- Center: Global Search Bar (From mockup) -->
    <div class="hidden md:flex items-center flex-1 max-w-md mx-8">
      <div class="relative w-full">
        <Search class="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input 
          type="text" 
          placeholder="Cari kelas, modul, materi, atau siswa..." 
          class="w-full bg-slate-50 hover:bg-slate-100/80 focus:bg-white text-sm pl-10 pr-12 py-2.5 rounded-xl border border-slate-200/80 focus:border-chemist-primary focus:ring-2 focus:ring-chemist-primary/20 outline-none transition-all placeholder:text-slate-400"
        />
        <div class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-0.5 text-[11px] font-medium text-slate-400 bg-white border border-slate-200 px-1.5 py-0.5 rounded-md shadow-2xs">
          <span>⌘</span><span>K</span>
        </div>
      </div>
    </div>

    <!-- Right: Status, Streak, Notifications & Profile -->
    <div class="flex items-center gap-3">
      <!-- Backend Status Badge -->
      <div 
        @click="emit('refresh')"
        title="Klik untuk refresh status backend"
        class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium cursor-pointer border transition-colors"
        :class="backendOnline ? 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100' : 'bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100'"
      >
        <span class="w-2 h-2 rounded-full" :class="backendOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'"></span>
        <span>{{ backendOnline ? 'API Connected' : 'API Offline' }}</span>
      </div>

      <!-- Streak Badge (Mockup) -->
      <div class="hidden lg:flex items-center gap-1.5 bg-amber-50 text-amber-800 border border-amber-200/70 px-3.5 py-1.5 rounded-full text-xs font-semibold shadow-2xs">
        <Flame class="w-4 h-4 text-amber-500 fill-amber-500" />
        <span>12 hari aktif</span>
      </div>

      <!-- Notification Bell -->
      <button class="relative p-2 rounded-xl text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors">
        <Bell class="w-5 h-5" />
        <span class="absolute top-2 right-2 w-2 h-2 bg-chemist-accent rounded-full ring-2 ring-white"></span>
      </button>

      <!-- Profile Avatar & Dropdown -->
      <div class="relative">
        <button 
          @click="showUserMenu = !showUserMenu"
          class="flex items-center gap-3 pl-2 pr-3 py-1.5 rounded-xl hover:bg-slate-50 transition-colors text-left border border-transparent hover:border-slate-200"
        >
          <div class="w-9 h-9 rounded-full bg-chemist-dark text-white font-bold text-xs flex items-center justify-center ring-2 ring-slate-100 shadow-sm">
            {{ getInitials(user?.full_name) }}
          </div>
          <div class="hidden sm:block leading-tight">
            <p class="text-xs font-bold text-slate-800 truncate max-w-[120px]">{{ user?.full_name || 'Guru Kimia' }}</p>
            <span class="inline-block text-[10px] font-semibold text-chemist-primary bg-blue-50 px-1.5 py-0.5 rounded capitalize">
              {{ user?.role === 'teacher' ? '👨‍🏫 Guru' : '👨‍🎓 Siswa' }}
            </span>
          </div>
        </button>

        <!-- Dropdown Menu -->
        <div 
          v-if="showUserMenu" 
          class="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-elevated border border-slate-100 py-2 z-50 text-sm"
        >
          <div class="px-4 py-2 border-b border-slate-100">
            <p class="font-bold text-slate-800">{{ user?.full_name }}</p>
            <p class="text-xs text-slate-400 truncate">{{ user?.email }}</p>
          </div>

          <div class="py-1">
            <button 
              @click="emit('open-auth'); showUserMenu = false"
              class="w-full text-left px-4 py-2 hover:bg-slate-50 text-slate-700 flex items-center gap-2.5"
            >
              <User class="w-4 h-4 text-slate-400" />
              <span>Ganti Akun / Login</span>
            </button>
            <button 
              @click="emit('refresh'); showUserMenu = false"
              class="w-full text-left px-4 py-2 hover:bg-slate-50 text-slate-700 flex items-center gap-2.5"
            >
              <RefreshCw class="w-4 h-4 text-slate-400" />
              <span>Sinkronkan Data API</span>
            </button>
          </div>

          <div class="border-t border-slate-100 pt-1">
            <button 
              @click="emit('logout'); showUserMenu = false"
              class="w-full text-left px-4 py-2 hover:bg-rose-50 text-rose-600 flex items-center gap-2.5 font-medium"
            >
              <LogOut class="w-4 h-4 text-rose-500" />
              <span>Keluar (Logout)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

