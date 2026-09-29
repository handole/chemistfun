<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { CheckCircle2, AlertCircle, RefreshCw, Send, Check } from 'lucide-vue-next'
import { api } from '@/api/client'

const props = defineProps({
  material: Object,
  user: Object,
  readOnly: {
    type: Boolean,
    default: false
  }
})

// Current Stage (1 to 5)
const currentStage = ref(1)

const stages = [
  { id: 1, title: '1. Konsep Mol' },
  { id: 2, title: '2. Hukum Lavoisier' },
  { id: 3, title: '3. Penyetaraan Reaksi' },
  { id: 4, title: '4. Pereaksi Pembatas' },
  { id: 5, title: '5. Stoikiometri Larutan' }
]

// Canvas References & Animation
const canvasRef = ref(null)
let animationId = null
let particles = []

class Particle {
  constructor(type, x, y, color, size = 5) {
    const canvas = canvasRef.value
    this.type = type
    this.x = x || (canvas ? Math.random() * (canvas.width - 20) + 10 : 50)
    this.y = y || (canvas ? Math.random() * (canvas.height - 20) + 10 : 50)
    this.vx = (Math.random() - 0.5) * 1.2
    this.vy = (Math.random() - 0.5) * 1.2
    this.color = color
    this.size = size
  }

  draw(ctx) {
    ctx.beginPath()
    ctx.fillStyle = this.color
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
    ctx.closePath()
  }

  update(width, height) {
    this.x += this.vx
    this.y += this.vy
    if (this.x < 10 || this.x > width - 10) this.vx *= -1
    if (this.y < 10 || this.y > height - 10) this.vy *= -1
  }
}

const startAnimation = () => {
  if (animationId) cancelAnimationFrame(animationId)
  const loop = () => {
    const canvas = canvasRef.value
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    particles.forEach(p => {
      p.update(canvas.width, canvas.height)
      p.draw(ctx)
    })
    animationId = requestAnimationFrame(loop)
  }
  loop()
}

// Stage 1 State
const s1Mass = ref(56)
const s1Answer = ref('')

// Stage 2 State
const s2System = ref('closed')
const s2FinalMass = ref(100.0)
const s2Answer = ref('')
const s2HasRun = ref(false)

// Stage 3 State
const s3CoefA = ref(1)
const s3CoefB = ref(1)
const s3CoefC = ref(1)

// Stage 4 State
const s4H2 = ref(4)
const s4O2 = ref(2)
const s4HasRun = ref(false)
const s4Mrs = ref({ rH2: '-', rO2: '-', rH2O: '-', sH2: '-', sO2: '-', sH2O: '-' })
const s4Limiting = ref('')
const s4WaterHeight = ref(0)
const s4Answer = ref('H2')

// Stage 5 State
const s5Vol = ref(20)
const s5HasRun = ref(false)
const s5PptHeight = ref(0)
const s5Answer = ref('')

// Verification State from Backend
const verifying = ref(false)
const verificationResult = ref(null)

const selectStage = (stageId) => {
  currentStage.value = stageId
  verificationResult.value = null
  initStage(stageId)
}

const initStage = (stageId) => {
  particles = []
  const canvas = canvasRef.value
  if (canvas) {
    canvas.width = canvas.parentElement.clientWidth || 300
    canvas.height = 200
  }

  if (stageId === 1) {
    const moles = s1Mass.value / 56
    for (let i = 0; i < Math.round(moles * 10); i++) {
      particles.push(new Particle('Fe', null, null, '#475569', 5))
    }
  } else if (stageId === 2) {
    s2HasRun.value = false
    s2FinalMass.value = 100.0
    for (let i = 0; i < 12; i++) {
      particles.push(new Particle('Reactant', null, null, '#2563EB', 5))
    }
  } else if (stageId === 3) {
    updateStage3Particles()
  } else if (stageId === 4) {
    s4HasRun.value = false
    s4WaterHeight.value = 0
    s4Mrs.value = { rH2: '-', rO2: '-', rH2O: '-', sH2: '-', sO2: '-', sH2O: '-' }
    s4Limiting.value = ''
    updateStage4Particles()
  } else if (stageId === 5) {
    s5HasRun.value = false
    s5PptHeight.value = 0
    for (let i = 0; i < 8; i++) particles.push(new Particle('Pb', null, null, '#D97706', 6))
    for (let i = 0; i < 12; i++) particles.push(new Particle('I', null, null, '#2563EB', 4))
  }
}

