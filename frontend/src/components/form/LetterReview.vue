<script setup lang="ts">
import { ref } from 'vue'
import { ChevronDown } from 'lucide-vue-next'
import type { Entity, MailForm } from '../../types/mail'

defineProps<{
  form: MailForm
  previewContent: string
	receivers: Entity[]
  loading: boolean
  onBack: () => void
  onNext: () => void
}>()

const showRecipients = ref(false)
</script>

<template>
  <div class="space-y-6 animate-in slide-in-from-right-4 duration-300">
		<div class="space-y-2">
			<button 
				@click="showRecipients = !showRecipients" 
				class="p-1 w-full justify-between flex flex-row flex-wrap bg-green-50 border-2 border-green-100 text-glas-green hover:bg-gray-100 rounded-lg transition-colors focus:outline-none"
				:aria-label="showRecipients ? 'Скрий получателите' : 'Виж всички получатели'"
			>
			<label class="text-sm font-bold text-gray-700">Получатели ({{ receivers.length }})</label>
				<ChevronDown 
					class="w-5 h-5 transition-transform duration-200" 
					:class="{ 'rotate-180': showRecipients }"
				/>
			</button>
      <div 
        v-if="showRecipients" 
        class="bg-gray-50 p-4 rounded-2xl border border-gray-100 overflow-y-auto animate-in fade-in slide-in-from-top-2 duration-200"
        style="max-height: 140px;"
      >
        <ul class="space-y-1">
          <li v-for="r in receivers" :key="r.id" class="text-xs md:text-sm text-gray-600 flex items-center gap-2">
            <label class="truncate border-2 bg-gray-100 border-gray-200 pl-2 pr-2 rounded-full">{{ r.email }}</label>
          </li>
        </ul>
      </div>
		</div>
    <div class="space-y-2">
      <label class="text-sm font-bold text-gray-700">Преглед на съдържанието</label>
      <div class="bg-gray-50 p-6 rounded-2xl border border-gray-100 text-sm md:text-base whitespace-pre-wrap leading-relaxed min-h-[250px] max-h-[400px] overflow-y-auto text-gray-600 relative">
        <div v-if="loading && !previewContent" class="absolute inset-0 flex items-center justify-center bg-gray-50/50 rounded-2xl">
          <span class="animate-spin text-2xl">⏳</span>
        </div>
        <template v-if="previewContent">
					<div v-html="previewContent"></div>
        </template>
        <div v-else-if="!loading" class="text-gray-400 italic text-center py-12">
          Грешка при генериране на прегледа.
        </div>
      </div>
    </div>

    <div class="flex flex-col md:flex-row gap-4">
      <button @click="onBack" class="flex-1 border-2 border-gray-100 text-gray-500 py-5 rounded-2xl font-bold hover:bg-gray-50 transition-all">
        Назад
      </button>
      <button @click="onNext" :disabled="loading" class="flex-[2] bg-glas-green text-white py-5 px-8 rounded-2xl font-bold hover:opacity-90 transition-all transform hover:scale-[1.02] shadow-xl shadow-green-100 active:scale-[0.98]">
        Потвърди и получи код
      </button>
    </div>
  </div>
</template>
