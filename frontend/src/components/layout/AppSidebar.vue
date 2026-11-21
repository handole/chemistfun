<script setup>
import { computed } from 'vue'
import {
  LayoutGrid,
  Users,
  BookOpen,
  FlaskConical,
  ClipboardCheck,
  CheckSquare,
  Settings,
  LogOut,
} from 'lucide-vue-next'

const props = defineProps({
  currentTab: {
    type: String,
    default: 'dashboard'
  },
  role: {
    type: String,
    default: 'teacher'
  },
  isMobile: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:currentTab', 'logout'])

// Grouped by the job the teacher or student is doing, not by screen name.
const teacherGroups = [
  {
    label: 'Mengajar',
    items: [
      { id: 'dashboard', label: 'Dashboard', icon: LayoutGrid },
      { id: 'classes', label: 'Kelas', icon: Users },
      { id: 'content', label: 'Modul belajar', icon: BookOpen },
      { id: 'journals', label: 'Jurnal mengajar', icon: ClipboardCheck },
    ],
  },
  {
    label: 'Laboratorium',
    items: [
      { id: 'labs', label: 'Lab virtual', icon: FlaskConical },
      { id: 'assessment', label: 'Kuis & asesmen', icon: CheckSquare },
    ],
  },
]

const studentGroups = [
  {
    label: 'Belajar',
    items: [
      { id: 'dashboard', label: 'Dashboard', icon: LayoutGrid },
      { id: 'labs', label: 'Praktikum mandiri', icon: FlaskConical },
    ],
  },
]

const groups = computed(() => (props.role === 'student' ? studentGroups : teacherGroups))
</script>

<template>
  <aside
    :class="[
      'flex flex-col justify-between bg-surface',
      isMobile ? 'h-full w-full' : 'sticky top-16 hidden h-[calc(100vh-4rem)] w-60 shrink-0 border-r border-line md:flex',
    ]"
  >
    <nav class="flex-1 overflow-y-auto px-3 py-4" aria-label="Navigasi utama">
      <div v-for="group in groups" :key="group.label" class="mb-5 last:mb-0">
        <p class="kf-group-label px-2 pb-1.5">{{ group.label }}</p>
        <ul class="space-y-0.5">
          <li v-for="item in group.items" :key="item.id">
            <button
              type="button"
              @click="emit('update:currentTab', item.id)"
              :aria-current="currentTab === item.id ? 'page' : undefined"
              class="relative flex min-h-[44px] w-full items-center gap-2.5 rounded-md py-2 pl-3 pr-2.5 text-left text-[13px] transition-colors"
              :class="
                currentTab === item.id
                  ? 'bg-sunken font-semibold text-ink'
                  : 'font-medium text-ink-muted hover:bg-sunken hover:text-ink'
              "
            >
              <span
                v-if="currentTab === item.id"
                class="absolute left-0 top-0 bottom-0 w-[3px] rounded-r-full bg-accent"
                aria-hidden="true"
              ></span>
              <component
                :is="item.icon"
                class="h-4 w-4 shrink-0"
                :class="currentTab === item.id ? 'text-accent' : 'text-ink-faint'"
                aria-hidden="true"
              />
              <span class="truncate">{{ item.label }}</span>
            </button>
          </li>
        </ul>
      </div>
    </nav>

    <div class="border-t border-line px-3 py-3">
      <button
        type="button"
        @click="emit('update:currentTab', 'settings')"
        :aria-current="currentTab === 'settings' ? 'page' : undefined"
        class="relative flex min-h-[44px] w-full items-center gap-2.5 rounded-md py-2 pl-3 pr-2.5 text-left text-[13px] transition-colors"
        :class="
          currentTab === 'settings'
            ? 'bg-sunken font-semibold text-ink'
            : 'font-medium text-ink-muted hover:bg-sunken hover:text-ink'
        "
      >
        <span
          v-if="currentTab === 'settings'"
          class="absolute left-0 top-0 bottom-0 w-[3px] rounded-r-full bg-accent"
          aria-hidden="true"
        ></span>
        <Settings
          class="h-4 w-4 shrink-0"
          :class="currentTab === 'settings' ? 'text-accent' : 'text-ink-faint'"
          aria-hidden="true"
        />
        Pengaturan
      </button>

      <button
        type="button"
        @click="emit('logout')"
        class="flex min-h-[44px] w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-left text-[13px] font-medium text-ink-muted transition-colors hover:bg-danger-50 hover:text-danger-700"
      >
        <LogOut class="h-4 w-4 shrink-0 text-ink-faint" aria-hidden="true" />
        Keluar
      </button>
    </div>
  </aside>
</template>
