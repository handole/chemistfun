<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import TeacherDashboard from '@/views/teacher/TeacherDashboard.vue'
import ClassManagementView from '@/views/teacher/ClassManagementView.vue'
import ContentManagementView from '@/views/teacher/ContentManagementView.vue'
import VirtualLabConfigView from '@/views/teacher/VirtualLabConfigView.vue'
import AssessmentView from '@/views/teacher/AssessmentView.vue'
import JournalManagementView from '@/views/teacher/JournalManagementView.vue'
import StudentDashboard from '@/views/student/StudentDashboard.vue'
import StoichiometryLab from '@/views/virtual-lab/StoichiometryLab.vue'
import SettingsView from '@/views/settings/SettingsView.vue'
import AuthModal from '@/views/auth/AuthModal.vue'
import AuthPage from '@/views/auth/AuthPage.vue'
import { MessageSquare, X, RefreshCw, Send } from 'lucide-vue-next'
import { api } from '@/api/client'
import { renderFormula } from '@/utils/formula'

const currentTab = ref('dashboard')
const backendOnline = ref(true)
const showAuthModal = ref(false)
const showKimi = ref(false)
const mobileMenuOpen = ref(false)
const selectedMaterialForLab = ref(null)

// Kimi Chat State
const kimiQuestion = ref('')
const kimiLoading = ref(false)
const kimiMessages = ref([
  {
    role: 'bot',
    text: 'Halo! Saya Kimi, asisten kimia kamu. Ada rumus, reaksi, atau konsep yang ingin kamu tanyakan hari ini?'
  }
])

const handleSendKimi = async () => {
  const q = kimiQuestion.value.trim()
  if (!q || kimiLoading.value) return

  kimiMessages.value.push({ role: 'user', text: q })
  kimiQuestion.value = ''
  kimiLoading.value = true

  try {
    const res = await api.content.chatChemBot(q)
    kimiMessages.value.push({
      role: 'bot',
      text: res.answer || 'Mohon maaf, Kimi belum dapat menjawab pertanyaan ini.'
    })
  } catch (err) {
    if (err.message && err.message.toLowerCase().includes('token')) {
      handleLogout()
      kimiMessages.value.push({
        role: 'bot',
        text: 'Sesi login telah berakhir atau tidak valid. Silakan login kembali.'
      })
    } else {
      kimiMessages.value.push({
        role: 'bot',
        text: 'Gagal terhubung ke Kimi: ' + err.message
      })
    }
  } finally {
    kimiLoading.value = false
  }
}

const user = ref(null)
const authChecked = ref(false)

const checkStatusAndUser = async () => {
  try {
    const health = await api.checkHealth()
    backendOnline.value = health?.status === 'healthy'
  } catch (err) {
    backendOnline.value = false
  }

  const savedUser = localStorage.getItem('KimiFun_user')
  const savedToken = localStorage.getItem('KimiFun_token')

  if (savedUser && savedToken) {
    try {
      user.value = JSON.parse(savedUser)
      const me = await api.auth.getMe()
      if (me) user.value = me
      else {
        user.value = null
        localStorage.removeItem('KimiFun_token')
        localStorage.removeItem('KimiFun_user')
      }
    } catch (e) {
      console.warn('Session expired or invalid, clearing local session')
      user.value = null
      localStorage.removeItem('KimiFun_token')
      localStorage.removeItem('KimiFun_user')
    }
  } else {
    user.value = null
  }
  authChecked.value = true
}

const handleLoginSuccess = (newUser) => {
  user.value = newUser
  currentTab.value = 'dashboard'
}

const handleLogout = () => {
  localStorage.removeItem('KimiFun_token')
  localStorage.removeItem('KimiFun_user')
  user.value = null
}

const openLabWithMaterial = (mat) => {
  selectedMaterialForLab.value = mat
  currentTab.value = 'labs'
}

const goToTab = (tab) => {
  currentTab.value = tab
  mobileMenuOpen.value = false
}

const handleDrawerKeydown = (event) => {
  if (event.key === 'Escape') mobileMenuOpen.value = false
}

onMounted(() => {
  checkStatusAndUser()
  window.addEventListener('keydown', handleDrawerKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleDrawerKeydown)
})
</script>

