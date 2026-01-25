export interface Entity {
	id: string
	name: string
	email: string
}

export interface Template {
	id: string
	content: string
	name: string
	expand?: {
		target_entities?: Entity[]
	}
}

export interface MailForm {
	name: string
	surname: string
	mail: string
	selected_template: string
	selected_entity: string
	otp: string
}
