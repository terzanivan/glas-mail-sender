<script setup lang="ts">
import { CheckCircle } from 'lucide-vue-next'

defineProps<{
  onReset: () => void
}>()
</script>

<template>
  <div class="text-center py-12 animate-in fade-in zoom-in duration-500">
    <div class="w-24 h-24 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-8">
      <CheckCircle class="w-16 h-16 text-glas-green" />
    </div>
    <h2 class="text-3xl font-bold mb-4 tracking-tight">Писмото е изпратено успешно!</h2>
    <p class="text-gray-600 mb-10 text-lg leading-relaxed">Благодарим ви за вашата активна гражданска позиция.</p>
    <button @click="onReset" class="bg-gray-900 text-white px-10 py-4 rounded-2xl font-bold hover:bg-black transition-all transform hover:scale-105 shadow-xl shadow-gray-200">
      Ново писмо
    </button>
  </div>
</template>
