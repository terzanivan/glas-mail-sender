import client from './client'
import type { Template, MailForm } from '../types/mail'

export const mailService = {
  async getTemplates() {
    const res = await client.get<Template[]>('/templates')
    return res.data
  },

  async getPreview(templateId: string, name: string, surname: string) {
    const res = await client.get<{ content: string }>(`/templates/${templateId}/preview`, {
      params: { name, surname }
    })
    return res.data
  },

  async requestOTP(form: Omit<MailForm, 'otp'>) {
    await client.post('/request-otp', {
      name: form.name,
      surname: form.surname,
      mail: form.mail,
      template_id: form.selected_template,
      entity_id: form.selected_entity
    })
  },

  async verifyAndSend(form: MailForm) {
    await client.post('/verify-and-send', {
      mail: form.mail,
      otp_code: parseInt(form.otp),
      name: form.name,
      surname: form.surname,
      template_id: form.selected_template,
      entity_id: form.selected_entity
    })
  }
}
