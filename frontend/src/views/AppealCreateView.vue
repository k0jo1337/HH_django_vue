<script setup>
import { reactive, ref } from "vue";
import api from "../api";
import FormField from "../components/FormField.vue";

const specialists = [
  { value: "plumber", label: "Сантехник" },
  { value: "carpenter", label: "Плотник" },
  { value: "electrician", label: "Электрик" },
  { value: "other", label: "Другое" },
];

const appealFields = [
  {
    name: "subject",
    label: "Тема",
    type: "text",
    class: "appeal-field",
    id: "appeal-subject",
    required: true,
    maxlength: 120,
    placeholder: "Кратко опишите проблему",
    labelTag: "label",
  },
  {
    name: "specialist",
    label: "Специалист",
    type: "select",
    class: "appeal-field",
    id: "appeal-specialist",
    required: true,
    placeholder: "Выберите специалиста",
    options: specialists,
    labelTag: "label",
  },
  {
    name: "message",
    label: "Обращение",
    type: "textarea",
    class: "appeal-field",
    id: "appeal-message",
    required: true,
    rows: 7,
    maxlength: 1000,
    placeholder: "Опишите, что случилось",
    labelTag: "label",
  },
];

const form = reactive({
  subject: "",
  specialist: "",
  message: "",
});

const loading = ref(false);
const success = ref("");
const error = ref("");

function resetForm() {
  form.subject = "";
  form.specialist = "";
  form.message = "";
}

async function createAppeal() {
  error.value = "";
  success.value = "";
  loading.value = true;

  try {
    form.subject = form.subject.trim();
    form.message = form.message.trim();

    await api.post("/appeals/create/", {
      subject: form.subject,
      specialist: form.specialist,
      message: form.message,
    });

    success.value = "Заявка отправлена на почту";
    resetForm();
  } catch (err) {
    error.value = err.response?.data?.error || "Не удалось отправить заявку";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main class="appeal-page appeal-create-page">
    <form class="appeal-form" @submit.prevent="createAppeal">
      <div class="appeal-header">
        <h1>Создание заявки</h1>
      </div>

      <FormField
        v-for="field in appealFields"
        :key="field.name"
        v-model="form[field.name]"
        :field="field"
      />

      <p v-if="error" class="appeal-message appeal-message-error">{{ error }}</p>
      <p v-if="success" class="appeal-message appeal-message-success">{{ success }}</p>

      <div class="appeal-actions">
        <button type="submit" :disabled="loading">
          {{ loading ? "Создание..." : "Создать заявку" }}
        </button>
      </div>
    </form>
  </main>
</template>
