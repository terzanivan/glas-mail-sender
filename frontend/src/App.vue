<script setup lang="ts">
import { useMailForm } from './composables/useMailForm'
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

    <main class="w-full max-w-2xl bg-white border border-gray-100 rounded-3xl shadow-xl shadow-gray-100 p-6 md:p-12 transition-all">
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
          :entities="entities"
          :preview-content="previewContent"
          :loading="loading"
          :on-back="() => step = 1"
          :on-next="requestOTP"
        />

        <VerificationForm
          v-if="step === 3"
          :form="form"
          :loading="loading"
          :is-email-valid="isEmailValid"
          :on-back="() => step = 2"
          :on-verify="verifyAndSend"
        />

        <ErrorMessage :message="error" />
      </template>
    </main>
    
    <AppFooter />
  </div>
</template>
