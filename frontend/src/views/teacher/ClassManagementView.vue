<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Users, Copy, Check, Trash2, UserX, AlertCircle } from 'lucide-vue-next'
import { api } from '@/api/client'

const props = defineProps({
  user: Object
})

const classes = ref([])
const loading = ref(true)
const showCreateModal = ref(false)
const selectedClass = ref(null)
const enrolledStudents = ref([])
const loadingStudents = ref(false)
const copiedCode = ref(null)

const newClassName = ref('')
const newClassGradeLevel = ref('X')
const newClassCode = ref('')
const createError = ref('')
const isSubmitting = ref(false)

const loadClasses = async () => {
  loading.value = true
  try {
    const res = await api.classes.list()
    classes.value = res || []
    if (classes.value.length > 0 && !selectedClass.value) {
      selectClass(classes.value[0])
    }
  } catch (err) {
    console.error('Gagal mengambil daftar kelas:', err)
  } finally {
    loading.value = false
  }
}

const generateRandomCode = () => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let code = ''
  for (let i = 0; i < 6; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  newClassCode.value = `CHEM-${code}`
}

const openCreateModal = () => {
  newClassName.value = ''
  generateRandomCode()
  createError.value = ''
  showCreateModal.value = true
}

const handleCreateClass = async () => {
  if (!newClassName.value.trim()) {
    createError.value = 'Nama kelas harus diisi.'
    return
  }
  isSubmitting.value = true
  createError.value = ''
  try {
    const res = await api.classes.create({
      name: newClassName.value.trim(),
      grade_level: newClassGradeLevel.value,
      enrollment_code: newClassCode.value.trim()
    })
    classes.value.push(res)
    showCreateModal.value = false
    selectClass(res)
  } catch (err) {
    createError.value = err.message || 'Gagal membuat kelas baru.'
  } finally {
    isSubmitting.value = false
  }
}

const selectClass = async (cls) => {
  selectedClass.value = cls
  loadingStudents.value = true
  try {
    const res = await api.classes.getStudents(cls.uuid)
    enrolledStudents.value = res || []
  } catch (err) {
    console.error('Gagal mengambil siswa:', err)
    enrolledStudents.value = []
  } finally {
    loadingStudents.value = false
  }
}

const handleUnenroll = async (student) => {
  if (!confirm(`Keluarkan ${student.full_name} dari kelas ${selectedClass.value.name}?`)) return
  try {
    await api.classes.unenroll(selectedClass.value.uuid, student.id)
    enrolledStudents.value = enrolledStudents.value.filter(s => s.id !== student.id)
  } catch (err) {
    alert('Gagal mengeluarkan siswa: ' + err.message)
  }
}

const handleDeleteClass = async (cls) => {
  if (!confirm(`Hapus kelas "${cls.name}" beserta seluruh materi di dalamnya?`)) return
  try {
    await api.classes.delete(cls.uuid)
    classes.value = classes.value.filter(c => c.id !== cls.id)
    if (selectedClass.value?.id === cls.id) {
      selectedClass.value = classes.value[0] || null
      if (selectedClass.value) selectClass(selectedClass.value)
    }
  } catch (err) {
    alert('Gagal menghapus kelas: ' + err.message)
  }
}

const copyCode = (code) => {
  navigator.clipboard.writeText(code)
  copiedCode.value = code
  setTimeout(() => (copiedCode.value = null), 2000)
}

