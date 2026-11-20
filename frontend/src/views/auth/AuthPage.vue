<script setup>
import { ref } from 'vue'
import { AlertTriangle, LogIn, UserPlus } from 'lucide-vue-next'
import { api } from '@/api/client'

const emit = defineEmits(['login-success'])

const mode = ref('login') // 'login' | 'register'
const email = ref('')
const password = ref('')
const fullName = ref('')
const role = ref('student')
const teacherInviteCode = ref('')

const loading = ref(false)
const error = ref('')

const switchMode = (next) => {
  mode.value = next
  error.value = ''
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
  } catch (err) {
    error.value = err.message || 'Gagal mendaftarkan akun baru.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center bg-paper px-4 py-10">
    <div class="w-full max-w-sm">
      <!-- Brand -->
      <div class="mb-6 flex items-center gap-3">
        <span class="grid h-11 w-11 place-items-center rounded-lg bg-ink">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6 text-accent-300"
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
          <p class="text-base font-semibold tracking-tight text-ink">KimiFun</p>
          <p class="text-xs text-ink-muted">Lab kimia virtual untuk kelas</p>
        </div>
      </div>

      <div class="rounded-xl border border-line bg-surface p-5 shadow-card sm:p-6">
        <h1 class="text-lg font-semibold tracking-tight text-ink">
          {{ mode === 'login' ? 'Masuk ke akun' : 'Buat akun baru' }}
        </h1>
        <p class="mt-1 text-xs leading-relaxed text-ink-muted">
          {{
            mode === 'login'
              ? 'Gunakan email dan password yang diberikan sekolah.'
              : 'Akun guru memerlukan kode undangan dari sekolah.'
          }}
        </p>

        <!-- Mode switch -->
        <div class="mt-4 grid grid-cols-2 gap-1 rounded-lg bg-sunken p-1" role="tablist" aria-label="Pilih mode akun">
          <button
            type="button"
            role="tab"
            :aria-selected="mode === 'login'"
            @click="switchMode('login')"
            class="min-h-[40px] rounded-md px-3 text-xs font-semibold transition-colors"
            :class="mode === 'login' ? 'bg-surface text-ink shadow-2xs' : 'text-ink-muted hover:text-ink'"
          >
            Masuk
          </button>
          <button
            type="button"
            role="tab"
            :aria-selected="mode === 'register'"
            @click="switchMode('register')"
            class="min-h-[40px] rounded-md px-3 text-xs font-semibold transition-colors"
            :class="mode === 'register' ? 'bg-surface text-ink shadow-2xs' : 'text-ink-muted hover:text-ink'"
          >
            Daftar
          </button>
        </div>

        <!-- Error -->
        <p
          v-if="error"
          role="alert"
          class="mt-4 flex items-start gap-2 rounded-md border border-danger-200 bg-danger-50 px-3 py-2 text-xs font-medium leading-relaxed text-danger-700"
        >
          <AlertTriangle class="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
          {{ error }}
        </p>

        <form
          class="mt-4 space-y-3"
          @submit.prevent="mode === 'login' ? handleLogin() : handleRegister()"
        >
          <div v-if="mode === 'register'">
            <label for="auth-name" class="mb-1 block text-xs font-semibold text-ink-soft">Nama lengkap</label>
            <input
              id="auth-name"
              v-model="fullName"
              type="text"
              autocomplete="name"
              placeholder="Nama sesuai daftar kelas"
              class="w-full rounded-md border border-line bg-paper px-3 py-2.5 text-sm text-ink outline-none transition-colors placeholder:text-ink-faint focus:border-accent focus:bg-surface"
            />
          </div>

          <div>
            <label for="auth-email" class="mb-1 block text-xs font-semibold text-ink-soft">Email</label>
            <input
              id="auth-email"
              v-model="email"
              type="email"
              autocomplete="email"
              inputmode="email"
              placeholder="nama@sekolah.sch.id"
              class="w-full rounded-md border border-line bg-paper px-3 py-2.5 text-sm text-ink outline-none transition-colors placeholder:text-ink-faint focus:border-accent focus:bg-surface"
            />
          </div>

          <div>
            <label for="auth-password" class="mb-1 block text-xs font-semibold text-ink-soft">Password</label>
            <input
              id="auth-password"
              v-model="password"
              type="password"
              :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
              placeholder="Minimal 8 karakter"
              class="w-full rounded-md border border-line bg-paper px-3 py-2.5 text-sm text-ink outline-none transition-colors placeholder:text-ink-faint focus:border-accent focus:bg-surface"
            />
          </div>

          <div v-if="mode === 'register'">
            <label for="auth-role" class="mb-1 block text-xs font-semibold text-ink-soft">Daftar sebagai</label>
            <select
              id="auth-role"
              v-model="role"
              class="w-full rounded-md border border-line bg-paper px-3 py-2.5 text-sm text-ink outline-none transition-colors focus:border-accent focus:bg-surface"
            >
              <option value="student">Siswa</option>
              <option value="teacher">Guru</option>
            </select>
          </div>

          <div v-if="mode === 'register' && role === 'teacher'">
            <label for="auth-invite" class="mb-1 block text-xs font-semibold text-ink-soft">Kode undangan guru</label>
            <input
              id="auth-invite"
              v-model="teacherInviteCode"
              type="text"
              placeholder="Kode dari sekolah"
              class="w-full rounded-md border border-line bg-paper px-3 py-2.5 font-mono text-sm text-ink outline-none transition-colors placeholder:font-sans placeholder:text-ink-faint focus:border-accent focus:bg-surface"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="mt-1 flex min-h-[44px] w-full items-center justify-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-ink-soft disabled:opacity-60"
          >
            <component :is="mode === 'login' ? LogIn : UserPlus" class="h-4 w-4 text-accent-300" aria-hidden="true" />
            {{ loading ? 'Memproses' : mode === 'login' ? 'Masuk' : 'Buat akun' }}
          </button>
        </form>
      </div>

      <p class="mt-4 text-center text-[11px] leading-relaxed text-ink-faint">
        Lupa password atau kode undangan? Hubungi guru atau admin sekolah.
      </p>
    </div>
  </div>
</template>
