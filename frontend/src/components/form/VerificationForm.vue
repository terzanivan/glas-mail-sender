<script setup lang="ts">
import { Send, ShieldCheck } from 'lucide-vue-next'
import type { MailForm } from '../../types/mail'

defineProps<{
  form: MailForm
  loading: boolean
  onBack: () => void
  onVerify: () => void
}>()
</script>

<template>
  <div class="space-y-10 text-center animate-in slide-in-from-right-4 duration-300">
    <div class="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-2">
      <ShieldCheck class="w-12 h-12 text-blue-500" />
    </div>
    <div>
      <h3 class="text-2xl font-bold tracking-tight">Потвърдете вашия имейл</h3>
      <p class="text-gray-500 mt-2">Изпратихме 6-цифрен код за потвърждение на<br/><span class="font-bold text-gray-900">{{ form.mail }}</span></p>
    </div>
    
    <input v-model="form.otp" type="text" maxlength="6" placeholder="000000" class="w-full max-w-[280px] mx-auto text-center text-5xl tracking-[0.2em] p-6 bg-gray-50 border-none rounded-3xl focus:ring-2 focus:ring-glas-green outline-none font-mono font-bold" />

    <div class="flex flex-col gap-4">
      <button @click="onVerify" :disabled="form.otp.length < 6 || loading" class="w-full bg-glas-green text-white py-5 rounded-2xl font-bold text-xl hover:opacity-90 transition-all transform hover:scale-[1.02] shadow-xl shadow-green-100 active:scale-[0.98]">
        <div v-if="loading" class="flex items-center justify-center gap-3">
          <span class="animate-spin text-2xl">⏳</span> Обработка...
        </div>
        <div v-else class="flex items-center justify-center gap-3">
          <Send class="w-6 h-6" /> Изпрати писмото
        </div>
      </button>
      <button @click="onBack" class="text-sm font-bold text-gray-400 hover:text-glas-red transition-all">
        Промяна на данните за изпращане
      </button>
    </div>
  </div>
</template>
