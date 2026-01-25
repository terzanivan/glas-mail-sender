import { ref, onMounted, computed, watch } from 'vue'
import confetti from 'canvas-confetti'
import { mailService } from '../api/mailService'
import type { Template, Entity, MailForm } from '../types/mail'

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function useMailForm() {
	const step = ref(1)
	const loading = ref(false)
	const error = ref('')
	const mailValidationError = ref('')
	const success = ref(false)
	const previewContent = ref('')

	const templates = ref<Template[]>([])
	const entities = ref<Entity[]>([])

	const form = ref<MailForm>({
		name: '',
		surname: '',
		mail: '',
		selected_template: '',
		selected_entity: '',
		otp: ''
	})

	// Computed states for validation
	const isEmailValid = computed(() => EMAIL_REGEX.test(form.value.mail))
	const isProfileComplete = computed(() =>
		form.value.name.trim().length >= 2 &&
		form.value.surname.trim().length >= 2 &&
		isEmailValid.value
	)

	// Debounced email validation
	let debounceTimer: ReturnType<typeof setTimeout>
	watch(() => form.value.mail, (newVal) => {
		clearTimeout(debounceTimer)
		if (!newVal) {
			mailValidationError.value = ''
			return
		}
		debounceTimer = setTimeout(() => {
			mailValidationError.value = isEmailValid.value ? '' : 'Моля, въведете валиден имейл адрес.'
		}, 1000)
	})

	// Watch for profile changes to refresh preview if template is already selected
	watch([() => form.value.name, () => form.value.surname], () => {
		if (form.value.selected_template && isProfileComplete.value) {
			onTemplateChange()
		}
	})

	const fetchTemplates = async () => {
		try {
			templates.value = await mailService.getTemplates()
		} catch (err) {
			error.value = 'Грешка при зареждане на шаблони.'
		}
	}

	const onTemplateChange = async () => {
		if (!form.value.selected_template) return

		try {
			loading.value = true
			error.value = ''

			const res = await mailService.getPreview(
				form.value.selected_template,
				form.value.name,
				form.value.surname
			)
			previewContent.value = res.content

			const t = templates.value.find(x => x.name === form.value.selected_template)
			entities.value = t?.expand?.target_entities || []
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
		error.value = ''
		step.value = 2
	}

	const requestOTP = async () => {
		try {
			loading.value = true
			error.value = ''
			await mailService.requestOTP(form.value)
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
			await mailService.verifyAndSend(form.value)
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
		form.value.selected_template = ''
		form.value.selected_entity = ''
		previewContent.value = ''
	}

	onMounted(fetchTemplates)

	return {
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
		isEmailValid,
		isProfileComplete,
		mailValidationError
	}
}
