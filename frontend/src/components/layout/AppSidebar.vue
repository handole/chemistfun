<script setup>
import { 
  LayoutGrid, 
  Users, 
  BookOpen, 
  FlaskConical, 
  CheckSquare, 
  BarChart3, 
  Settings,
  Sparkles,
  ExternalLink
} from 'lucide-vue-next'

const props = defineProps({
  currentTab: {
    type: String,
    default: 'dashboard'
  },
  role: {
    type: String,
    default: 'teacher'
  }
})

const emit = defineEmits(['update:currentTab'])

const teacherMenus = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutGrid },
  { id: 'classes', label: 'Kelas Saya', icon: Users },
  { id: 'content', label: 'Modul Belajar', icon: BookOpen },
  { id: 'labs', label: 'Lab Virtual', icon: FlaskConical },
  { id: 'assessment', label: 'Kuis & Asesmen', icon: CheckSquare },
  { id: 'analytics', label: 'Analisis Siswa', icon: BarChart3 },
]

const studentMenus = [
  { id: 'dashboard', label: 'Portal Belajar', icon: LayoutGrid },
  { id: 'labs', label: 'Praktikum Virtual', icon: FlaskConical },
]

const setTab = (id) => {
  emit('update:currentTab', id)
}
</script>

<template>
  <aside class="w-64 bg-white border-r border-slate-100 flex flex-col justify-between p-4 shrink-0 min-h-[calc(100vh-5rem)]">
    <!-- Top Nav Section -->
    <div class="space-y-6">
      <!-- Section: MENU UTAMA -->
      <div>
        <p class="text-[11px] font-bold tracking-wider text-slate-400 uppercase px-3 mb-3">
          {{ role === 'student' ? 'MENU SISWA' : 'MENU GURU' }}
        </p>
        <nav class="space-y-1">
          <button
            v-for="item in (role === 'student' ? studentMenus : teacherMenus)"
            :key="item.id"
            @click="setTab(item.id)"
            class="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150"
            :class="currentTab === item.id 
              ? 'bg-chemist-dark text-white shadow-md shadow-slate-900/10' 
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'"
          >
            <div class="flex items-center gap-3">
              <component :is="item.icon" class="w-4 h-4" :class="currentTab === item.id ? 'text-white' : 'text-slate-400'" />
              <span>{{ item.label }}</span>
            </div>

            <!-- Badges if any -->
            <span 
              v-if="item.id === 'labs'" 
              class="text-[10px] font-bold px-1.5 py-0.5 rounded-full"
              :class="currentTab === item.id ? 'bg-sky-500/30 text-sky-200' : 'bg-sky-50 text-sky-600'"
            >
              Lab
            </span>
          </button>
        </nav>
      </div>

      <!-- Section: AKUN & SISTEM -->
      <div>
        <p class="text-[11px] font-bold tracking-wider text-slate-400 uppercase px-3 mb-3">AKUN & SISTEM</p>
        <nav class="space-y-1">
          <button
            @click="setTab('settings')"
            class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all"
            :class="currentTab === 'settings' 
              ? 'bg-chemist-dark text-white shadow-md shadow-slate-900/10' 
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'"
          >
            <Settings class="w-4 h-4" :class="currentTab === 'settings' ? 'text-white' : 'text-slate-400'" />
            <span>Pengaturan</span>
          </button>
        </nav>
      </div>
    </div>

    <!-- Bottom: Premium / Info Card (From mockup) -->
    <div class="mt-6">
      <div class="bg-gradient-to-br from-chemist-dark via-slate-900 to-indigo-950 text-white p-4 rounded-2xl shadow-md relative overflow-hidden">
        <!-- Background decorative bubble -->
        <div class="absolute -right-4 -bottom-4 w-20 h-20 bg-indigo-500/20 rounded-full blur-xl pointer-events-none"></div>

        <div class="flex items-center gap-2 mb-2">
          <div class="w-6 h-6 rounded-lg bg-indigo-500/30 flex items-center justify-center">
            <Sparkles class="w-3.5 h-3.5 text-indigo-300" />
          </div>
          <span class="text-xs font-bold text-indigo-200 uppercase tracking-wider">CHEMISTFUN LAB</span>
        </div>

        <p class="text-xs text-slate-300 font-medium leading-relaxed">
          Simulasi eksperimen reaksi kimia dan asesmen radar siap digunakan.
        </p>

        <a 
          href="/docs" 
          target="_blank"
          class="mt-3 inline-flex items-center gap-1.5 text-[11px] font-semibold text-sky-400 hover:text-sky-300 transition-colors"
        >
          <span>Buka OpenAPI Swagger</span>
          <ExternalLink class="w-3 h-3" />
        </a>
      </div>
    </div>
  </aside>
</template>

