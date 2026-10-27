<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import {
  Calendar,
  Clock,
  Users,
  BookOpen,
  Plus,
  Trash2,
  Edit3,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Search,
  Filter,
  Check,
  ChevronRight,
  ClipboardList,
  Sparkles,
  UserCheck,
  Award
} from 'lucide-vue-next'
import { api } from '@/api/client'

const props = defineProps({
  user: Object
})

const loading = ref(false)
const journals = ref([])
const classes = ref([])
const selectedClassFilter = ref('')
const searchQuery = ref('')

// Form Modal State
const showModal = ref(false)
const modalMode = ref('create') // 'create' | 'edit'
const saving = ref(false)
const activeJournalUuid = ref(null)

// Selected class in modal (to fetch students & module materials)
const modalClassId = ref(null)
const classStudents = ref([])
const classModules = ref([])
const loadingClassData = ref(false)

// Form Fields
const form = ref({
  class_id: null,
  title: '',
  date: new Date().toISOString().split('T')[0],
  start_time: '07:30',
  end_time: '09:00',
  planned_materials: [],
  completed_materials: [],
  notes: '',
  attendances: []
})

// Load basic list
const loadClasses = async () => {
  try {
    const res = await api.classes.list(props.user?.id)
    classes.value = res || []
  } catch (err) {
    console.error('Gagal memuat kelas:', err)
  }
}

const loadJournals = async () => {
  loading.value = true
  try {
    const res = await api.journals.list(selectedClassFilter.value || null)
    journals.value = res || []
  } catch (err) {
    console.error('Gagal memuat jurnal:', err)
  } finally {
    loading.value = false
  }
}

// Watch class filter change
watch(selectedClassFilter, () => {
  loadJournals()
})

// When class in modal changes, fetch enrolled students and materials for that class
const onModalClassChange = async (classId) => {
  if (!classId) {
    classStudents.value = []
    classModules.value = []
    form.value.attendances = []
    return
  }

  const cls = classes.value.find(c => c.id === parseInt(classId))
  if (!cls) return

  loadingClassData.value = true
  try {
    // 1. Fetch Students
    const studentsRes = await api.classes.getStudents(cls.uuid)
    classStudents.value = studentsRes || []

    // Preserve existing attendances or initialize with PRESENT
    const existingMap = new Map(form.value.attendances.map(a => [a.student_id, a]))
    form.value.attendances = classStudents.value.map(s => {
      const exist = existingMap.get(s.id)
      return {
        student_id: s.id,
        student_name: s.full_name,
        student_email: s.email,
        status: exist ? exist.status : 'present',
        score: exist ? (exist.score ?? null) : null,
        notes: exist ? exist.notes || '' : ''
      }
    })

    // 2. Fetch Modules & Materials for this class's grade level
    const modulesRes = await api.content.listModules({
      grade_level: cls.grade_level || null,
      class_id: cls.id
    })
    
    // For each module, fetch its materials
    const modulesWithMats = await Promise.all(
      (modulesRes || []).map(async (mod) => {
        try {
          const mats = await api.content.listMaterials(mod.id)
          return { ...mod, materials: mats || [] }
        } catch {
          return { ...mod, materials: [] }
        }
      })
    )
    classModules.value = modulesWithMats
  } catch (err) {
    console.error('Gagal memuat data kelas:', err)
  } finally {
    loadingClassData.value = false
  }
}

// Open Create Modal
const openCreateModal = () => {
  modalMode.value = 'create'
  activeJournalUuid.value = null
  const defaultClass = classes.value.length > 0 ? classes.value[0].id : null
  form.value = {
    class_id: defaultClass,
    title: '',
    date: new Date().toISOString().split('T')[0],
    start_time: '07:30',
    end_time: '09:00',
    planned_materials: [],
    completed_materials: [],
    notes: '',
    attendances: []
  }
  showModal.value = true
  if (defaultClass) {
    onModalClassChange(defaultClass)
  }
}

