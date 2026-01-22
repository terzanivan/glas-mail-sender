# Glas Backend Spec

## Introduction
Written in Python. Dependency management by poetry. Mailtrap and Pocketbase as main dependencies.

The backend manages the available `templates`, `entities` and stores the associations between them. It provides them to the frontend via http requests.

## Business Rules
- **Global Rate Limit:** 1 send per 168 hours per `mail_hash`.
- **Deduplication:** A `mail_hash` cannot use the same `sent_template_id` twice.
- **OTP Expiry:** Codes are valid for 10 minutes.
- **Client Fingerprinting:** To prevent "one machine, many emails" spam, use the `X-Forwarded-For` IP or a custom browser fingerprint hash stored temporarily in Memory alongside the `mail_hash`.

## Model

1. user_sent_template
    ```yaml
    mail_hash:
        type: string
        constraint: unique_key
        desc: a salted hash of the mail the user provided
    sent_template_id:
        type: string
        constraint: foreign_key
        desc: the template that the user has sent
    template_sent_timestamp:
        type: date
        constraint: none
        desc: the moment at which the user's mail request was approved and sent
    auth_id:
        type: int
        constraint: foreign_key
        desc: the authentication id for the user
    ```
2. Template
    ```yaml
    id:
        type: string
        constraint: unique_key
        desc: a uuid of the template
    content:
        type: string
        constraint: none
        desc: the text content of the template
    target_entities:
        type: string
        constraint: foreign_key
        desc: the entities related to this template
    ```
3. Entity
    ```yaml
    id:
        type: string
        constraint: unique_key
        desc: a uuid of the entity
    email:
        type: email
        constraint: unique
        desc: a json object containing contact information
    name:
        type: string
        constraint: none
        desc: the name of the entity
    ent_type:
        type: enum
        constraint: none
        desc: the type of entity
        enum_values:
            - commission
            - mp
            - company
            - government_entity
    ```
4. Auth
    ```yaml
    id: 
        type: int
        constraint: unique_key
        desc: a numerical uuid of the user auth sequence
    state:
        type: enum
        constraint: none
        desc: the state of the authentication process
        enum_values:
            - sent
            - success
            - failed
            - expired
    expiry:
        type: datetime
        constraint: none
        desc: the expiry datetime of the authentication sequence
    code:
        type: int
        constraint: none
        desc: the 6-digit code that the application sent for user mail authentication
    ```
### Components

1. Authenticator
    Requirements:
        - manage the expiry of sent authentication codes
        - validate authentication codes
        - generate authentication codes


2. Template Manager
    Requirements:
        - Fetch templates from Pocketbase.
        - Filter associated entities based on the template's `target_entities` relation.
        - Handle string interpolation for the mail body.

3. Mail Sender
    Requirements:
        - Construct "Reply-To" header as `"{name}.{surname}@yourdomain.com"`.
        - Connect to Mailtrap SMTP.
        - Async execution (recommended) to avoid blocking the API response.

4. Server (Spam Prevention)
    Requirements:
        - Middleware to check IP-based request frequency.
        - Salt for `mail_hash` must be pulled from environment variables.

    3.1. Endpoints:
      GET /templates: Returns list of available templates.
      GET /templates/{id}/preview: Returns the content with placeholders.
      POST /request-otp: 
        Payload: { name, surname, mail, template_id, entity_id }
        Logic: Hash mail, check SentLog for rate limits, trigger Authenticator.
      POST /verify-and-send:
        Payload: { mail, otp_code }
        Logic: If Authenticator success -> trigger Mail Sender -> update SentLog.
