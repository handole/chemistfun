<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { FlaskConical, Sparkles, Check, Play, Save, RefreshCw, AlertCircle, Layers } from 'lucide-vue-next'
import { api } from '@/api/client'
import StoichiometryLab from '@/views/virtual-lab/StoichiometryLab.vue'

const props = defineProps({
  initialMaterial: Object,
  user: Object
})

const classes = ref([])
const selectedClassId = ref(null)
const materialsList = ref([])
const selectedMaterial = ref(null)

const activeLabTab = ref('stoichiometry') // 'stoichiometry' | 'titration'
const loading = ref(false)
const saving = ref(false)
const saveSuccess = ref(false)

// AI Lab Generator State
const aiPromptInput = ref('')
const isGeneratingAI = ref(false)
const aiError = ref('')
const aiSuccessMsg = ref('')

// Virtual Lab Form State
const labStatus = ref('ready')
const aiPromptHistory = ref('')
const config = ref({
  lab_title: 'Simulasi Reaksi Asam Basa',
  solution_name: 'HCl (Asam Klorida)',
  solution_molarity: 0.1,
  titrant_name: 'NaOH (Natrium Hidroksida)',
  titrant_molarity: 0.1,
  indicator_type: 'Phenolphthalein (PP)',
  color_start: '#F8FAFC',
  color_end: '#F472B6', // Pink titration
  max_volume_ml: 50,
  reaction_type: 'neutralization'
})

// Interactive Preview Simulation in Beaker
const currentVolume = ref(15)
const isSimulating = ref(false)

const eqVolume = computed(() => {
  const m1 = config.value.solution_molarity || 0.1
  const m2 = config.value.titrant_molarity || 0.1
  const v1 = 25 // 25 mL analit di erlenmeyer
  return +((m1 * v1) / (m2 || 1)).toFixed(1)
})

const liquidColor = computed(() => {
  if (currentVolume.value >= eqVolume.value) {
    return config.value.color_end || 'rgba(244, 114, 182, 0.8)'
  }
  return config.value.color_start || 'rgba(224, 242, 254, 0.5)'
})

const phValue = computed(() => {
  const eq = eqVolume.value || 25
  if (currentVolume.value < eq) {
    const diff = (eq - currentVolume.value) / eq
    return (1.0 + (1 - diff) * 6.0).toFixed(1)
  } else if (Math.abs(currentVolume.value - eq) < 0.2) {
    return '7.0'
  } else {
    const diff = (currentVolume.value - eq) / (config.value.max_volume_ml || 50)
    return Math.min(14.0, +(7.0 + diff * 7.0)).toFixed(1)
  }
})

const loadClassesAndMaterials = async () => {
  loading.value = true
  try {
    const allMats = []
    
    // 1. Fetch from modules across grades
    for (const lvl of ['X', 'XI', 'XII']) {
      try {
        const mods = await api.content.listModulesByGrade(lvl)
        for (const m of mods || []) {
          const mats = await api.content.listMaterials(m.id)
          allMats.push(...(mats || []))
        }
      } catch (e) {}
    }

    // 2. Fetch classes if any
    try {
      const cls = await api.classes.list()
      classes.value = cls || []
      for (const c of classes.value) {
        try {
          const mods = await api.content.listModules(c.id)
          for (const m of mods || []) {
            const mats = await api.content.listMaterials(m.id)
            allMats.push(...(mats || []))
          }
        } catch (e) {}
      }
    } catch (e) {}

    // Deduplicate
    const unique = []
    const seen = new Set()
    for (const m of allMats) {
      if (!seen.has(m.uuid)) {
        seen.add(m.uuid)
        unique.push(m)
      }
    }

    if (props.initialMaterial && !seen.has(props.initialMaterial.uuid)) {
      unique.unshift(props.initialMaterial)
    }

    materialsList.value = unique

    if (props.initialMaterial) {
      const found = unique.find(m => m.uuid === props.initialMaterial.uuid) || props.initialMaterial
      await selectMaterial(found)
      activeLabTab.value = 'titration'
    } else if (unique.length > 0) {
      await selectMaterial(unique[0])
    }
  } catch (err) {
    console.error('Gagal mengambil data:', err)
  } finally {
    loading.value = false
  }
}