// Open Edit Modal
const openEditModal = async (journalItem) => {
  modalMode.value = 'edit'
  activeJournalUuid.value = journalItem.uuid
  showModal.value = true
  loadingClassData.value = true

  try {
    const detail = await api.journals.get(journalItem.uuid)
    const cls = classes.value.find(c => c.id === detail.class_id)

    form.value = {
      class_id: detail.class_id,
      title: detail.title,
      date: detail.date,
      start_time: detail.start_time || '07:30',
      end_time: detail.end_time || '09:00',
      planned_materials: detail.planned_materials || [],
      completed_materials: detail.completed_materials || [],
      notes: detail.notes || '',
      attendances: (detail.attendances || []).map(a => ({
        student_id: a.student_id,
        student_name: a.student_name,
        student_email: a.student_email,
        status: a.status,
        score: a.score ?? null,
        notes: a.notes || ''
      }))
    }

    if (cls) {
      // Load modules
      const modulesRes = await api.content.listModules({
        grade_level: cls.grade_level || null,
        class_id: cls.id
      })
      const modulesWithMats = await Promise.all(
        (modulesRes || []).map(async (mod) => {
          try {
            const mats = await api.content.listMaterials(mod.id)
            return { ...mod, materials: mats || [] }
          } catch {
            return { ...mod, materials: [] }
          }
        })
      )
      classModules.value = modulesWithMats
    }
  } catch (err) {
    alert('Gagal memuat rincian jurnal: ' + err.message)
    showModal.value = false
  } finally {
    loadingClassData.value = false
  }
}

// Toggle Material Planned & Completed
const togglePlannedMaterial = (matId) => {
  const idx = form.value.planned_materials.indexOf(matId)
  if (idx > -1) {
    form.value.planned_materials.splice(idx, 1)
    // If removed from planned, also remove from completed
    const cIdx = form.value.completed_materials.indexOf(matId)
    if (cIdx > -1) form.value.completed_materials.splice(cIdx, 1)
  } else {
    form.value.planned_materials.push(matId)
  }
}

const toggleCompletedMaterial = (matId) => {
  const idx = form.value.completed_materials.indexOf(matId)
  if (idx > -1) {
    form.value.completed_materials.splice(idx, 1)
  } else {
    form.value.completed_materials.push(matId)
    // If marked completed, ensure it's in planned as well
    if (!form.value.planned_materials.includes(matId)) {
      form.value.planned_materials.push(matId)
    }
  }
}

// Quick Attendance Set All
const setAllAttendance = (status) => {
  form.value.attendances.forEach(a => {
    a.status = status
  })
}

// Save Journal
const handleSaveJournal = async () => {
  if (!form.value.class_id) {
    alert('Pilih kelas terlebih dahulu.')
    return
  }
  if (!form.value.title.trim()) {
    alert('Judul atau topik pertemuan wajib diisi.')
    return
  }

  saving.value = true
  try {
    const payload = {
      class_id: parseInt(form.value.class_id),
      title: form.value.title.trim(),
      date: form.value.date,
      start_time: form.value.start_time,
      end_time: form.value.end_time,
      planned_materials: form.value.planned_materials,
      completed_materials: form.value.completed_materials,
      notes: form.value.notes?.trim() || null,
      attendances: form.value.attendances.map(a => ({
        student_id: parseInt(a.student_id),
        status: a.status,
        score: a.score !== '' && a.score !== null && !isNaN(a.score) ? Number(a.score) : null,
        notes: a.notes?.trim() || null
      }))
    }

    if (modalMode.value === 'create') {
      await api.journals.create(payload)
    } else {
      await api.journals.update(activeJournalUuid.value, payload)
    }

    showModal.value = false
    await loadJournals()
  } catch (err) {
    alert('Gagal menyimpan jurnal: ' + err.message)
  } finally {
    saving.value = false
  }
}

// Delete Journal
const handleDeleteJournal = async (journalItem) => {
  if (!confirm(`Hapus jurnal pertemuan "${journalItem.title}"?`)) return
  try {
    await api.journals.delete(journalItem.uuid)
    await loadJournals()
  } catch (err) {
    alert('Gagal menghapus jurnal: ' + err.message)
  }
}

// Filtered Journals for Search
const filteredJournals = computed(() => {
  if (!searchQuery.value.trim()) return journals.value
  const q = searchQuery.value.toLowerCase()
  return journals.value.filter(j => 
    j.title.toLowerCase().includes(q) ||
    (j.class_name && j.class_name.toLowerCase().includes(q))
  )
})

