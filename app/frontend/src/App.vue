<template>
  <div id="app">
    <header class="app-header">
      <h1>Изпращане на писмо</h1>
    </header>
    <main class="app-main">
      <form @submit.prevent="handleSubmit" class="mail-form">
        <div class="form-group">
          <label for="name">Име:</label>
          <input type="text" id="name" v-model="form.name" required />
        </div>

        <div class="form-group">
          <label for="surname">Фамилия:</label>
          <input type="text" id="surname" v-model="form.surname" required />
        </div>

        <div class="form-group">
          <label for="email">Личен имейл:</label>
          <input type="email" id="email" v-model="form.mail" required />
        </div>

        <div class="form-group">
          <label for="template">Изберете шаблон:</label>
          <select id="template" v-model="form.selected_template" required>
            <option disabled value="">Моля, изберете един</option>
            <option
              v-for="template in templates"
              :key="template.id"
              :value="template.id"
            >
              {{ template.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="entity">Изберете институция:</label>
          <select id="entity" v-model="form.selected_entity" required>
            <option disabled value="">Моля, изберете една</option>
            <option
              v-for="entity in filteredEntities"
              :key="entity.id"
              :value="entity.id"
            >
              {{ entity.name }}
            </option>
          </select>
        </div>

        <button type="submit" :disabled="!isFormValid" class="send-button">
          Изпрати
        </button>

        <p v-if="successMessage" class="success-message">
          {{ successMessage }}
        </p>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </form>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import axios from "axios";

interface Template {
  id: number;
  name: string;
}

interface Entity {
  id: number;
  name: string;
}

const form = ref({
  name: "",
  surname: "",
  mail: "",
  selected_template: null as number | null,
  selected_entity: null as number | null,
});

const templates = ref<Template[]>([]);
const entities = ref<Entity[]>([]);
const successMessage = ref("");
const errorMessage = ref("");

const isFormValid = computed(() => {
  return (
    form.value.name &&
    form.value.surname &&
    form.value.mail &&
    form.value.selected_template !== null &&
    form.value.selected_entity !== null
  );
});

const filteredEntities = computed(() => {
  return entities.value;
});

watch(
  () => form.value.selected_template,
  (newTemplateId, oldTemplateId) => {
    // Reset selected_entity if the template changes
    if (newTemplateId !== oldTemplateId) {
      form.value.selected_entity = null;
    }
  }
);


const fetchTemplates = async () => {
  errorMessage.value = "";
  try {
    const response = await axios.get<Template[]>("/templates");
    templates.value = response.data;
  } catch (error: any) {
    errorMessage.value =
      "Грешка при зареждане на шаблони: " +
      (error.response?.data?.detail || error.message);
    console.error("Error fetching templates:", error);
  }
};

const fetchEntitiesForTemplate = async (templateId: number) => {
  errorMessage.value = "";
  try {
    const response = await axios.get<Entity[]>(`/entities/${templateId}`);
    entities.value = response.data;
  } catch (error: any) {
    errorMessage.value =
      "Грешка при зареждане на институции: " +
      (error.response?.data?.detail || error.message);
    console.error("Error fetching entities:", error);
  }
};

onMounted(() => {
  fetchTemplates();
});

watch(
  () => form.value.selected_template,
  async (newTemplateId) => {
    form.value.selected_entity = null; // Reset entity selection
    if (newTemplateId) {
      await fetchEntitiesForTemplate(newTemplateId);
    } else {
      entities.value = [];
    }
  }
);

const handleSubmit = async () => {
  successMessage.value = "";
  errorMessage.value = "";
  try {
    const response = await axios.post("/send-mail", form.value);
    successMessage.value =
      "Имейлът е изпратен успешно! Моля, проверете пощата си за потвърждение.";
    console.log("Form submitted successfully:", response.data);
  } catch (error: any) {
    errorMessage.value =
      "Възникна грешка при изпращане на имейла: " +
      (error.response?.data?.detail || error.message);
    console.error("Error submitting form:", error);
  }
};

</script>

<style>
#app {
  font-family: Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #333;
  margin-top: 60px;
  background-color: white; /* White background */
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.app-header {
  margin-bottom: 40px;
}

h1 {
  color: #007bff; /* A shade of blue for headings, can be adjusted to green/red */
}

.app-main {
  width: 100%;
  max-width: 500px;
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  background-color: #fff;
}

.mail-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  text-align: left;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

input[type="text"],
input[type="email"],
select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box; /* Ensures padding doesn't increase width */
}

.send-button {
  background-color: #28a745; /* Green accent */
  color: white;
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s;
}

.send-button:hover:not(:disabled) {
  background-color: #218838;
}

.send-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.success-message {
  color: #28a745; /* Green for success */
  font-weight: bold;
}

.error-message {
  color: #dc3545; /* Red for error */
  font-weight: bold;
}
</style>