// Stage 1 Actions
watch(s1Mass, (newVal) => {
  if (currentStage.value !== 1) return
  const moles = newVal / 56
  particles = []
  for (let i = 0; i < Math.round(moles * 10); i++) {
    particles.push(new Particle('Fe', null, null, '#475569', 5))
  }
})

// Stage 2 Actions
const runStage2 = () => {
  s2HasRun.value = true
  const isClosed = s2System.value === 'closed'
  s2FinalMass.value = isClosed ? 100.0 : 92.5
  particles = []
  const count = isClosed ? 12 : 6
  for (let i = 0; i < count; i++) {
    particles.push(new Particle('Product', null, null, '#D97706', 5))
  }
}

// Stage 3 Actions
const updateStage3Particles = () => {
  particles = []
  for (let i = 0; i < s3CoefA.value * 2; i++) particles.push(new Particle('N', null, null, '#2563EB', 5))
  for (let i = 0; i < s3CoefB.value * 2; i++) particles.push(new Particle('H', null, null, '#94A3B8', 4))
}
watch([s3CoefA, s3CoefB, s3CoefC], () => {
  if (currentStage.value === 3) updateStage3Particles()
})

// Stage 4 Actions
const updateStage4Particles = () => {
  particles = []
  for (let i = 0; i < s4H2.value; i++) particles.push(new Particle('H2', null, null, '#2563EB', 5))
  for (let i = 0; i < s4O2.value; i++) particles.push(new Particle('O2', null, null, '#DC2626', 6))
}
watch([s4H2, s4O2], () => {
  if (currentStage.value === 4 && !s4HasRun.value) updateStage4Particles()
})

const runStage4 = () => {
  s4HasRun.value = true
  const h2 = s4H2.value
  const o2 = s4O2.value

  const rH2 = (h2 / 2 <= o2 / 1) ? h2 : o2 * 2
  const rO2 = (h2 / 2 <= o2 / 1) ? h2 / 2 : o2
  const rH2O = rH2

  s4Mrs.value = {
    rH2: `-${rH2}`,
    rO2: `-${rO2}`,
    rH2O: `+${rH2O}`,
    sH2: h2 - rH2,
    sO2: o2 - rO2,
    sH2O: rH2O
  }

  s4Limiting.value = (h2 / 2 <= o2 / 1) ? 'Gas H₂' : 'Gas O₂'
  s4WaterHeight.value = Math.min((rH2O / 10) * 100, 85)

  particles = []
  for (let i = 0; i < h2 - rH2; i++) particles.push(new Particle('H2', null, null, '#2563EB', 5))
  for (let i = 0; i < o2 - rO2; i++) particles.push(new Particle('O2', null, null, '#DC2626', 6))
  for (let i = 0; i < rH2O; i++) particles.push(new Particle('H2O', null, null, '#7C3AED', 5))
}

// Stage 5 Actions
watch(s5Vol, () => {
  if (currentStage.value === 5 && !s5HasRun.value) {
    s5PptHeight.value = 0
  }
})

const runStage5 = () => {
  s5HasRun.value = true
  s5PptHeight.value = Math.min(s5Vol.value * 0.8, 45)
  const canvas = canvasRef.value
  particles = []
  for (let i = 0; i < 15; i++) {
    const p = new Particle(
      'PbI2',
      canvas ? canvas.width / 2 + (Math.random() * 80 - 40) : 100,
      canvas ? canvas.height - 20 : 150,
      '#D97706',
      5
    )
    p.vx = 0
    p.vy = 0
    particles.push(p)
  }
}

