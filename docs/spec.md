# Glas Mail Sender

## Introduction

A mail sender application that allows a single user to send a template mail to multiple state entities. The user shall be able to send 1 template every 72 hours. The user shall provide identifiable information:
- Name
- Surname
- Personal email

None of this information shall be stored in raw format. Only the email is salted and stored as a hash to prevent abuse (spam). The user shall have to confirm the authenticity of his email by confirming via a link sent to the provided `personal mail`.

Once a user has sent a specific template, he shall not be able to repeat the operation.

## Features

### Frontend

>[!NOTE] The fronend shall be in Bulgarian. It shall not support any other languages.

The frontend only provides a from where the user provides the following information:
- Name
- Surname
- Personal email

And selects from 2 lists of predefined options:
- mail template
- target state entities

Each mail template shall be sent only to associated `state entities`. The user first selects the template. Upon template selection the backend delivers a filled in mail template. The user then confirms the received template. Upon clicking the `confirm` button, an input box appears awaiting a 6-digit validation number. The user receives an authentication mail with a 6-digit code. Upon entering a valid code, the the `Send` button becomes available and the user can send the mail.

A confirmation and a rewarding animation is provided to the user upon sending the mail.

#### Technical

The frontend shall be written in Vue.js.

#### Design

The frontend shall have a modern, clean, minimalist interface, use white as background color, and green and red as accents.

#### API

The frontend shall communicate the user-provided data to the backend via a `POST` request on a suitable backend endpoint.

The request shall be as follows

```json
{
    "name":"Ivan",
    "surname":"Draganov",
    "mail":"loshiq_manqk@gmail.com",
    "selected_template":1,
    "selected_entity":4
}
```

### Backend
#### Key features

##### Spam prevention

Prevents spam by logging a salted hash of user's email. A user can send only 1 `template` every 168 hours. A user can not send the same template twice at any point.

##### User verification

The application performs user verificatino by sending an OTP to the email the user provided.

##### Mail template

The application provides a list of mail `templates` that the user selects from.

##### Mail sending

Sends the mail via the mailtrap service.


#### Operational sequence

1. Accepts the name and surname from the frontend in order to construct a Sender header as {name}.{surname}@{domain_name}. 
2. Sends a filled in mail template with the user's details
3. Awaits confirmation from the user to send OTP
3. Sends OTP and awaits OTP confirmation
4. Upon succesful OTP verification - sends the completed mail template as per its associated `entities`
5. Sends a confirmation to the FE for a sucessfully sent mail