<template>
  <!-- Session check -->
  <div v-if="!authChecked" class="flex min-h-screen items-center justify-center bg-paper">
    <p class="flex items-center gap-2 text-xs font-medium text-ink-muted">
      <RefreshCw class="h-4 w-4 animate-spin text-accent" aria-hidden="true" />
      Memuat sesi KimiFun
    </p>
  </div>

  <!-- Signed out -->
  <AuthPage v-else-if="!user" @login-success="handleLoginSuccess" />

  <!-- Workspace -->
  <div v-else class="flex min-h-screen flex-col bg-paper">
    <AppHeader
      :user="user"
      :backend-online="backendOnline"
      :mobile-menu-open="mobileMenuOpen"
      @toggle-sidebar="mobileMenuOpen = !mobileMenuOpen"
      @logout="handleLogout"
      @open-auth="showAuthModal = true"
      @refresh="checkStatusAndUser"
    />

    <!-- Mobile navigation sheet -->
    <div v-if="mobileMenuOpen" class="fixed inset-0 z-50 md:hidden">
      <div @click="mobileMenuOpen = false" class="absolute inset-0 bg-ink/40"></div>

      <div class="absolute inset-y-0 left-0 flex w-72 max-w-[85vw] flex-col bg-surface shadow-sheet">
        <div class="flex h-16 items-center justify-between border-b border-line px-3">
          <div class="flex items-center gap-2.5">
            <span class="grid h-9 w-9 place-items-center rounded-lg bg-ink">
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
            <p class="text-sm font-semibold tracking-tight text-ink">KimiFun</p>
          </div>
          <button
            type="button"
            @click="mobileMenuOpen = false"
            class="grid h-11 w-11 place-items-center rounded-lg text-ink-muted transition-colors hover:bg-sunken hover:text-ink"
            aria-label="Tutup menu navigasi"
          >
            <X class="h-5 w-5" aria-hidden="true" />
          </button>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto">
          <AppSidebar
            :current-tab="currentTab"
            :role="user?.role"
            :is-mobile="true"
            @update:current-tab="goToTab"
            @logout="handleLogout"
          />
        </div>
      </div>
    </div>

    <!-- Workspace body -->
    <div class="mx-auto flex w-full max-w-[1600px] flex-1">
      <AppSidebar
        :current-tab="currentTab"
        :role="user?.role"
        @update:current-tab="currentTab = $event"
        @logout="handleLogout"
      />

      <main class="min-w-0 flex-1 px-4 py-5 sm:px-6 sm:py-6 lg:px-8">
        <!-- STUDENT VIEWS -->
        <template v-if="user?.role === 'student'">
          <StudentDashboard
            v-if="currentTab === 'dashboard'"
            :user="user"
            @navigate="(tab) => (currentTab = tab)"
          />

          <div v-else-if="currentTab === 'labs'" class="space-y-4">
            <div class="rounded-xl border border-line bg-surface px-4 py-3">
              <h2 class="text-sm font-semibold text-ink">Praktikum mandiri</h2>
              <p class="text-xs text-ink-muted">Latihan stoikiometri dengan perhitungan yang bisa kamu ulang tanpa risiko bahan kimia.</p>
            </div>
            <StoichiometryLab :user="user" />
          </div>

          <SettingsView
            v-else-if="currentTab === 'settings'"
            :user="user"
            :backend-online="backendOnline"
            @logout="handleLogout"
            @refresh="checkStatusAndUser"
          />
        </template>

        <!-- TEACHER / ADMIN VIEWS -->
        <template v-else>
          <TeacherDashboard
            v-if="currentTab === 'dashboard'"
            :user="user"
            @navigate="(tab) => (currentTab = tab)"
          />

          <ClassManagementView v-else-if="currentTab === 'classes'" :user="user" />

          <ContentManagementView
            v-else-if="currentTab === 'content'"
            :user="user"
            @open-lab="openLabWithMaterial"
          />

          <JournalManagementView v-else-if="currentTab === 'journals'" :user="user" />

          <VirtualLabConfigView
            v-else-if="currentTab === 'labs'"
            :user="user"
            :initial-material="selectedMaterialForLab"
          />

          <AssessmentView
            v-else-if="currentTab === 'assessment' || currentTab === 'analytics'"
            :user="user"
          />

          <SettingsView
            v-else-if="currentTab === 'settings'"
            :user="user"
            :backend-online="backendOnline"
            @logout="handleLogout"
            @refresh="checkStatusAndUser"
          />
        </template>
      </main>
    </div>

    <!-- Kimi assistant -->
    <div class="fixed bottom-4 right-4 z-40 sm:bottom-6 sm:right-6">
      <div
        v-if="showKimi"
        class="mb-3 flex w-[min(20rem,calc(100vw-2rem))] flex-col overflow-hidden rounded-xl border border-line bg-surface shadow-sheet sm:w-96"
      >
        <div class="flex items-center justify-between border-b border-line bg-ink px-3.5 py-3 text-white">
          <div class="flex items-center gap-2.5">
            <span class="grid h-7 w-7 place-items-center rounded-md bg-accent text-[11px] font-semibold text-white">
              K
            </span>
            <div class="leading-tight">
              <p class="text-xs font-semibold">Kimi, asisten kimia</p>
              <p class="text-[11px] text-white/70">Tanya rumus, reaksi, atau konsep</p>
            </div>
          </div>
          <button
            type="button"
            @click="showKimi = false"
            class="grid h-11 w-11 place-items-center rounded-lg text-white/70 transition-colors hover:bg-white/10 hover:text-white"
            aria-label="Tutup panel Kimi"
          >
            <X class="h-4 w-4" aria-hidden="true" />
          </button>
        </div>

        <div class="max-h-64 space-y-2.5 overflow-y-auto bg-paper px-3.5 py-3">
          <div
            v-for="(msg, idx) in kimiMessages"
            :key="idx"
            :class="
              msg.role === 'user'
                ? 'ml-auto max-w-[85%] rounded-lg rounded-br-sm bg-ink px-3 py-2 text-xs font-medium text-white'
                : 'max-w-[85%] rounded-lg rounded-bl-sm border border-line bg-surface px-3 py-2 text-xs leading-relaxed text-ink-soft'
            "
            v-html="renderFormula(msg.text)"
          ></div>
          <p
            v-if="kimiLoading"
            class="flex max-w-[85%] items-center gap-2 rounded-lg rounded-bl-sm border border-line bg-surface px-3 py-2 text-xs text-ink-muted"
          >
            <RefreshCw class="h-3.5 w-3.5 animate-spin text-accent" aria-hidden="true" />
            Kimi sedang menyusun jawaban
          </p>
        </div>

        <div class="flex items-center gap-2 border-t border-line bg-surface px-2.5 py-2.5">
          <label for="kimi-question" class="sr-only">Pertanyaan untuk Kimi</label>
          <input
            id="kimi-question"
            v-model="kimiQuestion"
            type="text"
            placeholder="Tulis pertanyaan kimia"
            @keyup.enter="handleSendKimi"
            class="min-w-0 flex-1 rounded-md border border-line bg-paper px-3 py-2 text-xs text-ink outline-none placeholder:text-ink-faint focus:border-accent"
          />
          <button
            type="button"
            @click="handleSendKimi"
            :disabled="kimiLoading || !kimiQuestion.trim()"
            class="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-accent text-white transition-colors hover:bg-accent-700 disabled:opacity-50"
            aria-label="Kirim pertanyaan"
          >
            <Send class="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </div>

      <button
        type="button"
        @click="showKimi = !showKimi"
        class="grid h-12 w-12 place-items-center rounded-lg bg-accent text-white shadow-card transition-colors hover:bg-accent-700"
        :aria-label="showKimi ? 'Tutup panel Kimi' : 'Buka panel Kimi'"
        :aria-expanded="showKimi"
      >
        <component :is="showKimi ? X : MessageSquare" class="h-5 w-5" aria-hidden="true" />
      </button>
    </div>

    <AuthModal
      :is-open="showAuthModal"
      @close="showAuthModal = false"
      @login-success="handleLoginSuccess"
    />
  </div>
</template>