// Backend verification
const verifyAnswer = async () => {
  verifying.value = true
  verificationResult.value = null

  let payload = { stage: currentStage.value, user_answer: null, inputs: {} }

  if (currentStage.value === 1) {
    payload.user_answer = parseFloat(s1Answer.value) || 0
    payload.inputs = { mass: s1Mass.value, ar: 56 }
  } else if (currentStage.value === 2) {
    payload.user_answer = s2Answer.value
    payload.inputs = { system: s2System.value }
  } else if (currentStage.value === 3) {
    payload.user_answer = { a: s3CoefA.value, b: s3CoefB.value, c: s3CoefC.value }
    payload.inputs = { equation: 'N2 + H2 -> NH3' }
  } else if (currentStage.value === 4) {
    payload.user_answer = s4Answer.value
    payload.inputs = { h2: s4H2.value, o2: s4O2.value }
  } else if (currentStage.value === 5) {
    payload.user_answer = parseFloat(s5Answer.value) || 0
    payload.inputs = { vol_ml: s5Vol.value, molarity: 0.1, mr: 461 }
  }

  try {
    const res = await api.content.verifyInquiry(payload)
    verificationResult.value = res
  } catch (err) {
    verificationResult.value = {
      is_correct: false,
      explanation: 'Gagal menghubungi server: ' + err.message
    }
  } finally {
    verifying.value = false
  }
}

