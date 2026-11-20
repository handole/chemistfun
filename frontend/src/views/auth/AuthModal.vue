<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { LogIn, UserPlus, AlertTriangle, X } from 'lucide-vue-next'
import { api } from '@/api/client'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'login-success'])

const mode = ref('login') // 'login' | 'register'
const email = ref('')
const password = ref('')
const fullName = ref('')
const role = ref('student')
const teacherInviteCode = ref('')

const loading = ref(false)
const error = ref('')

const handleKeydown = (event) => {
  if (event.key === 'Escape' && props.isOpen) emit('close')
}

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
  if (role.value === 'teacher' && !teacherInviteCode.value.trim()) {
    error.value = 'Kode undangan guru wajib diisi untuk pendaftaran akun guru.'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await api.auth.register({
      email: email.value.trim(),
      password: password.value,
      full_name: fullName.value.trim(),
      role: role.value,
      teacher_invite_code: role.value === 'teacher' ? teacherInviteCode.value.trim() : null
    })
    localStorage.setItem('KimiFun_token', res.access_token)
    localStorage.setItem('KimiFun_user', JSON.stringify(res.user))
    emit('login-success', res.user)
    emit('close')
  } catch (err) {
    error.value = err.message || 'Gagal mendaftarkan akun baru.'
  } finally {
    loading.value = false
  }
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-ink/45 p-4"
    @click.self="emit('close')"
  >
    <div
      class="my-auto w-full max-w-md rounded-xl border border-line bg-surface shadow-sheet"
      role="dialog"
      aria-modal="true"
      aria-labelledby="auth-modal-title"
    >
      <div class="flex items-start justify-between gap-3 border-b border-line px-5 py-3.5">
        <div>
          <h2 id="auth-modal-title" class="text-sm font-semibold text-ink">
            {{ mode === 'login' ? 'Masuk ke akun lain' : 'Buat akun baru' }}
          </h2>
          <p class="mt-0.5 text-[11px] text-ink-muted">Sesi saat ini akan diganti setelah berhasil masuk.</p>
        </div>
        <button
          type="button"
          @click="emit('close')"
          class="-mr-1 grid h-11 w-11 shrink-0 place-items-center rounded-lg text-ink-muted transition-colors hover:bg-sunken hover:text-ink"
          aria-label="Tutup dialog"
        >
          <X class="h-4 w-4" aria-hidden="true" />
        </button>
      </div>

      <div class="px-5 py-4">
        <p
          v-if="error"
          role="alert"
          class="mb-4 flex items-start gap-2 rounded-md border border-danger-200 bg-danger-50 px-3 py-2 text-xs font-medium leading-relaxed text-danger-700"
        >
          <AlertTriangle class="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
          {{ error }}
        </p>

        <form class="space-y-3" @submit.prevent="mode === 'login' ? handleLogin() : handleRegister()">
          <div v-if="mode === 'register'">
            <label for="modal-name" class="mb-1 block text-xs font-semibold text-ink-soft">Nama lengkap</label>
            <input
              id="modal-name"
              v-model="fullName"
              type="text"
              autocomplete="name"
              class="w-full rounded-md border border-line bg-paper px-3 py-2.5 text-sm text-ink outline-none transition-colors focus:border-accent focus:bg-surface"
            />
          </div>

          <div>
            <label for="modal-email" class="mb-1 block text-xs font-semibold text-ink-soft">Email</label>
            <input
              id="modal-email"
              v-model="email"
              type="email"
              autocomplete="email"
              class="w-full rounded-md border border-line bg-paper px-3 py-2.5 text-sm text-ink outline-none transition-colors focus:border-accent focus:bg-surface"
            />
          </div>

          <div>
            <label for="modal-password" class="mb-1 block text-xs font-semibold text-ink-soft">Password</label>
            <input
              id="modal-password"
              v-model="password"
              type="password"
              :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
              class="w-full rounded-md border border-line bg-paper px-3 py-2.5 text-sm text-ink outline-none transition-colors focus:border-accent focus:bg-surface"
            />
          </div>

          <div v-if="mode === 'register'">
            <label for="modal-role" class="mb-1 block text-xs font-semibold text-ink-soft">Daftar sebagai</label>
            <select
              id="modal-role"
              v-model="role"
              class="w-full rounded-md border border-line bg-paper px-3 py-2.5 text-sm text-ink outline-none transition-colors focus:border-accent focus:bg-surface"
            >
              <option value="student">Siswa</option>
              <option value="teacher">Guru</option>
            </select>
          </div>

          <div v-if="mode === 'register' && role === 'teacher'">
            <label for="modal-invite" class="mb-1 block text-xs font-semibold text-ink-soft">Kode undangan guru</label>
            <input
              id="modal-invite"
              v-model="teacherInviteCode"
              type="text"
              class="w-full rounded-md border border-line bg-paper px-3 py-2.5 font-mono text-sm text-ink outline-none transition-colors focus:border-accent focus:bg-surface"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="flex min-h-[44px] w-full items-center justify-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-ink-soft disabled:opacity-60"
          >
            <component :is="mode === 'login' ? LogIn : UserPlus" class="h-4 w-4 text-accent-300" aria-hidden="true" />
            {{ loading ? 'Memproses' : mode === 'login' ? 'Masuk' : 'Buat akun' }}
          </button>
        </form>

        <button
          type="button"
          @click="mode = mode === 'login' ? 'register' : 'login'; error = ''"
          class="mt-3 min-h-[36px] w-full text-xs font-medium text-ink-muted transition-colors hover:text-accent"
        >
          {{ mode === 'login' ? 'Belum punya akun? Daftar' : 'Sudah punya akun? Masuk' }}
        </button>
      </div>
    </div>
  </div>
</template>
