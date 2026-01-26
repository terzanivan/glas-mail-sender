// TODO: Configure the entity enum
enum EntityType {
	MP,
	Commission,
	GovernmentEntity,
	Company
}

export interface Entity {
	id: string
	name: string
	email: string
	type: EntityType
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