onMounted(() => {
  initStage(1)
  startAnimation()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<template>
  <div class="space-y-5">
    <!-- Navigation Tabs -->
    <div class="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
      <button
        v-for="s in stages"
        :key="s.id"
        @click="selectStage(s.id)"
        :class="[
          'px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap',
          currentStage === s.id
            ? 'bg-chemist-dark text-white shadow-sm'
            : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
        ]"
      >
        {{ s.title }}
      </button>
    </div>

    <!-- 3 Windows Multi-Representation Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      
      <!-- WINDOW 1: MAKROSKOPIK -->
      <div class="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm flex flex-col justify-between min-h-[360px]">
        <div>
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
            <span class="text-xs font-bold text-slate-900">1. Jendela Makroskopik</span>
            <span class="text-[11px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded-md">Fenomena</span>
          </div>

          <div class="h-48 bg-slate-50 rounded-xl border border-slate-100 flex flex-col items-center justify-center p-4 relative">
            <!-- Stage 1 Macro -->
            <div v-if="currentStage === 1" class="flex flex-col items-center gap-3">
              <div class="w-14 h-14 rounded-lg bg-slate-200 border border-slate-300 flex items-center justify-center text-slate-700 font-bold text-base shadow-2xs">
                Fe
              </div>
              <div class="bg-white border border-slate-200 px-3 py-1 rounded-md font-mono text-slate-800 font-bold text-sm shadow-2xs">
                {{ s1Mass.toFixed(2) }} g
              </div>
            </div>

            <!-- Stage 2 Macro -->
            <div v-else-if="currentStage === 2" class="flex flex-col items-center gap-3">
              <div class="w-20 h-24 border-2 border-t-0 border-slate-400 rounded-b-xl relative bg-white flex items-center justify-center">
                <span class="text-[11px] font-medium text-slate-600">
                  {{ s2System === 'closed' ? 'Tertutup' : 'Terbuka' }}
                </span>
              </div>
              <div class="bg-white border border-slate-200 px-3 py-1 rounded-md font-mono text-slate-800 font-bold text-sm shadow-2xs">
                {{ s2FinalMass.toFixed(2) }} g
              </div>
            </div>

            <!-- Stage 3 Macro -->
            <div v-else-if="currentStage === 3" class="text-center space-y-2">
              <div class="w-12 h-12 rounded-full bg-blue-50 border border-blue-100 flex items-center justify-center mx-auto text-blue-600 text-lg">
                ⚗️
              </div>
              <p class="text-xs font-semibold text-slate-800">Sintesis Gas Amonia</p>
              <p class="text-[11px] text-slate-500 font-mono">N₂ + 3H₂ ⇌ 2NH₃</p>
            </div>

            <!-- Stage 4 Macro -->
            <div v-else-if="currentStage === 4" class="flex flex-col items-center gap-2">
              <div class="w-20 h-28 border-2 border-t-0 border-slate-400 rounded-b-xl relative bg-white overflow-hidden">
                <div
                  class="absolute bottom-0 w-full bg-blue-100 border-t border-blue-300 transition-all duration-500"
                  :style="{ height: s4WaterHeight + '%' }"
                ></div>
              </div>
              <span class="text-[11px] text-slate-500">Volume H₂O terbentuk</span>
            </div>

            <!-- Stage 5 Macro -->
            <div v-else-if="currentStage === 5" class="flex flex-col items-center gap-2">
              <div class="w-20 h-28 border-2 border-t-0 border-slate-400 rounded-b-xl relative bg-white overflow-hidden">
                <div
                  class="absolute bottom-0 w-full bg-amber-200 border-t border-amber-400 transition-all duration-700"
                  :style="{ height: s5PptHeight + '%' }"
                ></div>
              </div>
              <span class="text-[11px] text-slate-600 font-medium">Endapan Kuning PbI₂</span>
            </div>
          </div>
        </div>

        <p class="text-xs text-slate-500 mt-3 pt-3 border-t border-slate-100 leading-relaxed">
          <span v-if="currentStage === 1">Pengukuran massa padatan logam Besi pada neraca analitis.</span>
          <span v-else-if="currentStage === 2">Reaksi CaCO₃ + 2HCl pada sistem terbuka atau tertutup.</span>
          <span v-else-if="currentStage === 3">Reaksi kesetimbangan gas pembentukan amonia.</span>
          <span v-else-if="currentStage === 4">Reaksi pembentukan air dengan pereaksi pembatas.</span>
          <span v-else-if="currentStage === 5">Reaksi pengendapan PbI₂ dari larutan KI dan Pb(NO₃)₂.</span>
        </p>
      </div>

      <!-- WINDOW 2: SUBMIKROSKOPIK -->
      <div class="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm flex flex-col justify-between min-h-[360px]">
        <div>
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
            <span class="text-xs font-bold text-slate-900">2. Jendela Submikroskopik</span>
            <span class="text-[11px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded-md">Partikel</span>
          </div>

          <div class="h-48 bg-slate-50 rounded-xl border border-slate-100 p-2 flex items-center justify-center">
            <canvas ref="canvasRef" class="w-full h-full bg-white rounded-lg border border-slate-200 block"></canvas>
          </div>
        </div>

        <p class="text-xs text-slate-500 mt-3 pt-3 border-t border-slate-100 leading-relaxed">
          <span v-if="currentStage === 1">Jumlah partikel atom Fe bertambah seiring peningkatan massa dan mol.</span>
          <span v-else-if="currentStage === 2">Pergerakan molekul pereaksi dan produk dalam wadah.</span>
          <span v-else-if="currentStage === 3">Atom Nitrogen (Biru) dan Hidrogen (Abu-abu).</span>
          <span v-else-if="currentStage === 4">Molekul H₂ (Biru), O₂ (Merah), dan H₂O (Ungu).</span>
          <span v-else-if="currentStage === 5">Kation Pb²⁺ dan anion I⁻ membentuk kisi endapan di dasar wadah.</span>
        </p>
      </div>

      <!-- WINDOW 3: SIMBOLIK & TUGAS E-LKPD -->
      <div class="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm flex flex-col justify-between min-h-[360px] space-y-4">
        <div>
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
            <span class="text-xs font-bold text-slate-900">3. Jendela Simbolik & Latihan</span>
            <span class="text-[11px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded-md">Rumus</span>
          </div>

          <!-- Formula Text Box -->
          <div class="bg-slate-50 border border-slate-200/80 rounded-xl p-2.5 text-center font-mono text-xs font-semibold text-slate-800 mb-3">
            <span v-if="currentStage === 1">n = m / Ar &nbsp;|&nbsp; N = n × 6.02 × 10²³</span>
            <span v-else-if="currentStage === 2">CaCO₃(s) + 2HCl(aq) → CaCl₂(aq) + H₂O(l) + CO₂(g)</span>
            <span v-else-if="currentStage === 3">{{ s3CoefA }}N₂ + {{ s3CoefB }}H₂ ⇌ {{ s3CoefC }}NH₃</span>
            <span v-else-if="currentStage === 4">2H₂ (g) + O₂ (g) → 2H₂O (g)</span>
            <span v-else-if="currentStage === 5">Pb(NO₃)₂ + 2KI → PbI₂↓ + 2KNO₃</span>
          </div>

          <!-- Interactive Controls -->
          <div class="space-y-3">
            <!-- Stage 1 -->
            <div v-if="currentStage === 1" class="space-y-1.5">
              <div class="flex justify-between text-xs text-slate-600 font-medium">
                <span>Massa Besi (Fe):</span>
                <span class="font-bold text-slate-900">{{ s1Mass }} Gram</span>
              </div>
              <input
                type="range"
                min="14"
                max="112"
                step="14"
                v-model.number="s1Mass"
                class="w-full accent-chemist-primary cursor-pointer"
              />
            </div>

            <!-- Stage 2 -->
            <div v-else-if="currentStage === 2" class="space-y-2">
              <label class="block text-xs text-slate-600 font-medium">Sistem Wadah Reaksi:</label>
              <select
                v-model="s2System"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 outline-none"
              >
                <option value="closed">Wadah Tertutup</option>
                <option value="open">Wadah Terbuka</option>
              </select>
              <button
                @click="runStage2"
                class="w-full py-2 bg-chemist-dark hover:bg-slate-900 rounded-xl text-xs font-semibold text-white transition-all shadow-2xs"
              >
                Jalankan Reaksi
              </button>
            </div>

            <!-- Stage 3 -->
            <div v-else-if="currentStage === 3" class="space-y-2">
              <label class="block text-xs text-slate-600 font-medium">Koefisien Reaksi:</label>
              <div class="grid grid-cols-3 gap-2">
                <div>
                  <label class="text-[10px] text-slate-400 block mb-1">Koef a(N₂)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    v-model.number="s3CoefA"
                    class="w-full bg-slate-50 border border-slate-200 rounded-lg p-1.5 text-xs text-center font-bold text-slate-800 outline-none"
                  />
                </div>
                <div>
                  <label class="text-[10px] text-slate-400 block mb-1">Koef b(H₂)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    v-model.number="s3CoefB"
                    class="w-full bg-slate-50 border border-slate-200 rounded-lg p-1.5 text-xs text-center font-bold text-slate-800 outline-none"
                  />
                </div>
                <div>
                  <label class="text-[10px] text-slate-400 block mb-1">Koef c(NH₃)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    v-model.number="s3CoefC"
                    class="w-full bg-slate-50 border border-slate-200 rounded-lg p-1.5 text-xs text-center font-bold text-slate-800 outline-none"
                  />
                </div>
              </div>
            </div>

            <!-- Stage 4 -->
            <div v-else-if="currentStage === 4" class="space-y-2">
              <div class="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <div class="flex justify-between text-slate-600 mb-1">
                    <span>H₂:</span>
                    <span class="font-bold text-slate-900">{{ s4H2 }} mol</span>
                  </div>
                  <input
                    type="range"
                    min="2"
                    max="10"
                    step="2"
                    v-model.number="s4H2"
                    class="w-full accent-chemist-primary cursor-pointer"
                  />
                </div>
                <div>
                  <div class="flex justify-between text-slate-600 mb-1">
                    <span>O₂:</span>
                    <span class="font-bold text-slate-900">{{ s4O2 }} mol</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    step="1"
                    v-model.number="s4O2"
                    class="w-full accent-chemist-primary cursor-pointer"
                  />
                </div>
              </div>

              <button
                @click="runStage4"
                class="w-full py-1.5 bg-chemist-dark hover:bg-slate-900 rounded-xl text-xs font-semibold text-white transition-all shadow-2xs"
              >
                Hitung Tabel M-R-S
              </button>

              <table v-if="s4HasRun" class="w-full text-[11px] text-center border-collapse mt-2 border border-slate-200 rounded-lg overflow-hidden">
                <thead class="bg-slate-50 text-slate-700">
                  <tr>
                    <th class="p-1 border border-slate-200">Tahap</th>
                    <th class="p-1 border border-slate-200">2H₂</th>
                    <th class="p-1 border border-slate-200">O₂</th>
                    <th class="p-1 border border-slate-200">2H₂O</th>
                  </tr>
                </thead>
                <tbody class="text-slate-600">
                  <tr>
                    <td class="p-1 border border-slate-200 font-medium">M</td>
                    <td class="p-1 border border-slate-200">{{ s4H2 }}</td>
                    <td class="p-1 border border-slate-200">{{ s4O2 }}</td>
                    <td class="p-1 border border-slate-200">0</td>
                  </tr>
                  <tr>
                    <td class="p-1 border border-slate-200 font-medium">R</td>
                    <td class="p-1 border border-slate-200">{{ s4Mrs.rH2 }}</td>
                    <td class="p-1 border border-slate-200">{{ s4Mrs.rO2 }}</td>
                    <td class="p-1 border border-slate-200">{{ s4Mrs.rH2O }}</td>
                  </tr>
                  <tr class="font-bold text-slate-900 bg-slate-50/50">
                    <td class="p-1 border border-slate-200">S</td>
                    <td class="p-1 border border-slate-200">{{ s4Mrs.sH2 }}</td>
                    <td class="p-1 border border-slate-200">{{ s4Mrs.sO2 }}</td>
                    <td class="p-1 border border-slate-200">{{ s4Mrs.sH2O }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Stage 5 -->
            <div v-else-if="currentStage === 5" class="space-y-2">
              <div class="flex justify-between text-xs text-slate-600 font-medium">
                <span>Volume KI (0.1 M):</span>
                <span class="font-bold text-slate-900">{{ s5Vol }} mL</span>
              </div>
              <input
                type="range"
                min="10"
                max="50"
                step="10"
                v-model.number="s5Vol"
                class="w-full accent-chemist-primary cursor-pointer"
              />
              <button
                @click="runStage5"
                class="w-full py-2 bg-chemist-dark hover:bg-slate-900 rounded-xl text-xs font-semibold text-white transition-all shadow-2xs"
              >
                Reaksikan Larutan
              </button>
            </div>
          </div>
        </div>

        <!-- Inquiry Question Section -->
        <div class="bg-slate-50 border border-slate-200/80 rounded-xl p-3.5 space-y-2">
          <div class="text-xs font-bold text-slate-800">
            Pertanyaan Siswa:
          </div>

          <p class="text-xs text-slate-600 leading-relaxed">
            <span v-if="currentStage === 1">
              Berapa jumlah mol (n) jika massa Fe = <b>{{ s1Mass }}</b> gram? (Ar Fe = 56)
            </span>
            <span v-else-if="currentStage === 2">
              Apakah massa sistem terukur tetap sama pada wadah terbuka?
            </span>
            <span v-else-if="currentStage === 3">
              Tentukan rasio koefisien bulat (a, b, c) agar reaksi amonia setara!
            </span>
            <span v-else-if="currentStage === 4">
              Dari kondisi mula-mula di atas, senyawa manakah yang menjadi <b>Pereaksi Pembatas</b>?
            </span>
            <span v-else-if="currentStage === 5">
              Hitung massa endapan teoritis PbI₂ (Mr=461) dari <b>{{ s5Vol }} mL</b> larutan KI 0.1 M!
            </span>
          </p>

          <div class="flex gap-2">
            <input
              v-if="currentStage === 1"
              type="number"
              step="0.01"
              v-model="s1Answer"
              placeholder="Nilai mol..."
              class="flex-1 bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 outline-none"
            />
            <select
              v-else-if="currentStage === 2"
              v-model="s2Answer"
              class="flex-1 bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-xs text-slate-800 outline-none"
            >
              <option value="">-- Pilih Jawaban --</option>
              <option value="false">Tidak, massa berkurang karena gas lepas</option>
              <option value="true">Ya, massa selalu tetap di segala wadah</option>
            </select>
            <div v-else-if="currentStage === 3" class="flex-1 text-xs text-slate-400 py-1">
              Atur koefisien a, b, c di atas lalu periksa.
            </div>
            <select
              v-else-if="currentStage === 4"
              v-model="s4Answer"
              class="flex-1 bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-xs text-slate-800 outline-none"
            >
              <option value="H2">Gas H₂</option>
              <option value="O2">Gas O₂</option>
            </select>
            <input
              v-else-if="currentStage === 5"
              type="number"
              step="0.001"
              v-model="s5Answer"
              placeholder="Massa (gram)..."
              class="flex-1 bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 outline-none"
            />

            <button
              @click="verifyAnswer"
              :disabled="verifying"
              class="px-3.5 py-1.5 bg-chemist-primary hover:bg-blue-600 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shrink-0"
            >
              <RefreshCw v-if="verifying" class="w-3.5 h-3.5 animate-spin" />
              <Check v-else class="w-3.5 h-3.5" />
              <span>Periksa</span>
            </button>
          </div>

          <!-- Feedback Banner -->
          <div
            v-if="verificationResult"
            :class="[
              'p-2.5 rounded-lg text-xs font-medium border flex items-start gap-2 mt-2 leading-relaxed',
              verificationResult.is_correct
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                : 'bg-rose-50 border-rose-200 text-rose-800'
            ]"
          >
            <CheckCircle2 v-if="verificationResult.is_correct" class="w-4 h-4 shrink-0 text-emerald-600 mt-0.5" />
            <AlertCircle v-else class="w-4 h-4 shrink-0 text-rose-600 mt-0.5" />
            <div>
              {{ verificationResult.explanation }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
