# Glas Naroden Mail Sender

## Introduction

A web app that allows users to send mail templates to a range of government-associated email addresses. While the specification is in English, the app is entirely in Bulgarian.

## Specification

### Frontend

A simple Vue.js app that provides a form which requires:
- Name
- Surname
- Mail address (for receiving a verification mail, and a response from the institutions)
- A selector for predefined mail templates
- A selector for `entities` to which the `templates` can be sent

Not all `templates` can be sent to all `entities`. The user first selects a template and then selects the available entities for that template.

All fields are mandatory. Once all the data is filled in, the `Send` button becomes active and the user can press it.

On button press the following data is sent to the backend:
```json
{
    "name":"Ivan",
    "surname":"Draganov",
    "mail":"loshiq_ivan@gmail.com",
    "selection_template":"1",
    "selection_entity":"2,3"
}
```
### Backend

#### Key features

##### Spam prevention

Prevents spam by logging a hash of user's email the hash is deleted after 72 hours and that user can send a mail to another entity. The same user *can not* send *the same template to the same entities* ever again.

##### User verification

Verifies the `mail` address prior to sending the requested `templates` to the `entities`. 

Verification is done by: storing the provided mail address as a hash signed with the app's key and sending a mail with a verification link containing the signed hash.


##### Mail template

Provides a list of mail templates associate with certain entities. The user can select the template and the entity.

##### Mail sending

Sends the mail via the mailtrap service.

#### Operation

Written in python. Dependency management by `poetry`. `Mailtrap` and `PostgreSQL` as main dependencies.

##### Sequence
1. Accepts the `name` and `surname` from the frontend in order to construct a `Sender` header as `{name}.{surname}@glasnarodeneu.bg`. Uses the `mail-address` from the frontend as a `Reply-To` header in the email.
2. Sends a verification mail to the user
3. Constructs a mail from the selected `template`
4. Stores the constructed mail.
5. Awaits the user's verification
6. Upon receiving verification sends the user-requested mail to the `entities`
7. Updates the frontend to inform the user that the mail has been sent and that he now has to wait for 72 hours before he can send a different template


> [!NOTE]
> The application not store *any identifiable* data.

