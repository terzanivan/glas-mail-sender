<script setup lang="ts">
import type { Entity, MailForm } from '../../types/mail'

defineProps<{
  form: MailForm
  entities: Entity[]
  previewContent: string
  loading: boolean
  onBack: () => void
  onNext: () => void
}>()
</script>

<template>
  <div class="space-y-8 animate-in slide-in-from-right-4 duration-300">
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
      <button @click="onBack" class="flex-1 border-2 border-gray-100 text-gray-500 py-5 rounded-2xl font-bold hover:bg-gray-50 transition-all">
        Назад
      </button>
      <button @click="onNext" :disabled="!form.selected_entity || loading" class="flex-[2] bg-glas-green text-white py-5 px-8 rounded-2xl font-bold hover:opacity-90 transition-all transform hover:scale-[1.02] shadow-xl shadow-green-100 active:scale-[0.98]">
        Потвърди и получи код
      </button>
    </div>
  </div>
</template>
