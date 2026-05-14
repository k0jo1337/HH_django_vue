<script setup>
import { ref } from "vue";
import api from "../api";

const emit = defineEmits(['close']);

const email = ref("");
const loading = ref(false);
const error = ref("");
const success = ref("");

async function resetPassword() {
  error.value = "";
  success.value = "";
  loading.value = true;

  try {
    const response = await api.post("/account/password-reset/", {
      email: email.value
    });

    success.value = response.data.message || "Инструкции отправлены на ваш email";

    setTimeout(() => {
      emit('close');
    }, 3000);
  } catch (err) {
    if (err.response?.data?.error) {
      error.value = err.response.data.error;
    } else if (err.response?.data?.message) {
      success.value = err.response.data.message;
    } else {
      error.value = "Ошибка сервера";
    }
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <form @submit.prevent="resetPassword">
    <div class="form-group">
      <label>Email</label>
      <input
        v-model="email"
        type="email"
        required
        placeholder="Введите ваш email"
      >
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="success" class="success-message">
      {{ success }}
    </div>

    <div class="modal-buttons">
      <button type="button" @click="$emit('close')">Отмена</button>
      <button type="submit" :disabled="loading">
        {{ loading ? "Отправка..." : "Отправить" }}
      </button>
    </div>
  </form>
</template>

<style scoped>
.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.error-message {
  color: red;
  font-size: 14px;
  margin-bottom: 12px;
}

.success-message {
  color: green;
  font-size: 14px;
  margin-bottom: 12px;
}

.modal-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 16px;
}

.modal-buttons button {
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}

.modal-buttons button[type="button"] {
  background: #e0e0e0;
  border: none;
}

.modal-buttons button[type="submit"] {
  background: #3c5ba4;
  color: white;
  border: none;
}

.modal-buttons button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>