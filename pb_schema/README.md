# Pocketbase Collections Setup

Create the following collections in your Pocketbase admin panel (http://localhost:8090/_/):

### 1. entities
- **name**: `text` (Required)
- **email**: `email` (Required, Unique)
- **ent_type**: `select` (commission, mp, company, government_entity)

### 2. templates
- **content**: `text` (Required)
- **target_entities**: `relation` (Multiple, Collection: `entities`)

### 3. auth_attempts
- **mail_hash**: `text` (Required)
- **code**: `number` (Required)
- **expiry**: `date` (Required)
- **state**: `select` (sent, success, failed, expired)

### 4. sent_logs
- **mail_hash**: `text` (Required)
- **template_id**: `relation` (Single, Collection: `templates`)
- **entity_id**: `relation` (Single, Collection: `entities`)
- **timestamp**: `date` (Required)

---
**Note**: Ensure that API rules are set to allow `List/View` for `templates` and `entities` (public or based on your preference), and `Create` for `auth_attempts` and `sent_logs` (handled by the backend service account if using one, or public if the backend is the only one talking to it).
