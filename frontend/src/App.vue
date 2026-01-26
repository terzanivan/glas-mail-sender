<script setup lang="ts">
import { useMailForm } from './composables/useMailForm'
import { ShieldCheck, Signature } from 'lucide-vue-next'
import AppHeader from './components/layout/AppHeader.vue'
import AppFooter from './components/layout/AppFooter.vue'
import ErrorMessage from './components/feedback/ErrorMessage.vue'
import SuccessState from './components/feedback/SuccessState.vue'
import SenderForm from './components/form/SenderForm.vue'
import LetterReview from './components/form/LetterReview.vue'
import VerificationForm from './components/form/VerificationForm.vue'

const {
  step,
  loading,
  error,
  success,
  form,
  templates,
  entities,
  previewContent,
  onTemplateChange,
  confirmDetails,
  requestOTP,
  verifyAndSend,
  reset,
  isProfileComplete,
  mailValidationError
} = useMailForm()
</script>

<template>
  <div class="min-h-screen bg-white text-gray-900 font-sans p-4 md:p-8 flex flex-col items-center">
    <AppHeader />
    
    <div class="flex flex-col lg:flex-row gap-8 items-start max-w-5xl w-full mt-4 md:mt-8">
      <main class="w-full lg:max-w-2xl bg-white border border-gray-100 rounded-3xl shadow-xl shadow-gray-100 p-6 md:p-12 transition-all">
        <SuccessState v-if="success" :on-reset="reset" />
  
        <template v-else>
          <SenderForm 
            v-if="step === 1"
            :form="form"
            :templates="templates"
            :loading="loading"
            :is-profile-complete="isProfileComplete"
            :mail-validation-error="mailValidationError"
            :on-template-change="onTemplateChange"
            :on-confirm="confirmDetails"
          />
  
          <LetterReview
            v-if="step === 2"
            :form="form"
            :receivers="entities"
            :preview-content="previewContent"
            :loading="loading"
            :on-back="() => step = 1"
            :on-next="requestOTP"
          />
  
          <VerificationForm
            v-if="step === 3"
            :form="form"
            :loading="loading"
            :on-back="() => step = 2"
            :on-verify="verifyAndSend"
          />
  
          <ErrorMessage :message="error" />
        </template>
      </main>

			<div class="flex flex-col space-y-2">
				<aside class="w-full lg:w-80 bg-gray-50 border-2 border-glas-black rounded-3xl p-4 md:p-6 sticky top-8">
					<div class="flex items-center gap-3 mb-4 text-slate-500">
						<Signature class="w-6 h-6" />
						<h3 class="font-bold">Твоят начин да се изразиш</h3>
					</div>
					<p class="text-sm text-gray-600 leading-relaxed">
						Glas дава възможност да дадеш гражданско становище директно на народни представители или държавни институции
					</p>
					<ol class="text-sm text-gray-600 leading-relaxed">
						<li>1. Въведи име и фамилия</li>
						<li>2. Въведи своя мейл</li>
						<li>3. Избери шаблон</li>
						<li>4. Продължи нататък</li>
					</ol>
				</aside>

				<aside class="w-full lg:w-80 bg-gray-50 border-2 border-glas-black rounded-3xl p-4 md:p-6 sticky top-8">
					<div class="flex items-center gap-3 mb-4 text-glas-green">
						<ShieldCheck class="w-6 h-6" />
						<h3 class="font-bold">Поверителност</h3>
					</div>
					<p class="text-sm text-gray-600 leading-relaxed">
						Приложението не съхранява лични данни на потребителите. Съхранява се единствено цифров отпечатък (fingerprint), който не е свързан с Вашата самоличност. Целта на този отпечатък е единствено предотвратяването на недобросъвестни спам действия.
					</p>
				</aside>
			</div>
    </div>
    
    <AppFooter />
  </div>
</template>
