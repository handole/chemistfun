<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import TeacherDashboard from '@/views/teacher/TeacherDashboard.vue'
import ClassManagementView from '@/views/teacher/ClassManagementView.vue'
import ContentManagementView from '@/views/teacher/ContentManagementView.vue'
import VirtualLabConfigView from '@/views/teacher/VirtualLabConfigView.vue'
import AssessmentView from '@/views/teacher/AssessmentView.vue'
import StudentDashboard from '@/views/student/StudentDashboard.vue'
import StoichiometryLab from '@/views/virtual-lab/StoichiometryLab.vue'
import SettingsView from '@/views/settings/SettingsView.vue'
import AuthModal from '@/views/auth/AuthModal.vue'
import AuthPage from '@/views/auth/AuthPage.vue'
import { Sparkles, MessageSquare, X, RefreshCw, Send } from 'lucide-vue-next'
import { api } from '@/api/client'

const currentTab = ref('dashboard')
const backendOnline = ref(true)
const showAuthModal = ref(false)
const showKimi = ref(false)
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
    kimiMessages.value.push({
      role: 'bot',
      text: 'Gagal terhubung ke Kimi: ' + err.message
    })
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

  // Check stored user
  const savedUser = localStorage.getItem('KimiFun_user')
  const savedToken = localStorage.getItem('KimiFun_token')

  if (savedUser && savedToken) {
    try {
      user.value = JSON.parse(savedUser)
      // verify token with backend
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

onMounted(() => {
  checkStatusAndUser()
})
</script>

<template>
  <!-- Loading initial session check -->
  <div v-if="!authChecked" class="min-h-screen bg-[#F6F8FC] flex items-center justify-center">
    <div class="flex items-center gap-2 text-xs font-semibold text-slate-500">
      <RefreshCw class="w-4 h-4 animate-spin text-chemist-primary" />
      <span>Memuat sesi KimiFun...</span>
    </div>
  </div>

  <!-- AUTH VIEW (Jika belum login) -->
  <AuthPage 
    v-else-if="!user" 
    @login-success="handleLoginSuccess" 
  />

  <!-- MAIN APP VIEW (Jika sudah login) -->
  <div v-else class="min-h-screen bg-[#F6F8FC] flex flex-col">
    <!-- Topbar Navigation -->
    <AppHeader 
      :user="user"
      :backend-online="backendOnline"
      @logout="handleLogout"
      @open-auth="showAuthModal = true"
      @refresh="checkStatusAndUser"
    />

    <!-- Main Workspace Body (Sidebar + Content) -->
    <div class="flex-1 flex max-w-[1600px] w-full mx-auto">
      <!-- Sidebar -->
      <AppSidebar 
        :current-tab="currentTab"
        :role="user?.role"
        @update:current-tab="(tab) => currentTab = tab"
        class="hidden md:flex"
      />

      <!-- Content Area -->
      <main class="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto max-w-full">
        <!-- STUDENT VIEWS -->
        <template v-if="user?.role === 'student'">
          <StudentDashboard 
            v-if="currentTab === 'dashboard'" 
            :user="user"
            @navigate="(tab) => currentTab = tab"
          />

          <div v-else-if="currentTab === 'labs'" class="space-y-4">
            <div class="bg-white rounded-2xl border border-slate-200/80 p-4 shadow-sm flex items-center justify-between">
              <div>
                <h3 class="text-sm font-bold text-slate-900">Laboratorium Virtual Siswa</h3>
                <p class="text-xs text-slate-500">Praktikum mandiri stoikiometri dan kimia analitis.</p>
              </div>
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
            @navigate="(tab) => currentTab = tab"
          />

          <ClassManagementView 
            v-else-if="currentTab === 'classes'" 
            :user="user"
          />

          <ContentManagementView 
            v-else-if="currentTab === 'content'" 
            :user="user"
            @open-lab="openLabWithMaterial"
          />

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

    <!-- Mini Kimi Widget (AI Tutor Bot) -->
    <div class="fixed bottom-6 right-6 z-40">
      <!-- Popup Chat Box if opened -->
      <div 
        v-if="showKimi" 
        class="mb-3 w-80 sm:w-96 bg-white rounded-3xl shadow-elevated border border-slate-100 overflow-hidden text-xs flex flex-col"
      >
        <!-- Header -->
        <div class="bg-gradient-to-r from-purple-600 to-indigo-600 p-3.5 text-white flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center font-bold">
              K
            </div>
            <div>
              <p class="font-bold text-sm">Kimi AI Tutor</p>
              <p class="text-[10px] text-purple-200">Online • Teman belajar konsep & rumus kimia</p>
            </div>
          </div>
          <button @click="showKimi = false" class="text-white/80 hover:text-white">
            <X class="w-4 h-4" />
          </button>
        </div>

        <!-- Chat Stream Messages -->
        <div class="p-4 space-y-3 max-h-64 overflow-y-auto bg-slate-50/50">
          <div 
            v-for="(msg, idx) in kimiMessages" 
            :key="idx"
            :class="msg.role === 'user' 
              ? 'bg-slate-900 text-white p-3 rounded-2xl rounded-br-none ml-auto max-w-[85%] text-xs font-medium'
              : 'bg-white border border-slate-200 text-slate-700 p-3 rounded-2xl rounded-bl-none max-w-[85%] text-xs leading-relaxed shadow-2xs whitespace-pre-line'"
          >
            {{ msg.text }}
          </div>
          <div v-if="kimiLoading" class="bg-white border border-slate-200 text-slate-400 p-2.5 rounded-2xl rounded-bl-none max-w-[85%] text-xs flex items-center gap-2">
            <RefreshCw class="w-3.5 h-3.5 animate-spin text-purple-600" />
            <span>Kimi sedang berpikir...</span>
          </div>
        </div>

        <!-- Input Box -->
        <div class="p-2.5 border-t border-slate-100 bg-white flex items-center gap-2">
          <input 
            v-model="kimiQuestion"
            type="text" 
            placeholder="Tanyakan rumus / reaksi kimia ke Kimi..." 
            @keyup.enter="handleSendKimi"
            class="flex-1 bg-slate-50 px-3 py-2 rounded-xl text-xs outline-none border border-slate-200"
          />
          <button 
            @click="handleSendKimi"
            :disabled="kimiLoading || !kimiQuestion.trim()"
            class="p-2 bg-chemist-primary text-white rounded-xl font-bold hover:bg-blue-600 disabled:opacity-50 flex items-center justify-center transition-all"
          >
            <Send class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <!-- Toggle Button -->
      <button 
        @click="showKimi = !showKimi"
        class="w-13 h-13 rounded-2xl bg-gradient-to-br from-purple-600 to-indigo-600 text-white shadow-lg shadow-indigo-500/25 flex items-center justify-center hover:scale-105 active:scale-95 transition-all"
        title="Tanya Kimi AI"
      >
        <MessageSquare v-if="!showKimi" class="w-6 h-6" />
        <X v-else class="w-6 h-6" />
      </button>
    </div>

    <!-- Authentication Modal -->
    <AuthModal 
      :is-open="showAuthModal"
      @close="showAuthModal = false"
      @login-success="handleLoginSuccess"
    />
  </div>
</template>

