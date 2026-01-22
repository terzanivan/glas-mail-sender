<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Send, CheckCircle, Mail, User, ShieldCheck } from 'lucide-vue-next'
import confetti from 'canvas-confetti'

// Types
interface Template {
  id: string
  content: string
  expand?: {
    target_entities?: Entity[]
  }
}

interface Entity {
  id: string
  name: string
  email: string
}

// State
const step = ref(1)
const loading = ref(false)
const error = ref('')
const success = ref(false)

const form = ref({
  name: '',
  surname: '',
  mail: '',
  selected_template: '',
  selected_entity: '',
  otp: ''
})

const templates = ref<Template[]>([])
const entities = ref<Entity[]>([])
const previewContent = ref('')

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// Lifecycle
onMounted(async () => {
  try {
    const res = await api.get('/templates')
    templates.value = res.data
  } catch (err) {
    error.value = 'Грешка при зареждане на шаблони.'
  }
})

// Actions
const onTemplateChange = async () => {
  if (!form.value.selected_template) return
  
  try {
    loading.value = true
    // Get preview
    const res = await api.get(`/templates/${form.value.selected_template}/preview`, {
      params: { name: form.value.name, surname: form.value.surname }
    })
    previewContent.value = res.data.content
    
    // Fetch associated entities
    const t = templates.value.find(x => x.id === form.value.selected_template)
    if (t && t.expand && t.expand.target_entities) {
        entities.value = t.expand.target_entities
    } else {
        entities.value = []
    }
  } catch (err) {
    error.value = 'Грешка при зареждане на детайли.'
  } finally {
    loading.value = false
  }
}

const confirmDetails = () => {
  if (!form.value.name || !form.value.surname || !form.value.mail || !form.value.selected_template) {
    error.value = 'Моля попълнете всички полета.'
    return
  }
  step.value = 2
}

const requestOTP = async () => {
  try {
    loading.value = true
    error.value = ''
    await api.post('/request-otp', {
      name: form.value.name,
      surname: form.value.surname,
      mail: form.value.mail,
      template_id: form.value.selected_template,
      entity_id: form.value.selected_entity
    })
    step.value = 3
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Грешка при изпращане на OTP.'
  } finally {
    loading.value = false
  }
}

const verifyAndSend = async () => {
  try {
    loading.value = true
    error.value = ''
    await api.post('/verify-and-send', {
      mail: form.value.mail,
      otp_code: parseInt(form.value.otp),
      name: form.value.name,
      surname: form.value.surname,
      template_id: form.value.selected_template,
      entity_id: form.value.selected_entity
    })
    success.value = true
    confetti({
      particleCount: 150,
      spread: 70,
      origin: { y: 0.6 }
    })
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Невалиден код или грешка при изпращане.'
  } finally {
    loading.value = false
  }
}

const reset = () => {
  step.value = 1
  success.value = false
  form.value.otp = ''
  error.value = ''
}
</script>

