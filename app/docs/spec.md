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

The backend manages the available `templates`, `entities` and stores the associations between them. It provides them to the frontend via http requests.

The backend holds a simple database where it can track the:
- `entity` - `template` association a specific user mail hash is associated with
- the timeout between consecutive requests for a particular user mail hash

The backend communicates with the selected mail service provider `Mailtrap` in order to send the requested templates to the requested entities.

The backend populates the `templates` with the provided userdata.

#### Operational sequence

1. User submits a completed form
2. Backend sends verification mail to user
3. Backend the prepares the user-requested template with relevant data and stores it
4. User confirms the verification within predefined time limit
5. Backend sends the prepared template to the relevant `entities`
6. Frontend receives confirmation that the process has started and informs the user
7. The user may not submit any additional requests for the next 72 hours and may never submit another request for the same `template`-`entity` combination

