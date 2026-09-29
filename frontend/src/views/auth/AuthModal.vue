<script setup>
import { ref } from 'vue'
import { LogIn, UserPlus, Sparkles, AlertCircle, X } from 'lucide-vue-next'
import { api } from '@/api/client'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'login-success'])

const mode = ref('login') // 'login' | 'register'
const email = ref('guru@chemistfun.com')
const password = ref('Password123!')
const fullName = ref('')
const role = ref('teacher')

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await api.auth.login(email.value.trim(), password.value)
    localStorage.setItem('chemistfun_token', res.access_token)
    localStorage.setItem('chemistfun_user', JSON.stringify(res.user))
    emit('login-success', res.user)
    emit('close')
  } catch (err) {
    error.value = err.message || 'Email atau password salah.'
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!fullName.value.trim() || !email.value.trim() || !password.value) {
    error.value = 'Semua data wajib diisi.'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await api.auth.register({
      email: email.value.trim(),
      password: password.value,
      full_name: fullName.value.trim(),
      role: role.value
    })
    localStorage.setItem('chemistfun_token', res.access_token)
    localStorage.setItem('chemistfun_user', JSON.stringify(res.user))
    emit('login-success', res.user)
    emit('close')
  } catch (err) {
    error.value = err.message || 'Gagal mendaftarkan akun baru.'
  } finally {
    loading.value = false
  }
}

const quickLoginTeacher = async () => {
  email.value = 'guru@chemistfun.com'
  password.value = 'Password123!'
  mode.value = 'login'
  await handleLogin()
}

const quickLoginStudent = async () => {
  email.value = 'budi@chemistfun.com'
  password.value = 'Password123!'
  mode.value = 'login'
  await handleLogin()
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 shadow-elevated space-y-6 relative">
      <!-- Close button -->
      <button 
        @click="emit('close')"
        class="absolute right-5 top-5 p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100"
      >
        <X class="w-5 h-5" />
      </button>

      <!-- Brand Header -->
      <div class="text-center space-y-1">
        <div class="w-12 h-12 rounded-2xl bg-chemist-dark text-white flex items-center justify-center mx-auto shadow-md">
          <Sparkles class="w-6 h-6 text-sky-400" />
        </div>
        <h3 class="text-xl font-extrabold text-slate-900 tracking-tight pt-2">
          {{ mode === 'login' ? 'Masuk ke ChemistFun' : 'Daftar Akun Baru' }}
        </h3>
        <p class="text-xs text-slate-400">Platform Laboratorium Maya & Pembelajaran Kimia Interaktif</p>
      </div>

      <!-- Quick 1-Click Demo Button -->
      <div class="bg-slate-50 border border-slate-200/80 p-3.5 rounded-2xl space-y-2">
        <span class="font-bold text-slate-800 text-xs block">Pilihan Akun Demo (1-Klik)</span>
        <div class="grid grid-cols-2 gap-2">
          <button 
            type="button"
            @click="quickLoginTeacher"
            class="py-2 px-2.5 bg-chemist-dark hover:bg-slate-900 text-white rounded-xl text-xs font-semibold transition-all shadow-2xs flex items-center justify-center gap-1.5"
          >
            <LogIn class="w-3.5 h-3.5 text-blue-400" />
            <span>Guru Demo</span>
          </button>
          <button 
            type="button"
            @click="quickLoginStudent"
            class="py-2 px-2.5 bg-white border border-slate-200 hover:bg-slate-100 text-slate-800 rounded-xl text-xs font-semibold transition-all shadow-2xs flex items-center justify-center gap-1.5"
          >
            <LogIn class="w-3.5 h-3.5 text-emerald-600" />
            <span>Siswa Demo</span>
          </button>
        </div>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 font-medium flex items-center gap-2">
        <AlertCircle class="w-4 h-4 shrink-0" />
        <span>{{ error }}</span>
      </div>

      <!-- Form -->
      <form @submit.prevent="mode === 'login' ? handleLogin() : handleRegister()" class="space-y-3.5 text-xs">
        <div v-if="mode === 'register'">
          <label class="block font-bold text-slate-700 mb-1">Nama Lengkap</label>
          <input 
            v-model="fullName"
            type="text" 
            placeholder="Contoh: Denih Handoko, M.Pd"
            class="w-full bg-slate-50 focus:bg-white text-xs px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none"
          />
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">Alamat Email</label>
          <input 
            v-model="email"
            type="email" 
            placeholder="nama@sekolah.com"
            class="w-full bg-slate-50 focus:bg-white text-xs px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none"
          />
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">Kata Sandi (Password)</label>
          <input 
            v-model="password"
            type="password" 
            placeholder="••••••••"
            class="w-full bg-slate-50 focus:bg-white text-xs px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none"
          />
        </div>

        <div v-if="mode === 'register'">
          <label class="block font-bold text-slate-700 mb-1">Peran Akun (Role)</label>
          <select 
            v-model="role"
            class="w-full bg-slate-50 focus:bg-white text-xs px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none font-semibold"
          >
            <option value="teacher">👨‍🏫 Guru (Teacher)</option>
            <option value="student">👨‍🎓 Siswa (Student)</option>
          </select>
        </div>

        <button 
          type="submit"
          :disabled="loading"
          class="w-full py-2.5 rounded-xl text-xs font-bold bg-chemist-primary hover:bg-blue-600 text-white transition-all shadow-md mt-2 disabled:opacity-50"
        >
          {{ loading ? 'Memproses...' : (mode === 'login' ? 'Masuk Sekarang' : 'Daftar Akun') }}
        </button>
      </form>

      <!-- Toggle Switch mode -->
      <div class="text-center pt-2 border-t border-slate-100">
        <button 
          v-if="mode === 'login'"
          @click="mode = 'register'; error = ''"
          class="text-xs text-slate-500 hover:text-chemist-primary font-medium"
        >
          Belum punya akun? <strong class="text-chemist-primary">Daftar sekarang</strong>
        </button>
        <button 
          v-else
          @click="mode = 'login'; error = ''"
          class="text-xs text-slate-500 hover:text-chemist-primary font-medium"
        >
          Sudah punya akun? <strong class="text-chemist-primary">Masuk di sini</strong>
        </button>
      </div>
    </div>
  </div>
</template>