onMounted(() => {
  loadClasses()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header Page -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-extrabold text-slate-900 tracking-tight">Manajemen Kelas Kimia</h2>
        <p class="text-xs text-slate-500 font-medium mt-1">Kelola kelas, bagikan kode bergabung kepada siswa, dan monitor peserta didik.</p>
      </div>
      <button 
        @click="openCreateModal"
        class="inline-flex items-center gap-2 bg-chemist-dark hover:bg-slate-900 text-white text-xs sm:text-sm font-bold px-4 py-2.5 rounded-xl shadow-md transition-all active:scale-95 self-start"
      >
        <Plus class="w-4 h-4 text-emerald-400" />
        <span>Buat Kelas Baru</span>
      </button>
    </div>

    <!-- Main Content Layout (Split List & Detail) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <!-- Left: Classes Cards List (5 Cols) -->
      <div class="lg:col-span-5 space-y-3">
        <div v-if="loading" class="bg-white p-8 rounded-2xl border border-slate-100 text-center text-slate-400 text-sm">
          Memuat daftar kelas...
        </div>

        <div v-else-if="classes.length === 0" class="bg-white p-8 rounded-2xl border border-slate-100 text-center space-y-3">
          <p class="text-sm font-bold text-slate-700">Belum Ada Kelas Dibuat</p>
          <p class="text-xs text-slate-400">Klik tombol di atas untuk membuat kelas pertama Anda.</p>
        </div>

        <div 
          v-for="cls in classes" 
          :key="cls.id"
          @click="selectClass(cls)"
          class="p-5 rounded-2xl border transition-all cursor-pointer text-left relative overflow-hidden"
          :class="selectedClass?.id === cls.id 
            ? 'bg-white border-chemist-primary ring-2 ring-chemist-primary/15 shadow-card' 
            : 'bg-white/80 border-slate-100 hover:border-slate-300 hover:bg-white'"
        >
          <!-- Active indicator bar on left -->
          <div 
            v-if="selectedClass?.id === cls.id" 
            class="absolute left-0 top-0 bottom-0 w-1.5 bg-chemist-primary"
          ></div>

          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="flex items-center gap-1.5">
                <span class="text-[10px] font-bold px-2 py-0.5 bg-blue-50 text-chemist-primary rounded-md uppercase">Kimia</span>
                <span class="text-[10px] font-black px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-100 rounded-md uppercase">Kelas {{ cls.grade_level || 'X' }}</span>
              </div>
              <h4 class="font-bold text-slate-900 text-base mt-1.5">{{ cls.name }}</h4>
            </div>
            <button 
              @click.stop="handleDeleteClass(cls)"
              class="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg transition-colors"
              title="Hapus Kelas"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>

          <!-- Code pill -->
          <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span class="text-slate-400 font-medium">Kode Gabung:</span>
            <span class="font-mono font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded">{{ cls.enrollment_code }}</span>
          </div>
        </div>
      </div>

      <!-- Right: Selected Class Detail & Enrolled Students (7 Cols) -->
      <div class="lg:col-span-7 bg-white rounded-3xl border border-slate-100 p-6 shadow-card space-y-6">
        <div v-if="!selectedClass" class="text-center py-16 text-slate-400 text-sm">
          Pilih salah satu kelas di sebelah kiri untuk melihat detail & daftar siswa.
        </div>

        <template v-else>
          <!-- Class Header -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-100">
            <div>
              <h3 class="text-xl font-bold text-slate-900">{{ selectedClass.name }}</h3>
              <p class="text-xs text-slate-400 font-medium mt-0.5">Dikelola oleh Anda (Guru Pengampu)</p>
            </div>

            <!-- Enrollment Code Share Box -->
            <div class="flex items-center gap-2 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl">
              <span class="text-[11px] font-bold text-slate-500 uppercase">KODE:</span>
              <span class="font-mono font-bold text-sm text-slate-900">{{ selectedClass.enrollment_code }}</span>
              <button 
                @click="copyCode(selectedClass.enrollment_code)"
                class="ml-1 p-1 hover:bg-slate-200 rounded text-slate-600 transition-colors"
                title="Salin Kode"
              >
                <component :is="copiedCode === selectedClass.enrollment_code ? Check : Copy" class="w-3.5 h-3.5 text-chemist-primary" />
              </button>
            </div>
          </div>

          <!-- Students List Header -->
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Users class="w-4 h-4 text-chemist-primary" />
              <h4 class="font-bold text-slate-800 text-sm">Siswa Terdaftar ({{ enrolledStudents.length }})</h4>
            </div>
            <span class="text-xs text-slate-400">Siswa bergabung menggunakan kode di atas</span>
          </div>

          <!-- Students Table / List -->
          <div v-if="loadingStudents" class="text-center py-8 text-slate-400 text-xs">
            Memuat daftar siswa...
          </div>

          <div v-else-if="enrolledStudents.length === 0" class="text-center py-10 bg-slate-50/60 rounded-2xl border border-dashed border-slate-200 space-y-2">
            <p class="text-sm font-semibold text-slate-600">Belum ada siswa yang bergabung</p>
            <p class="text-xs text-slate-400 max-w-sm mx-auto">
              Siswa dapat mendaftar dan memasukkan kode <span class="font-mono font-bold text-slate-700">{{ selectedClass.enrollment_code }}</span> pada menu "Gabung Kelas".
            </p>
          </div>

          <div v-else class="divide-y divide-slate-100">
            <div 
              v-for="st in enrolledStudents" 
              :key="st.id"
              class="py-3 flex items-center justify-between hover:bg-slate-50/80 px-2 rounded-xl transition-colors"
            >
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-slate-200 text-slate-700 font-bold text-xs flex items-center justify-center">
                  {{ st.full_name?.substring(0, 2).toUpperCase() }}
                </div>
                <div>
                  <p class="text-xs font-bold text-slate-900">{{ st.full_name }}</p>
                  <p class="text-[11px] text-slate-400">{{ st.email }}</p>
                </div>
              </div>

              <button 
                @click="handleUnenroll(st)"
                class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                title="Keluarkan Siswa"
              >
                <UserX class="w-4 h-4" />
              </button>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Modal Buat Kelas Baru -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-elevated space-y-5">
        <div>
          <h3 class="text-lg font-bold text-slate-900">Buat Kelas Kimia Baru</h3>
          <p class="text-xs text-slate-500 mt-0.5">Tentukan nama kelas dan kode unik untuk siswa Anda.</p>
        </div>

        <div v-if="createError" class="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 font-medium flex items-center gap-2">
          <AlertCircle class="w-4 h-4 shrink-0" />
          <span>{{ createError }}</span>
        </div>

        <div class="space-y-4 text-sm">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1.5">Nama Kelas / Sub-Kelas</label>
            <input 
              v-model="newClassName"
              type="text" 
              placeholder="Contoh: X-1, X-2, atau XI-IPA-A" 
              class="w-full bg-slate-50 focus:bg-white text-sm px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary focus:ring-2 focus:ring-chemist-primary/20 outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1.5">Tingkatan Level Kelas</label>
            <select
              v-model="newClassGradeLevel"
              class="w-full bg-slate-50 focus:bg-white text-sm px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none font-semibold text-slate-800"
            >
              <option value="X">Kelas X (Sepuluh)</option>
              <option value="XI">Kelas XI (Sebelas)</option>
              <option value="XII">Kelas XII (Dua Belas)</option>
            </select>
            <p class="text-[11px] text-slate-400 mt-1">Kelas ini otomatis mewarisi seluruh materi kurikulum level tersebut.</p>
          </div>

          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="block text-xs font-bold text-slate-700">Kode Enrollment (Gabung Kelas)</label>
              <button 
                type="button"
                @click="generateRandomCode"
                class="text-[11px] text-chemist-primary hover:underline font-semibold"
              >
                Acak Ulang
              </button>
            </div>
            <input 
              v-model="newClassCode"
              type="text" 
              class="w-full font-mono uppercase bg-slate-50 focus:bg-white text-sm px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-chemist-primary focus:ring-2 focus:ring-chemist-primary/20 outline-none tracking-wider"
            />
          </div>
        </div>

        <div class="flex items-center justify-end gap-2.5 pt-2 border-t border-slate-100">
          <button 
            type="button"
            @click="showCreateModal = false"
            class="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
          >
            Batal
          </button>
          <button 
            type="button"
            :disabled="isSubmitting"
            @click="handleCreateClass"
            class="px-5 py-2 rounded-xl text-xs font-bold bg-chemist-dark hover:bg-slate-900 text-white disabled:opacity-50 transition-all shadow-md"
          >
            {{ isSubmitting ? 'Menyimpan...' : 'Simpan Kelas' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

