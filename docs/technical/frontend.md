Glas Frontend Spec (Vue.js)

Design & Localization

- Language: Strictly Bulgarian (BG).

- UI: Minimalist, white background.

- Accents: Green (success/confirm), Red (error/cancel).

User Flow

1. Selection: User enters Name, Surname, Email. Selects Template from dropdown.

2. Entity Selection: Displays entities associated with the selected template.

3. Preview: Backend returns the filled-in template; user clicks "Confirm".

4. OTP Step: 6-digit input appears. User enters code received via email.

5. Dispatch: On valid OTP, "Send" button is enabled.

6. Reward: On success, trigger a "Rewarding Animation" (e.g., confetti or checkmark).