<template>
  <div class="min-h-screen bg-white text-gray-900 font-sans p-4 md:p-8 flex flex-col items-center">
    <header class="mb-12 text-center">
      <h1 class="text-4xl font-extrabold text-gray-900 mb-2 tracking-tight">GLAS</h1>
      <p class="text-gray-500 font-medium">Изпратете писмо до държавните институции</p>
    </header>

    <main class="w-full max-w-2xl bg-white border border-gray-100 rounded-3xl shadow-xl shadow-gray-100 p-6 md:p-12 transition-all">
      
      <div v-if="success" class="text-center py-12 animate-in fade-in zoom-in duration-500">
        <div class="w-24 h-24 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-8">
          <CheckCircle class="w-16 h-16 text-glas-green" />
        </div>
        <h2 class="text-3xl font-bold mb-4 tracking-tight">Писмото е изпратено успешно!</h2>
        <p class="text-gray-600 mb-10 text-lg leading-relaxed">Благодарим ви за вашата активна гражданска позиция.</p>
        <button @click="reset" class="bg-gray-900 text-white px-10 py-4 rounded-2xl font-bold hover:bg-black transition-all transform hover:scale-105 shadow-xl shadow-gray-200">
          Ново писмо
        </button>
      </div>

      <div v-else>
        <!-- Step 1: Info & Template -->
        <div v-if="step === 1" class="space-y-8 animate-in slide-in-from-right-4 duration-300">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-2">
              <label class="text-sm font-bold text-gray-700 flex items-center gap-2">
                <User class="w-4 h-4 text-gray-400" /> Име
              </label>
              <input v-model="form.name" type="text" placeholder="Иван" class="w-full p-4 bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-glas-green outline-none transition-all" />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-bold text-gray-700 flex items-center gap-2">
                <User class="w-4 h-4 text-gray-400" /> Фамилия
              </label>
              <input v-model="form.surname" type="text" placeholder="Иванов" class="w-full p-4 bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-glas-green outline-none transition-all" />
            </div>
          </div>
          
          <div class="space-y-2">
            <label class="text-sm font-bold text-gray-700 flex items-center gap-2">
              <Mail class="w-4 h-4 text-gray-400" /> Личен Имейл
            </label>
            <input v-model="form.mail" type="email" placeholder="ivan@example.com" class="w-full p-4 bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-glas-green outline-none transition-all" />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-bold text-gray-700">Изберете тема</label>
            <select v-model="form.selected_template" @change="onTemplateChange" class="w-full p-4 bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-glas-green outline-none appearance-none cursor-pointer">
              <option value="" disabled>Изберете шаблон на писмо</option>
              <option v-for="t in templates" :key="t.id" :value="t.id">Шаблон: {{ t.id }}</option>
            </select>
          </div>

          <button @click="confirmDetails" :disabled="loading" class="w-full bg-glas-green text-white py-5 rounded-2xl font-bold text-lg hover:opacity-90 transition-all transform hover:scale-[1.02] shadow-xl shadow-green-100 mt-6 active:scale-[0.98]">
            Продължи
          </button>
        </div>

        <!-- Step 2: Entity & Preview -->
        <div v-if="step === 2" class="space-y-8 animate-in slide-in-from-right-4 duration-300">
          <div class="space-y-2">
            <label class="text-sm font-bold text-gray-700">Получател</label>
            <select v-model="form.selected_entity" class="w-full p-4 bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-glas-green outline-none appearance-none cursor-pointer">
              <option value="" disabled>Изберете държавна институция</option>
              <option v-for="e in entities" :key="e.id" :value="e.id">{{ e.name }}</option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-bold text-gray-700">Преглед на съдържанието</label>
            <div class="bg-gray-50 p-6 rounded-2xl border border-gray-100 text-sm md:text-base whitespace-pre-wrap leading-relaxed min-h-[250px] max-h-[400px] overflow-y-auto text-gray-600">
              {{ previewContent }}
            </div>
          </div>

          <div class="flex flex-col md:flex-row gap-4">
            <button @click="step = 1" class="flex-1 border-2 border-gray-100 text-gray-500 py-5 rounded-2xl font-bold hover:bg-gray-50 transition-all">
              Назад
            </button>
            <button @click="requestOTP" :disabled="!form.selected_entity || loading" class="flex-[2] bg-glas-green text-white py-5 px-8 rounded-2xl font-bold hover:opacity-90 transition-all transform hover:scale-[1.02] shadow-xl shadow-green-100 active:scale-[0.98]">
              Потвърди и получи код
            </button>
          </div>
        </div>

        <!-- Step 3: OTP -->
        <div v-if="step === 3" class="space-y-10 text-center animate-in slide-in-from-right-4 duration-300">
          <div class="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-2">
            <ShieldCheck class="w-12 h-12 text-blue-500" />
          </div>
          <div>
            <h3 class="text-2xl font-bold tracking-tight">Потвърдете вашия имейл</h3>
            <p class="text-gray-500 mt-2">Изпратихме 6-цифрен код за потвърждение на<br/><span class="font-bold text-gray-900">{{ form.mail }}</span></p>
          </div>
          
          <input v-model="form.otp" type="text" maxlength="6" placeholder="000000" class="w-full max-w-[280px] mx-auto text-center text-5xl tracking-[0.2em] p-6 bg-gray-50 border-none rounded-3xl focus:ring-2 focus:ring-glas-green outline-none font-mono font-bold" />

          <div class="flex flex-col gap-4">
            <button @click="verifyAndSend" :disabled="form.otp.length < 6 || loading" class="w-full bg-glas-green text-white py-5 rounded-2xl font-bold text-xl hover:opacity-90 transition-all transform hover:scale-[1.02] shadow-xl shadow-green-100 active:scale-[0.98]">
              <div v-if="loading" class="flex items-center justify-center gap-3">
                <span class="animate-spin text-2xl">⏳</span> Обработка...
              </div>
              <div v-else class="flex items-center justify-center gap-3">
                <Send class="w-6 h-6" /> Изпрати писмото
              </div>
            </button>
            <button @click="step = 2" class="text-sm font-bold text-gray-400 hover:text-glas-red transition-all">
              Промяна на данните за изпращане
            </button>
          </div>
        </div>

        <div v-if="error" class="mt-8 p-4 bg-red-50 text-glas-red rounded-2xl text-sm font-bold border border-red-100 flex items-center justify-center gap-2 animate-in shake duration-300">
           {{ error }}
        </div>
      </div>
    </main>
    
    <footer class="mt-auto py-8 text-gray-400 text-sm">
      © 2026 GLAS Project. Всички права запазени.
    </footer>
  </div>
</template>

<style>
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-white antialiased;
  }
}

.animate-in {
  animation-duration: 0.5s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.shake {
  animation: shake 0.3s ease-in-out;
}
</style>