onMounted(() => {
  loadClasses()
  loadJournals()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header Section -->
    <div class="bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-chemist-primary text-xs font-semibold">
          <ClipboardList class="w-3.5 h-3.5" />
          <span>Jurnal Pembelajaran & Presensi</span>
        </div>
        <h2 class="text-2xl font-bold text-slate-900 tracking-tight">
          Jurnal Mengajar Guru
        </h2>
        <p class="text-xs sm:text-sm text-slate-500 font-normal max-w-xl leading-relaxed">
          Catat waktu mengajar, ceklis capaian materi kimia yang diajarkan, serta pantau kehadiran murid secara terintegrasi.
        </p>
      </div>

      <button
        @click="openCreateModal"
        class="bg-chemist-dark hover:bg-slate-900 text-white px-5 py-3 rounded-2xl text-xs font-bold transition-all shadow-md flex items-center gap-2 shrink-0 active:scale-95"
      >
        <Plus class="w-4 h-4" />
        <span>Buat Jurnal Pertemuan</span>
      </button>
    </div>

    <!-- Filter & Search Bar -->
    <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
      <div class="flex items-center gap-3 flex-1 max-w-md bg-white border border-slate-200/80 rounded-2xl px-4 py-2.5 shadow-2xs">
        <Search class="w-4 h-4 text-slate-400 shrink-0" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Cari judul jurnal atau kelas..."
          class="w-full text-xs text-slate-800 bg-transparent outline-none placeholder:text-slate-400 font-medium"
        />
      </div>

      <div class="flex items-center gap-2">
        <Filter class="w-4 h-4 text-slate-400" />
        <select
          v-model="selectedClassFilter"
          class="bg-white border border-slate-200/80 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 outline-none shadow-2xs"
        >
          <option value="">Semua Kelas</option>
          <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }} ({{ c.grade_level }})</option>
        </select>
      </div>
    </div>

    <!-- Journals Grid / List -->
    <div v-if="loading" class="text-center py-12 text-slate-400 text-xs">
      Memuat riwayat jurnal mengajar...
    </div>

    <div v-else-if="filteredJournals.length === 0" class="bg-white rounded-3xl border border-slate-200/80 p-12 text-center space-y-3 shadow-sm">
      <ClipboardList class="w-12 h-12 text-slate-300 mx-auto" />
      <h3 class="text-base font-bold text-slate-800">Belum Ada Catatan Jurnal Mengajar</h3>
      <p class="text-xs text-slate-500 max-w-sm mx-auto leading-relaxed">
        Klik tombol "Buat Jurnal Pertemuan" untuk merekam presensi siswa dan materi yang telah diajarkan hari ini.
      </p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      <div
        v-for="item in filteredJournals"
        :key="item.id"
        class="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4"
      >
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-blue-50 text-chemist-primary text-[11px] font-bold">
              {{ item.class_name || 'Kelas' }}
            </span>
            <div class="flex items-center gap-1 text-[11px] text-slate-500 font-medium">
              <Calendar class="w-3.5 h-3.5 text-slate-400" />
              <span>{{ item.date }}</span>
            </div>
          </div>

          <div>
            <h4 class="text-base font-bold text-slate-900 leading-snug">{{ item.title }}</h4>
            <div class="flex items-center gap-2 text-xs text-slate-500 mt-1">
              <Clock class="w-3.5 h-3.5 text-slate-400" />
              <span>{{ item.start_time || '07:30' }} - {{ item.end_time || '09:00' }} WIB</span>
            </div>
          </div>

          <!-- Progress Checklist Summary -->
          <div class="bg-slate-50 border border-slate-100 rounded-xl p-3 space-y-2 text-xs">
            <div class="flex items-center justify-between text-slate-600 font-medium">
              <span class="flex items-center gap-1.5">
                <BookOpen class="w-3.5 h-3.5 text-chemist-primary" />
                <span>Materi Tuntas</span>
              </span>
              <span class="font-bold text-slate-900">
                {{ item.completed_materials?.length || 0 }} / {{ item.planned_materials?.length || 0 }} Materi
              </span>
            </div>

            <!-- Attendance Mini Stats -->
            <div class="flex items-center justify-between text-slate-600 font-medium pt-1 border-t border-slate-200/50">
              <span class="flex items-center gap-1.5">
                <UserCheck class="w-3.5 h-3.5 text-emerald-600" />
                <span>Presensi Murid</span>
              </span>
              <span class="font-bold text-emerald-700">
                {{ item.present_students }} / {{ item.total_students }} Hadir
              </span>
            </div>

            <!-- Average Assignment Score -->
            <div v-if="item.avg_score !== null && item.avg_score !== undefined" class="flex items-center justify-between text-slate-600 font-medium pt-1 border-t border-slate-200/50">
              <span class="flex items-center gap-1.5">
                <Award class="w-3.5 h-3.5 text-amber-500" />
                <span>Rata-rata Tugas</span>
              </span>
              <span class="font-bold text-amber-700 font-mono">
                {{ item.avg_score }}
              </span>
            </div>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
          <button
            @click="openEditModal(item)"
            class="flex-1 py-1.5 px-3 bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 transition-colors border border-slate-200/60"
          >
            <Edit3 class="w-3.5 h-3.5 text-slate-500" />
            <span>Lihat / Edit</span>
          </button>

          <button
            @click="handleDeleteJournal(item)"
            class="p-2 text-rose-500 hover:text-rose-700 hover:bg-rose-50 rounded-xl transition-colors"
            title="Hapus Jurnal"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL FORM CREATE / EDIT JURNAL -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs"
    >
      <div class="bg-white rounded-3xl shadow-elevated border border-slate-100 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Modal Header -->
        <div class="p-6 border-b border-slate-100 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-chemist-dark text-white flex items-center justify-center">
              <ClipboardList class="w-5 h-5 text-sky-400" />
            </div>
            <div>
              <h3 class="text-base font-bold text-slate-900">
                {{ modalMode === 'create' ? 'Buat Jurnal Pertemuan Baru' : 'Perbarui Jurnal Mengajar' }}
              </h3>
              <p class="text-xs text-slate-400">Pencatatan sesi mengajar, absensi murid, dan capaian silabus materi</p>
            </div>
          </div>

          <button
            @click="showModal = false"
            class="text-slate-400 hover:text-slate-600 p-2 rounded-xl hover:bg-slate-50 transition-colors"
          >
            ✕
          </button>
        </div>

        <!-- Modal Body (Scrollable) -->
        <div class="p-6 overflow-y-auto space-y-6 text-xs">
          <!-- Step 1: Info Pertemuan & Waktu -->
          <div class="space-y-4">
            <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-blue-100 text-chemist-primary flex items-center justify-center text-[10px] font-bold">1</span>
              <span>Informasi Kelas & Waktu Pertemuan</span>
            </h4>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              <!-- Class Select -->
              <div>
                <label class="block font-bold text-slate-700 mb-1">Kelas</label>
                <select
                  v-model="form.class_id"
                  @change="(e) => onModalClassChange(e.target.value)"
                  class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-800 outline-none font-semibold focus:border-chemist-primary"
                >
                  <option v-for="c in classes" :key="c.id" :value="c.id">
                    {{ c.name }} (Kelas {{ c.grade_level }})
                  </option>
                </select>
              </div>

              <!-- Date Input -->
              <div>
                <label class="block font-bold text-slate-700 mb-1">Tanggal</label>
                <input
                  type="date"
                  v-model="form.date"
                  class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-800 outline-none font-semibold focus:border-chemist-primary"
                />
              </div>

              <!-- Start Time -->
              <div>
                <label class="block font-bold text-slate-700 mb-1">Jam Mulai</label>
                <input
                  type="time"
                  v-model="form.start_time"
                  class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-800 outline-none font-semibold focus:border-chemist-primary"
                />
              </div>

              <!-- End Time -->
              <div>
                <label class="block font-bold text-slate-700 mb-1">Jam Selesai</label>
                <input
                  type="time"
                  v-model="form.end_time"
                  class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-800 outline-none font-semibold focus:border-chemist-primary"
                />
              </div>
            </div>

            <!-- Title / Topic -->
            <div>
              <label class="block font-bold text-slate-700 mb-1">Topik / Judul Pertemuan</label>
              <input
                type="text"
                v-model="form.title"
                placeholder="Contoh: Pertemuan 3 - Stoikiometri Reaksi & Konsep Mol"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-800 outline-none font-medium focus:border-chemist-primary"
              />
            </div>
          </div>

          <!-- Step 2: Checklist Materi (Direncanakan vs Dibahas) -->
          <div class="space-y-4 pt-4 border-t border-slate-100">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
                <span class="w-5 h-5 rounded-full bg-blue-100 text-chemist-primary flex items-center justify-center text-[10px] font-bold">2</span>
                <span>Checklist Materi Pembelajaran</span>
              </h4>
              <span class="text-[11px] text-slate-400">
                Pilih rencana materi dan tandai checklist jika sudah selesai dibahas
              </span>
            </div>

            <div v-if="loadingClassData" class="py-4 text-center text-slate-400">
              Memuat daftar materi silabus...
            </div>

            <div v-else-if="classModules.length === 0" class="p-4 bg-slate-50 border border-slate-200 rounded-2xl text-center text-slate-400">
              Belum ada modul & materi terdaftar untuk tingkatan kelas ini. Tambahkan materi pada menu "Modul Belajar".
            </div>

            <div v-else class="space-y-3 max-h-60 overflow-y-auto pr-1">
              <div
                v-for="mod in classModules"
                :key="mod.id"
                class="bg-slate-50/60 border border-slate-200/80 rounded-2xl p-3.5 space-y-2"
              >
                <div class="flex items-center justify-between">
                  <span class="font-bold text-slate-800">{{ mod.title }}</span>
                  <span class="text-[10px] bg-slate-200/60 text-slate-600 px-2 py-0.5 rounded-full font-semibold">
                    {{ mod.materials?.length || 0 }} Materi
                  </span>
                </div>

                <div v-if="mod.materials && mod.materials.length > 0" class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                  <div
                    v-for="mat in mod.materials"
                    :key="mat.id"
                    :class="[
                      'p-2.5 rounded-xl border flex items-center justify-between gap-2 transition-all',
                      form.completed_materials.includes(mat.id)
                        ? 'bg-emerald-50/70 border-emerald-300'
                        : form.planned_materials.includes(mat.id)
                          ? 'bg-blue-50/50 border-blue-200'
                          : 'bg-white border-slate-200/70'
                    ]"
                  >
                    <span class="font-semibold text-slate-800 truncate">{{ mat.title }}</span>

                    <div class="flex items-center gap-1.5 shrink-0">
                      <!-- Planned Toggle -->
                      <button
                        type="button"
                        @click="togglePlannedMaterial(mat.id)"
                        :class="[
                          'px-2 py-0.5 rounded text-[10px] font-bold transition-all',
                          form.planned_materials.includes(mat.id)
                            ? 'bg-blue-600 text-white'
                            : 'bg-slate-200 text-slate-600 hover:bg-slate-300'
                        ]"
                        title="Direncanakan dibahas"
                      >
                        Target
                      </button>

                      <!-- Completed Checkbox -->
                      <button
                        type="button"
                        @click="toggleCompletedMaterial(mat.id)"
                        :class="[
                          'px-2 py-0.5 rounded text-[10px] font-bold flex items-center gap-1 transition-all',
                          form.completed_materials.includes(mat.id)
                            ? 'bg-emerald-600 text-white shadow-2xs'
                            : 'bg-slate-200 text-slate-600 hover:bg-slate-300'
                        ]"
                        title="Tandai selesai diajarkan"
                      >
                        <Check class="w-3 h-3" />
                        <span>Selesai</span>
                      </button>
                    </div>
                  </div>
                </div>

                <p v-else class="text-[11px] text-slate-400 italic">Belum ada materi pada modul ini.</p>
              </div>
            </div>
          </div>

          <!-- Step 3: Presensi Kehadiran Murid -->
          <div class="space-y-4 pt-4 border-t border-slate-100">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
                <span class="w-5 h-5 rounded-full bg-blue-100 text-chemist-primary flex items-center justify-center text-[10px] font-bold">3</span>
                <span>Presensi Kehadiran Siswa ({{ form.attendances.length }} Murid)</span>
              </h4>

              <div class="flex items-center gap-1.5 flex-wrap">
                <span class="text-[10px] font-bold text-slate-400 uppercase">Set Semua:</span>
                <button
                  type="button"
                  @click="setAllAttendance('present')"
                  class="px-2 py-1 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 font-bold text-[10px] transition-colors"
                >
                  Semua Hadir
                </button>
                <button
                  type="button"
                  @click="setAllAttendance('permitted')"
                  class="px-2 py-1 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 font-bold text-[10px] transition-colors"
                >
                  Izin
                </button>
                <button
                  type="button"
                  @click="setAllAttendance('sick')"
                  class="px-2 py-1 rounded-lg bg-amber-50 text-amber-700 hover:bg-amber-100 font-bold text-[10px] transition-colors"
                >
                  Sakit
                </button>
              </div>
            </div>

            <div v-if="loadingClassData" class="py-4 text-center text-slate-400">
              Memuat daftar siswa...
            </div>

            <div v-else-if="form.attendances.length === 0" class="p-4 bg-slate-50 border border-slate-200 rounded-2xl text-center text-slate-400">
              Belum ada siswa yang terdaftar di kelas ini. Siswa dapat bergabung menggunakan kode kelas.
            </div>

            <div v-else class="border border-slate-200 rounded-2xl overflow-hidden">
              <table class="w-full text-left border-collapse">
                <thead class="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold">
                  <tr>
                    <th class="p-3 w-12 text-center">No</th>
                    <th class="p-3">Nama Siswa</th>
                    <th class="p-3 text-center">Status Presensi</th>
                    <th class="p-3 w-28 text-center">Nilai Tugas</th>
                    <th class="p-3">Keterangan</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-for="(att, idx) in form.attendances" :key="att.student_id" class="hover:bg-slate-50/50">
                    <td class="p-3 text-center text-slate-400 font-mono">{{ idx + 1 }}</td>
                    <td class="p-3">
                      <div class="font-bold text-slate-800">{{ att.student_name || 'Siswa ' + att.student_id }}</div>
                      <div class="text-[10px] text-slate-400">{{ att.student_email }}</div>
                    </td>
                    <td class="p-3 text-center">
                      <div class="inline-flex items-center gap-1 bg-slate-100 p-1 rounded-xl">
                        <button
                          type="button"
                          @click="att.status = 'present'"
                          :class="[
                            'px-2.5 py-1 rounded-lg font-bold text-[11px] transition-all',
                            att.status === 'present'
                              ? 'bg-emerald-600 text-white shadow-2xs'
                              : 'text-slate-500 hover:text-slate-800'
                          ]"
                        >
                          Hadir
                        </button>
                        <button
                          type="button"
                          @click="att.status = 'sick'"
                          :class="[
                            'px-2.5 py-1 rounded-lg font-bold text-[11px] transition-all',
                            att.status === 'sick'
                              ? 'bg-amber-500 text-white shadow-2xs'
                              : 'text-slate-500 hover:text-slate-800'
                          ]"
                        >
                          Sakit
                        </button>
                        <button
                          type="button"
                          @click="att.status = 'permitted'"
                          :class="[
                            'px-2.5 py-1 rounded-lg font-bold text-[11px] transition-all',
                            att.status === 'permitted'
                              ? 'bg-blue-600 text-white shadow-2xs'
                              : 'text-slate-500 hover:text-slate-800'
                          ]"
                        >
                          Izin
                        </button>
                        <button
                          type="button"
                          @click="att.status = 'absent'"
                          :class="[
                            'px-2.5 py-1 rounded-lg font-bold text-[11px] transition-all',
                            att.status === 'absent'
                              ? 'bg-rose-600 text-white shadow-2xs'
                              : 'text-slate-500 hover:text-slate-800'
                          ]"
                        >
                          Alpa
                        </button>
                      </div>
                    </td>
                    <td class="p-3 text-center">
                      <input
                        type="number"
                        min="0"
                        max="100"
                        step="0.5"
                        v-model.number="att.score"
                        placeholder="0 - 100"
                        class="w-20 text-center bg-slate-50 border border-slate-200 rounded-lg px-2 py-1.5 text-xs text-slate-800 font-semibold outline-none focus:border-chemist-primary"
                      />
                    </td>
                    <td class="p-3">
                      <input
                        type="text"
                        v-model="att.notes"
                        placeholder="Catatan kehadiran (opsional)..."
                        class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 outline-none focus:border-chemist-primary"
                      />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Step 4: Catatan Guru / Evaluasi Kelas -->
          <div class="space-y-2 pt-4 border-t border-slate-100">
            <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-blue-100 text-chemist-primary flex items-center justify-center text-[10px] font-bold">4</span>
              <span>Catatan Refleksi & Kendala Pembelajaran</span>
            </h4>
            <textarea
              rows="3"
              v-model="form.notes"
              placeholder="Tuliskan kendala siswa, hal yang perlu diulang pada pertemuan depan, atau catatan khusus praktikum..."
              class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-800 outline-none focus:border-chemist-primary"
            ></textarea>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="p-6 border-t border-slate-100 bg-slate-50 flex items-center justify-end gap-3">
          <button
            type="button"
            @click="showModal = false"
            class="px-4 py-2.5 border border-slate-200 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
          >
            Batal
          </button>

          <button
            type="button"
            @click="handleSaveJournal"
            :disabled="saving"
            class="px-6 py-2.5 bg-chemist-dark hover:bg-slate-900 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition-all shadow-md flex items-center gap-2"
          >
            <Check class="w-4 h-4 text-emerald-400" />
            <span>{{ saving ? 'Menyimpan...' : 'Simpan Jurnal Pertemuan' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
