<script setup lang="ts">
import { User, Mail } from 'lucide-vue-next'
import type { Template, MailForm } from '../../types/mail'

defineProps<{
  form: MailForm
  templates: Template[]
  loading: boolean
  isProfileComplete: boolean
  mailValidationError: string
  onTemplateChange: () => void
  onConfirm: () => void
}>()
</script>

<template>
  <div class="space-y-8 animate-in slide-in-from-right-4 duration-300">
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
      <p v-if="mailValidationError" class="text-xs text-glas-red font-bold mt-1 px-2">{{ mailValidationError }}</p>
    </div>

    <div class="space-y-2">
      <label class="text-sm font-bold text-gray-700">Изберете тема</label>
      <select 
        v-model="form.selected_template" 
        @change="onTemplateChange" 
        :disabled="!isProfileComplete"
        class="w-full p-4 bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-glas-green outline-none appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <option value="" disabled>Изберете шаблон на писмо</option>
        <option v-for="t in templates" :key="t.id" :value="t.id">{{ t.name }}</option>
      </select>
    </div>

    <button 
      @click="onConfirm" 
      :disabled="!isProfileComplete || !form.selected_template || loading" 
      class="w-full bg-glas-green text-white py-5 rounded-2xl font-bold text-lg hover:opacity-90 transition-all transform hover:scale-[1.02] shadow-xl shadow-green-100 mt-6 active:scale-[0.98] disabled:opacity-50 disabled:scale-100 disabled:shadow-none"
    >
      Продължи
    </button>
  </div>
</template>