const selectMaterial = async (mat) => {
  if (!mat) return
  selectedMaterial.value = mat
  aiPromptInput.value = mat.title ? `Praktikum reaksi dan simulasi untuk ${mat.title}` : ''
  try {
    const lab = await api.content.getLab(mat.uuid)
    if (lab) {
      labStatus.value = lab.status || 'ready'
      aiPromptHistory.value = lab.ai_prompt_history || ''
      if (lab.config_data && Object.keys(lab.config_data).length > 0) {
        config.value = { ...config.value, ...lab.config_data }
      }
    }
  } catch (err) {
    // If not found, prepare ready-to-save custom lab for this material
    labStatus.value = 'ready'
    config.value.lab_title = `Simulasi Praktikum: ${mat.title}`
  }
}

watch(() => props.initialMaterial, async (newMat) => {
  if (newMat) {
    if (!materialsList.value.some(m => m.uuid === newMat.uuid)) {
      materialsList.value.unshift(newMat)
    }
    await selectMaterial(newMat)
    activeLabTab.value = 'titration'
  }
}, { immediate: true })

const saveLabConfig = async () => {
  if (!selectedMaterial.value) return
  saving.value = true
  saveSuccess.value = false
  try {
    await api.content.upsertLab(selectedMaterial.value.uuid, {
      material_id: selectedMaterial.value.id,
      ai_prompt_history: aiPromptHistory.value,
      config_data: config.value,
      status: labStatus.value || 'ready'
    })
    saveSuccess.value = true
    setTimeout(() => (saveSuccess.value = false), 4000)
  } catch (err) {
    alert('Gagal menyimpan konfigurasi lab: ' + err.message)
  } finally {
    saving.value = false
  }
}

const handleGenerateLabAI = async () => {
  if (!aiPromptInput.value.trim()) return
  isGeneratingAI.value = true
  aiError.value = ''
  aiSuccessMsg.value = ''

  try {
    const res = await api.content.generateLabWithAI(
      aiPromptInput.value.trim(),
      selectedMaterial.value?.uuid
    )
    if (res && res.config_data) {
      config.value = { ...config.value, ...res.config_data }
      aiPromptHistory.value = res.ai_prompt_history || aiPromptInput.value
      aiSuccessMsg.value = 'Parameter lab berhasil di-generate AI!'
      setTimeout(() => (aiSuccessMsg.value = ''), 4000)
    }
  } catch (err) {
    aiError.value = err.message || 'Gagal generate lab dengan AI.'
  } finally {
    isGeneratingAI.value = false
  }
}

const toggleTitration = () => {
  isSimulating.value = !isSimulating.value
  if (isSimulating.value) {
    const interval = setInterval(() => {
      if (!isSimulating.value || currentVolume.value >= 40) {
        clearInterval(interval)
        isSimulating.value = false
      } else {
        currentVolume.value += 1
      }
    }, 150)
  }
}

const resetSimulation = () => {
  isSimulating.value = false
  currentVolume.value = 10
}

