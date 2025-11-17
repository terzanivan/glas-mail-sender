# Glas Mail Sender

## Introduction

A mail sender application that allows a single user to send a template mail to multiple state entities. The user shall be able to send 1 template every 72 hours. The user shall provide identifiable information:
- Name
- Surname
- Personal email

None of this information shall be stored in raw format. Only the email is stored as a hash to prevent abuse (spam). The user shall have to confirm the authenticity of his email by confirming via a link sent to the provided `personal mail`.

Once a user has sent a specific template to a specific state `entity` he shall not be able to repeat the operation.

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

Each mail template shall be sent only to associated `state entities`. The user first selects the template and afterwards the `entities`. The associations between the `entities` and the templates are predefined in the app's database and the user shall have no control over them.

After the entire form has been filled a `Send` button becomes available. Upon clicking it, the user starts the verification process of his `personal mail`. 

Once the user completes the `personal mail` verification process and the backend has successfully started sending email to the required `entities`, the frontend shall display a confirmation that the selected `template` has been sent to the requested `entities`

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

Written in python. Dependency management by poetry. Mailtrap and PostgreSQL as main dependencies.

The backend manages the available `templates`, `entities` and stores the associations between them. It provides them to the frontend via http requests.

The backend holds a simple database where it can track the:
- `entity` - `template` association a specific user mail hash is associated with
- the time between consecutive requests for a particular user mail hash (one request per 72 hours)

The backend communicates with the selected mail service provider `Mailtrap` in order to send the requested templates to the requested entities.

The backend populates the `templates` with the provided userdata.

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


#### Operational sequence

1. Accepts the name and surname from the frontend in order to construct a Sender header as {name}.{surname}@glasnarodeneu.bg. Uses the `mail-address` from the frontend as a `Reply-To` header in the email. Guaranteeing the `entity` would respond to the mail the user verified.
2. Sends a verification mail to the user
3. Constructs a mail from the selected template
4. Stores the constructed mail.
5. Awaits the user's verification
6. Upon receiving verification sends the user-requested mail to the entities
7. Updates the frontend to inform the user that the mail has been sent and that he now has to wait for 72 hours before he can send a different template
