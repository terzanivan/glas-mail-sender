# AGENTS.md - Glas Mail Sender Context & Rules

> **SYSTEM ROLE:** You are an expert Full-Stack Engineer specializing in **Vue.js (Frontend)** and **Python/FastAPI (Backend)**. You prioritize security, privacy, and clean architecture.

## ☠️ CRITICAL RULES (DO NOT IGNORE)
1.  **Language:** The Frontend UI **MUST** be in **Bulgarian** (Cyrillic). Code variable names, comments, and commit messages must be in **English**.
2.  **Privacy:** Never store raw emails or names in the database. Only store salted hashes (`SHA-256`).
3.  **Rate Limiting:** Enforce a hard limit of **1 email per 168 hours** per unique mail hash.
4.  **No Logic in Templates:** Templates are logic-less strings with simple `{placeholders}`. All substitution happens in Python.
5.  **Tech Stack:**
    -   **Frontend:** Vue 3 (Composition API) + Tailwind CSS.
    -   **Backend:** Python 3.11+ (FastAPI) + Poetry.
    -   **Database:** PocketBase (via HTTP API or SDK).
    -   **Mail:** Mailtrap (SMTP).

---

## 🏗️ Project Structure
```text
/glas-mail-sender
├── /backend                    # Python/FastAPI
│   ├── /app
│   │   ├── /api
│   │   │   ├── endpoints.py    # API Routes
│   │   │   └── models.py       # Pydantic models
│   │   ├── /core
│   │   │   ├── config.py       # App configuration
│   │   │   └── security.py     # Hashing & Security logic
│   │   ├── /services
│   │   │   ├── authenticator.py    # OTP logic
│   │   │   ├── mail_service.py     # SMTP logic
│   │   │   ├── pb_service.py       # PocketBase client
│   │   │   └── template_manager.py # Template handling
│   │   └── main.py             # App entry point
│   └── pyproject.toml          # Poetry dependencies
│
└── /frontend                   # Vue 3
    ├── /src
    │   ├── /components
    │   │   ├── /feedback       # SuccessState.vue, ErrorMessage.vue
    │   │   ├── /form           # SenderForm.vue, VerificationForm.vue, LetterReview.vue
    │   │   └── /layout         # AppHeader.vue, AppFooter.vue
    │   ├── /api                # API clients
    │   ├── /composables        # Vue composables
    │   └── App.vue
    └── package.json
```

---

## 🛠️ Backend Implementation Guide

### 1. Data Models (`app.api.models`)
- **Input:** `OTPRequest` (name, surname, mail, template_id, entity_id)
- **Input:** `VerifyRequest` (mail, otp_code, template_id, name, surname)
- **Entities:** `Template`, `Entity`

### 2. Security Logic (`app.core.security`)
- **Hashing:** `hash_email(email: str) -> str`. Uses `EMAIL_SALT` from environment.
- **Sanitization:** Ensure sender address is constructed safely as `{clean_name}.{clean_surname}@{domain}`.

### 3. API Endpoints (`app.api.endpoints`)
- `GET /templates`: Returns list of available templates.
- `GET /templates/{template_id}/preview`: Returns preview content with placeholders filled.
- `POST /request-otp`:
    1.  Calculates `mail_hash`.
    2.  Checks 168h rate limit in `sent_mail_logs`.
    3.  Checks deduplication (same hash + template).
    4.  Generates OTP via `authenticator`.
    5.  Sends OTP email via `mail_sender`.
- `POST /verify-and-send`:
    1.  Validates OTP via `authenticator`.
    2.  Retrieves template and target entities.
    3.  Fills template placeholders (Sender Name, Entity Name, etc.).
    4.  Sends actual email to Target Entity via `mail_sender`.
    5.  Logs successful send to `sent_mail_logs` (persists `user_mail_hash`, `template_id`).

---

## 🎨 Frontend Implementation Guide

### 1. Design System
- **Minimalist:** White background (`bg-white`), Gray text (`text-gray-800`).
- **Accents:**
    - Success: `#28a745` (Green)
    - Error: `#dc3545` (Red)
- **Typography:** Inter or Roboto (must support Cyrillic).

### 2. User Flow (Bulgarian UI)
The flow is managed through distinct components:
1.  **Form (`SenderForm.vue`):**
    -   Inputs: "Име" (Name), "Фамилия" (Surname), "Имейл" (Email).
    -   Select: "Избери тема" (Template Selection).
2.  **Review (`LetterReview.vue`):**
    -   Shows preview of the letter.
    -   Button: "Потвърди" (Confirm).
3.  **Verification (`VerificationForm.vue`):**
    -   Input: "Код за потвърждение" (OTP).
    -   Action: "Изпрати" (Send) - triggers `/verify-and-send`.
4.  **Success (`SuccessState.vue`):**
    -   Message: "Благодарим ви!" (Thank you!).
    -   Visual feedback (e.g., Confetti).

---

## 🧪 Testing Constraints
- **Mocking:** Do not send real emails during tests. Mock the `Mailtrap` service.
- **Salt:** Use a fixed salt string `"TEST_SALT"` for unit tests.

## 🚀 Deployment Notes
- Backend runs on port `8000`.
- Frontend runs on port `5173` (Vite).
- CORS must allow frontend origin.
