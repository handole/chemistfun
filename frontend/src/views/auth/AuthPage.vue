<script setup>
import { ref } from 'vue'
import { Sparkles, AlertCircle, LogIn, UserPlus } from 'lucide-vue-next'
import { api } from '@/api/client'

const emit = defineEmits(['login-success'])

const mode = ref('login') // 'login' | 'register'
const email = ref('')
const password = ref('')
const fullName = ref('')
const role = ref('teacher')

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!email.value.trim() || !password.value) {
    error.value = 'Email dan password wajib diisi.'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await api.auth.login(email.value.trim(), password.value)
    localStorage.setItem('KimiFun_token', res.access_token)
    localStorage.setItem('KimiFun_user', JSON.stringify(res.user))
    emit('login-success', res.user)
  } catch (err) {
    error.value = err.message || 'Email atau password salah.'
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!fullName.value.trim() || !email.value.trim() || !password.value) {
    error.value = 'Semua data formulir wajib diisi.'
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
    localStorage.setItem('KimiFun_token', res.access_token)
    localStorage.setItem('KimiFun_user', JSON.stringify(res.user))
    emit('login-success', res.user)
  } catch (err) {
    error.value = err.message || 'Gagal mendaftarkan akun baru.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#F6F8FC] flex flex-col justify-center items-center p-4">
    <div class="bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 shadow-elevated border border-slate-100 space-y-6">
      <!-- Brand Header -->
      <div class="text-center space-y-1">
        <div class="w-12 h-12 rounded-2xl bg-chemist-dark text-white flex items-center justify-center mx-auto shadow-md">
          <Sparkles class="w-6 h-6 text-sky-400" />
        </div>
        <h2 class="text-xl font-extrabold text-slate-900 tracking-tight pt-2">
          {{ mode === 'login' ? 'Masuk ke KimiFun' : 'Daftar Akun KimiFun' }}
        </h2>
        <p class="text-xs text-slate-400">Platform Laboratorium Maya & Pembelajaran Kimia</p>
      </div>

      <!-- Mode Switcher Tabs -->
      <div class="flex p-1 bg-slate-100 rounded-xl text-xs font-semibold">
        <button 
          type="button"
          @click="mode = 'login'; error = ''"
          :class="mode === 'login' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-500 hover:text-slate-800'"
          class="flex-1 py-2 rounded-lg transition-all"
        >
          Masuk
        </button>
        <button 
          type="button"
          @click="mode = 'register'; error = ''"
          :class="mode === 'register' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-500 hover:text-slate-800'"
          class="flex-1 py-2 rounded-lg transition-all"
        >
          Daftar Akun
        </button>
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
            placeholder="Nama lengkap"
            class="w-full bg-slate-50 focus:bg-white text-xs px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none"
          />
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">Email</label>
          <input 
            v-model="email"
            type="email" 
            placeholder="alamat@email.com"
            class="w-full bg-slate-50 focus:bg-white text-xs px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none"
          />
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">Password</label>
          <input 
            v-model="password"
            type="password" 
            placeholder="••••••••"
            class="w-full bg-slate-50 focus:bg-white text-xs px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none"
          />
        </div>

        <div v-if="mode === 'register'">
          <label class="block font-bold text-slate-700 mb-1">Daftar Sebagai</label>
          <select 
            v-model="role"
            class="w-full bg-slate-50 focus:bg-white text-xs px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none"
          >
            <option value="teacher">Guru</option>
            <option value="student">Siswa</option>
          </select>
        </div>

        <button 
          type="submit"
          :disabled="loading"
          class="w-full py-3 bg-chemist-dark hover:bg-slate-900 text-white rounded-xl text-xs font-bold transition-all shadow-md active:scale-98 disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
        >
          <LogIn v-if="mode === 'login'" class="w-4 h-4 text-sky-400" />
          <UserPlus v-else class="w-4 h-4 text-emerald-400" />
          <span>{{ loading ? 'Memproses...' : (mode === 'login' ? 'Masuk ke Akun' : 'Daftar Sekarang') }}</span>
        </button>
      </form>
    </div>
  </div>
</template>
