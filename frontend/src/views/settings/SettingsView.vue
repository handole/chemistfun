<script setup>
import { ref } from 'vue'
import { User, Server, Shield, CheckCircle2, RotateCcw } from 'lucide-vue-next'

const props = defineProps({
  user: Object,
  backendOnline: Boolean
})

const emit = defineEmits(['logout', 'refresh'])
</script>

<template>
  <div class="space-y-6 max-w-3xl">
    <div>
      <h2 class="text-2xl font-extrabold text-slate-900 tracking-tight">Pengaturan Akun & Sistem</h2>
      <p class="text-xs text-slate-500 font-medium mt-1">Konfigurasi profil guru, status server backend FastAPI, dan kredensial akses.</p>
    </div>

    <!-- Profil Card -->
    <div class="bg-white rounded-3xl border border-slate-100 p-6 shadow-card space-y-4">
      <div class="flex items-center gap-3 pb-3 border-b border-slate-100">
        <User class="w-5 h-5 text-chemist-primary" />
        <h3 class="font-bold text-slate-900 text-sm">Informasi Akun Anda</h3>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
        <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-100">
          <span class="text-slate-400 font-medium">Nama Lengkap:</span>
          <p class="font-bold text-slate-900 text-sm mt-0.5">{{ user?.full_name || 'Guru Kimia' }}</p>
        </div>

        <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-100">
          <span class="text-slate-400 font-medium">Alamat Email:</span>
          <p class="font-bold text-slate-900 text-sm mt-0.5">{{ user?.email || 'guru@chemistfun.com' }}</p>
        </div>

        <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-100">
          <span class="text-slate-400 font-medium">Hak Akses (Role):</span>
          <p class="font-bold text-chemist-primary text-sm mt-0.5 capitalize">{{ user?.role || 'teacher' }} (Pendidik)</p>
        </div>

        <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-100">
          <span class="text-slate-400 font-medium">Public UUID:</span>
          <p class="font-mono text-[11px] text-slate-600 mt-0.5 truncate">{{ user?.uuid || 'Local Session' }}</p>
        </div>
      </div>
    </div>

    <!-- Backend Status Card -->
    <div class="bg-white rounded-3xl border border-slate-100 p-6 shadow-card space-y-4">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100">
        <div class="flex items-center gap-3">
          <Server class="w-5 h-5 text-emerald-600" />
          <h3 class="font-bold text-slate-900 text-sm">Status Endpoint API Backend</h3>
        </div>
        <button 
          @click="emit('refresh')"
          class="text-xs font-bold text-chemist-primary hover:underline flex items-center gap-1"
        >
          <RotateCcw class="w-3 h-3" />
          <span>Cek Ulang</span>
        </button>
      </div>

      <div class="p-4 rounded-2xl flex items-center justify-between" :class="backendOnline ? 'bg-emerald-50/70 border border-emerald-200' : 'bg-rose-50 border border-rose-200'">
        <div class="flex items-center gap-3">
          <span class="w-3 h-3 rounded-full" :class="backendOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'"></span>
          <div>
            <p class="text-xs font-bold" :class="backendOnline ? 'text-emerald-900' : 'text-rose-900'">
              {{ backendOnline ? 'Layanan FastAPI & PostgreSQL Terhubung Normal' : 'Koneksi API Backend Terputus' }}
            </p>
            <p class="text-[11px]" :class="backendOnline ? 'text-emerald-700' : 'text-rose-700'">
              URL: http://localhost:8000 (Docker network chemistfun_network)
            </p>
          </div>
        </div>

        <span class="text-xs font-mono font-bold px-2.5 py-1 rounded-md" :class="backendOnline ? 'bg-emerald-200/60 text-emerald-800' : 'bg-rose-200 text-rose-800'">
          {{ backendOnline ? 'HTTP 200' : 'OFFLINE' }}
        </span>
      </div>
    </div>
  </div>
</template>

