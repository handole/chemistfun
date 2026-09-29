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
import { Sparkles, MessageSquare, X } from 'lucide-vue-next'
import { api } from '@/api/client'

const currentTab = ref('dashboard')
const backendOnline = ref(true)
const showAuthModal = ref(false)
const showChemBot = ref(false)
const selectedMaterialForLab = ref(null)

const user = ref({
  id: 1,
  full_name: 'Guru Kimia',
  email: 'guru@chemistfun.com',
  role: 'teacher'
})

const checkStatusAndUser = async () => {
  try {
    const health = await api.checkHealth()
    backendOnline.value = health?.status === 'healthy'
  } catch (err) {
    backendOnline.value = false
  }

  // Check stored user
  const savedUser = localStorage.getItem('chemistfun_user')
  const savedToken = localStorage.getItem('chemistfun_token')

  if (savedUser && savedToken) {
    try {
      user.value = JSON.parse(savedUser)
      // verify token with backend
      const me = await api.auth.getMe()
      if (me) user.value = me
    } catch (e) {
      console.warn('Session expired or invalid, clearing local session')
    }
  } else {
    // Attempt automatic quick login for default teacher demo so user has instant data
    try {
      const res = await api.auth.login('guru@chemistfun.com', 'Password123!')
      localStorage.setItem('chemistfun_token', res.access_token)
      localStorage.setItem('chemistfun_user', JSON.stringify(res.user))
      user.value = res.user
    } catch (e) {
      // Demo user not created yet or custom setup
    }
  }
}

const handleLoginSuccess = (newUser) => {
  user.value = newUser
  currentTab.value = 'dashboard'
}

const handleLogout = () => {
  localStorage.removeItem('chemistfun_token')
  localStorage.removeItem('chemistfun_user')
  user.value = {
    full_name: 'Tamu (Belum Login)',
    email: '-',
    role: 'teacher'
  }
  showAuthModal.value = true
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
  <div class="min-h-screen bg-[#F6F8FC] flex flex-col">
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

    <!-- Mini ChemBot Widget (Inspired by mockup bottom-right card) -->
    <div class="fixed bottom-6 right-6 z-40">
      <!-- Popup Chat Box if opened -->
      <div 
        v-if="showChemBot" 
        class="mb-3 w-80 sm:w-96 bg-white rounded-3xl shadow-elevated border border-slate-100 overflow-hidden text-xs flex flex-col"
      >
        <!-- Header -->
        <div class="bg-gradient-to-r from-purple-600 to-indigo-600 p-3.5 text-white flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center font-bold">
              C
            </div>
            <div>
              <p class="font-bold text-sm">ChemBot AI Tutor</p>
              <p class="text-[10px] text-purple-200">Online • Siap membantu rumus & konsep kimia</p>
            </div>
          </div>
          <button @click="showChemBot = false" class="text-white/80 hover:text-white">
            <X class="w-4 h-4" />
          </button>
        </div>

        <!-- Chat Stream Messages -->
        <div class="p-4 space-y-3 max-h-64 overflow-y-auto bg-slate-50/50">
          <div class="bg-slate-900 text-white p-3 rounded-2xl rounded-br-none ml-auto max-w-[85%] text-xs font-medium">
            Jelaskan konsep titik ekuivalen pada titrasi asam-basa?
          </div>
          <div class="bg-white border border-slate-200 text-slate-700 p-3 rounded-2xl rounded-bl-none max-w-[85%] text-xs leading-relaxed shadow-2xs">
            Titik ekuivalen adalah kondisi di mana jumlah mol asam tepat bereaksi netral dengan jumlah mol basa sesuai stoikiometri reaksi (mol H⁺ = mol OH⁻).
          </div>
        </div>

        <!-- Input Box -->
        <div class="p-2.5 border-t border-slate-100 bg-white flex items-center gap-2">
          <input 
            type="text" 
            placeholder="Tanyakan konsep reaksi kimia..." 
            class="flex-1 bg-slate-50 px-3 py-2 rounded-xl text-xs outline-none border border-slate-200"
          />
          <button class="p-2 bg-chemist-primary text-white rounded-xl font-bold hover:bg-blue-600">
            <Sparkles class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <!-- Toggle Button -->
      <button 
        @click="showChemBot = !showChemBot"
        class="w-13 h-13 rounded-2xl bg-gradient-to-br from-purple-600 to-indigo-600 text-white shadow-lg shadow-indigo-500/25 flex items-center justify-center hover:scale-105 active:scale-95 transition-all"
        title="Buka ChemBot AI"
      >
        <MessageSquare v-if="!showChemBot" class="w-6 h-6" />
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