onMounted(() => {
  loadClassesAndMaterials()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-extrabold text-slate-900 tracking-tight">Konfigurasi Lab Virtual & Simulasi</h2>
        <p class="text-xs text-slate-500 font-medium mt-1">Atur parameter reaksi kimia interaktif yang akan dijalankan oleh siswa di laboratorium maya.</p>
      </div>

      <!-- Selector Material -->
      <div class="flex items-center gap-2 self-start sm:self-auto">
        <label class="text-xs font-bold text-slate-500 whitespace-nowrap">Materi Terpilih:</label>
        <select 
          v-if="materialsList.length > 0"
          :value="selectedMaterial?.uuid"
          @change="(e) => selectMaterial(materialsList.find(m => m.uuid === e.target.value))"
          class="bg-white text-xs font-bold px-3 py-2 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none shadow-2xs max-w-xs truncate"
        >
          <option v-for="m in materialsList" :key="m.uuid" :value="m.uuid">{{ m.title }}</option>
        </select>
        <span v-else class="text-xs text-slate-400 italic">Belum ada materi dibuat</span>
      </div>
    </div>

    <!-- Lab Engine Selector Tabs -->
    <div class="flex items-center gap-2 border-b border-slate-200 pb-3">
      <button
        @click="activeLabTab = 'stoichiometry'"
        :class="[
          'px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2',
          activeLabTab === 'stoichiometry'
            ? 'bg-slate-900 text-white shadow-md'
            : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
        ]"
      >
        <Layers class="w-4 h-4 text-sky-400" />
        <span>Stoikiometri Multi-Representasi (E-LKPD Inquiry)</span>
      </button>

      <button
        @click="activeLabTab = 'titration'"
        :class="[
          'px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2',
          activeLabTab === 'titration'
            ? 'bg-slate-900 text-white shadow-md'
            : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
        ]"
      >
        <FlaskConical class="w-4 h-4 text-pink-400" />
        <span>Simulator Titrasi Asam-Basa (Buret & Erlenmeyer)</span>
      </button>
    </div>

    <!-- Active View 1: Stoichiometry Lab (Integrated from baselab.html) -->
    <div v-if="activeLabTab === 'stoichiometry'">
      <StoichiometryLab :material="selectedMaterial" :user="user" />
    </div>

    <!-- Active View 2: Titration Lab Config -->
    <div v-else-if="activeLabTab === 'titration'">
      <!-- Empty State if no materials -->
      <div v-if="materialsList.length === 0" class="bg-white p-12 rounded-3xl border border-slate-100 text-center space-y-3">
        <FlaskConical class="w-12 h-12 text-slate-300 mx-auto" />
        <h3 class="font-bold text-slate-800 text-base">Belum Ada Materi Pembelajaran</h3>
        <p class="text-xs text-slate-400 max-w-md mx-auto">
          Simulasi Lab Virtual melekat secara 1-ke-1 dengan materi teori kimia. Silakan buat materi pada menu "Modul Belajar" terlebih dahulu.
        </p>
      </div>

      <!-- Workspace Grid: Parameter Form on Left, Interactive Simulation Canvas on Right -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <!-- Left: Form Parameters (6 Cols) -->
      <div class="lg:col-span-6 bg-white rounded-3xl border border-slate-100 p-6 shadow-card space-y-5">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h4 class="text-sm font-bold text-slate-900">Parameter Eksperimen</h4>
            <p class="text-xs text-slate-400">Untuk materi: <span class="font-semibold text-slate-700">{{ selectedMaterial?.title }}</span></p>
          </div>

          <!-- Status Draft/Ready pill -->
          <select 
            v-model="labStatus"
            class="text-xs font-bold px-2.5 py-1 rounded-full border outline-none cursor-pointer"
            :class="labStatus === 'ready' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-amber-50 text-amber-700 border-amber-200'"
          >
            <option value="ready">🟢 Ready (Siap Pakai)</option>
            <option value="draft">🟡 Draft (Penyusunan)</option>
          </select>
        </div>

        <!-- AI Generator Assistant Box -->
        <div class="bg-slate-50 border border-slate-200/80 rounded-2xl p-3.5 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-800 flex items-center gap-1.5">
              <Sparkles class="w-3.5 h-3.5 text-chemist-primary" />
              <span>Generate Parameter Simulasi</span>
            </span>
          </div>
          <div class="flex gap-2">
            <input 
              v-model="aiPromptInput"
              type="text"
              placeholder="Ketik topik simulasi, cth: Titrasi cuka dapur dengan NaOH 0.1M..."
              @keyup.enter="handleGenerateLabAI"
              class="flex-1 bg-white border border-slate-200 focus:border-chemist-primary rounded-xl px-3 py-2 text-xs text-slate-800 outline-none"
            />
            <button 
              @click="handleGenerateLabAI"
              :disabled="isGeneratingAI || !aiPromptInput.trim()"
              class="bg-chemist-dark hover:bg-slate-900 disabled:opacity-50 text-white px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all shadow-2xs shrink-0"
            >
              <RefreshCw v-if="isGeneratingAI" class="w-3.5 h-3.5 animate-spin" />
              <Sparkles v-else class="w-3.5 h-3.5 text-sky-400" />
              <span>{{ isGeneratingAI ? 'Memproses...' : 'Generate' }}</span>
            </button>
          </div>
          <p v-if="aiSuccessMsg" class="text-[11px] text-emerald-600 font-semibold">{{ aiSuccessMsg }}</p>
          <p v-if="aiError" class="text-[11px] text-rose-600 font-semibold">{{ aiError }}</p>
        </div>

        <div class="space-y-4 text-xs">
          <!-- Lab Title -->
          <div>
            <label class="block font-bold text-slate-700 mb-1">Nama Judul Simulasi</label>
            <input 
              v-model="config.lab_title"
              type="text" 
              class="w-full bg-slate-50 focus:bg-white text-xs px-3 py-2 rounded-xl border border-slate-200 focus:border-chemist-primary outline-none"
            />
          </div>

          <!-- Reagent 1: Titrand -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-bold text-slate-700 mb-1">Larutan Analit (Di Erlenmeyer)</label>
              <input 
                v-model="config.solution_name"
                type="text" 
                class="w-full bg-slate-50 focus:bg-white text-xs px-3 py-2 rounded-xl border border-slate-200 outline-none font-semibold"
              />
            </div>
            <div>
              <label class="block font-bold text-slate-700 mb-1">Konsentrasi Analit (M)</label>
              <input 
                v-model.number="config.solution_molarity"
                type="number" 
                step="0.01"
                class="w-full bg-slate-50 focus:bg-white text-xs px-3 py-2 rounded-xl border border-slate-200 outline-none"
              />
            </div>
          </div>

          <!-- Reagent 2: Titrant -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-bold text-slate-700 mb-1">Larutan Titran (Di Buret)</label>
              <input 
                v-model="config.titrant_name"
                type="text" 
                class="w-full bg-slate-50 focus:bg-white text-xs px-3 py-2 rounded-xl border border-slate-200 outline-none font-semibold"
              />
            </div>
            <div>
              <label class="block font-bold text-slate-700 mb-1">Konsentrasi Titran (M)</label>
              <input 
                v-model.number="config.titrant_molarity"
                type="number" 
                step="0.01"
                class="w-full bg-slate-50 focus:bg-white text-xs px-3 py-2 rounded-xl border border-slate-200 outline-none"
              />
            </div>
          </div>

          <!-- Indicator -->
          <div>
            <label class="block font-bold text-slate-700 mb-1">Indikator Perubahan Warna</label>
            <input 
              v-model="config.indicator_type"
              type="text" 
              class="w-full bg-slate-50 focus:bg-white text-xs px-3 py-2 rounded-xl border border-slate-200 outline-none"
            />
          </div>

          <!-- Prompt History / Catatan AI -->
          <div>
            <label class="block font-bold text-slate-700 mb-1">Catatan Panduan Praktikum Siswa</label>
            <textarea 
              v-model="aiPromptHistory"
              rows="3"
              placeholder="Instruksi untuk siswa: 'Teteskan NaOH perlahan hingga larutan di dalam labu erlenmeyer berubah warna menjadi merah muda konstan...'"
              class="w-full bg-slate-50 focus:bg-white text-xs px-3 py-2 rounded-xl border border-slate-200 outline-none"
            ></textarea>
          </div>
        </div>

        <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
          <span v-if="saveSuccess" class="text-xs text-emerald-600 font-bold flex items-center gap-1">
            <Check class="w-4 h-4" />
            <span>Tersimpan di database!</span>
          </span>
          <span v-else class="text-xs text-slate-400">Siap diterapkan ke dashboard siswa</span>

          <div v-if="saveSuccess" class="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 font-semibold flex items-center gap-2">
            <Check class="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Konfigurasi Lab berhasil disimpan dan aktif! Siswa yang mengakses materi ini sekarang dapat langsung menjalankan simulasi praktikum ini.</span>
          </div>

          <button 
            @click="saveLabConfig"
            :disabled="saving"
            class="inline-flex items-center gap-2 bg-chemist-dark hover:bg-slate-900 text-white text-xs font-bold px-5 py-2.5 rounded-xl shadow-md transition-all active:scale-95 disabled:opacity-50"
          >
            <Save class="w-4 h-4 text-emerald-400" />
            <span>{{ saving ? 'Menyimpan...' : 'Simpan & Publikasikan ke Siswa' }}</span>
          </button>
        </div>
      </div>

      <!-- Right: Live Interactive Simulation Preview (6 Cols) -->
      <div class="lg:col-span-6 bg-white rounded-3xl border border-slate-100 p-6 shadow-card space-y-5">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h4 class="text-sm font-bold text-slate-900">Pratinjau Simulasi Interaktif</h4>
            <p class="text-xs text-slate-400">Tampilan langsung apa yang akan dieksekusi siswa.</p>
          </div>
          <button 
            @click="resetSimulation"
            class="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100"
            title="Reset Percobaan"
          >
            <RefreshCw class="w-4 h-4" />
          </button>
        </div>

        <!-- Beaker & Titration Canvas -->
        <div class="h-64 bg-slate-50 rounded-2xl border border-slate-100 relative flex items-center justify-center overflow-hidden">
          <!-- Buret tip above -->
          <div class="absolute top-2 w-3 h-16 bg-slate-300 rounded-b flex flex-col justify-end items-center">
            <span v-if="isSimulating" class="w-1.5 h-1.5 rounded-full bg-blue-500 animate-ping mb-1"></span>
          </div>

          <!-- Erlenmeyer Flask Simulation -->
          <div class="w-36 h-44 relative flex flex-col items-center justify-end">
            <!-- Flask Neck -->
            <div class="w-10 h-14 border-l-2 border-r-2 border-slate-400 bg-transparent z-10"></div>
            
            <!-- Flask Body (Triangular Trapeze) -->
            <div 
              class="w-36 h-30 border-2 border-slate-400 rounded-b-2xl relative overflow-hidden flex flex-col justify-end p-1 transition-colors duration-500"
              :style="{ backgroundColor: liquidColor }"
            >
              <!-- Liquid level wave -->
              <div 
                class="w-full rounded-b-xl transition-all duration-300"
                :style="{ height: `${Math.min(currentVolume * 2.2, 90)}%`, backgroundColor: liquidColor }"
              ></div>

              <!-- Measurement Lines -->
              <div class="absolute left-2 top-4 text-[9px] font-mono text-slate-400 space-y-2">
                <div>- 50ml</div>
                <div>- 25ml</div>
                <div>- 10ml</div>
              </div>
            </div>
          </div>

          <!-- Floating Telemetry Card -->
          <div class="absolute right-4 bottom-4 bg-white/95 backdrop-blur-md p-3 rounded-xl border border-slate-200 shadow-sm text-xs space-y-1">
            <div class="flex items-center justify-between gap-3">
              <span class="text-slate-400">pH Larutan:</span>
              <span class="font-mono font-bold text-slate-900">{{ phValue }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-slate-400">Titran Masuk:</span>
              <span class="font-mono font-bold text-chemist-primary">{{ currentVolume }} mL</span>
            </div>
          </div>
        </div>

        <!-- Controls for Teacher Test -->
        <div class="space-y-3">
          <div class="flex items-center justify-between text-xs font-semibold text-slate-600">
            <span>Uji Kran Buret (Volume Titran):</span>
            <span class="font-mono font-bold text-slate-800">{{ currentVolume }} / 50 mL</span>
          </div>

          <input 
            type="range" 
            min="0" 
            max="50" 
            v-model.number="currentVolume"
            class="w-full accent-chemist-primary cursor-pointer"
          />

          <div class="flex items-center gap-2 pt-2">
            <button 
              @click="toggleTitration"
              class="flex-1 py-2 px-4 rounded-xl text-xs font-bold text-white transition-colors flex items-center justify-center gap-2"
              :class="isSimulating ? 'bg-rose-500 hover:bg-rose-600' : 'bg-chemist-primary hover:bg-blue-600'"
            >
              <Play class="w-3.5 h-3.5" />
              <span>{{ isSimulating ? 'Hentikan Aliran' : 'Mulai Tetes Titrasi Otomatis' }}</span>
            </button>
            <button 
              @click="resetSimulation"
              class="py-2 px-4 rounded-xl text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200"
            >
              Reset
            </button>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

