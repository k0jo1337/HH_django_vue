<script setup>
import { ref } from "vue";
import api from "../api";

const emit = defineEmits(['close', 'success']);

const show = ref(true);
const loading = ref(false);
const error = ref("");
const success = ref("");

const form = ref({
  old_password: "",
  new_password1: "",
  new_password2: "",
});

// Состояние видимости паролей
const showOldPassword = ref(false);
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);

function closeModal() {
  show.value = false;
  emit('close');
}

function togglePassword(field) {
  if (field === 'old') showOldPassword.value = !showOldPassword.value;
  if (field === 'new') showNewPassword.value = !showNewPassword.value;
  if (field === 'confirm') showConfirmPassword.value = !showConfirmPassword.value;
}

async function changePassword() {
  error.value = "";
  success.value = "";
  loading.value = true;

  if (form.value.new_password1 !== form.value.new_password2) {
    error.value = "Новые пароли не совпадают";
    loading.value = false;
    return;
  }

  try {
    const response = await api.post("/account/change-password/", {
      old_password: form.value.old_password,
      new_password1: form.value.new_password1,
      new_password2: form.value.new_password2,
    });

    success.value = response.data.message;

    form.value = {
      old_password: "",
      new_password1: "",
      new_password2: "",
    };

    setTimeout(() => {
      emit('success');
      closeModal();
    }, 1500);

  } catch (err) {
    if (err.response?.data) {
      const errors = err.response.data;
      if (errors.old_password) {
        error.value = errors.old_password;
      } else if (errors.new_password1) {
        error.value = errors.new_password1;
      } else if (errors.new_password2) {
        error.value = errors.new_password2;
      } else {
        error.value = "Ошибка смены пароля";
      }
    } else {
      error.value = "Ошибка сервера";
    }
  } finally {
    loading.value = false;
  }
}

function handleOverlayClick(e) {
  if (e.target === e.currentTarget) {
    closeModal();
  }
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Смена пароля</h2>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="changePassword">
          <div class="form-group">
            <label>Текущий пароль</label>
            <div class="password-wrapper">
              <input
                v-model="form.old_password"
                :type="showOldPassword ? 'text' : 'password'"
                required
                placeholder="Введите текущий пароль"
              >
              <button
                type="button"
                class="eye-btn"
                @click="togglePassword('old')"
              >
                <i :class="showOldPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>Новый пароль</label>
            <div class="password-wrapper">
              <input
                v-model="form.new_password1"
                :type="showNewPassword ? 'text' : 'password'"
                required
                placeholder="Введите новый пароль"
              >
              <button
                type="button"
                class="eye-btn"
                @click="togglePassword('new')"
              >
                <i :class="showNewPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>Подтверждение нового пароля</label>
            <div class="password-wrapper">
              <input
                v-model="form.new_password2"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                placeholder="Подтвердите новый пароль"
              >
              <button
                type="button"
                class="eye-btn"
                @click="togglePassword('confirm')"
              >
                <i :class="showConfirmPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
              </button>
            </div>
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>

          <div v-if="success" class="success-message">
            {{ success }}
          </div>

          <div class="modal-buttons">
            <button type="button" @click="closeModal" class="btn-cancel">
              Отмена
            </button>
            <button type="submit" :disabled="loading" class="btn-submit">
              {{ loading ? "Сохранение..." : "Сменить пароль" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 450px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #E2E8F0;
}

.modal-header h2 {
  margin: 0;
  font-size: 24px;
  color: #1E293B;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #94A3B8;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #1E293B;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #1E293B;
  font-weight: 500;
  font-size: 14px;
}

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-wrapper input {
  width: 100%;
  padding: 10px 40px 10px 12px;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.password-wrapper input:focus {
  outline: none;
  border-color: #3c5ba4;
  box-shadow: 0 0 0 3px rgba(60, 91, 164, 0.1);
}

.eye-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  padding: 0;
  color: #94A3B8;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.eye-btn:hover {
  color: #3c5ba4;
}

.error-message {
  background: #FEE2E2;
  color: #DC2626;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 20px;
}

.success-message {
  background: #DCFCE7;
  color: #16A34A;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 20px;
}

.modal-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.btn-cancel,
.btn-submit {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #E2E8F0;
  color: #1E293B;
}

.btn-cancel:hover {
  background: #CBD5E1;
}

.btn-submit {
  background: #3c5ba4;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: #2d4b91;
  transform: translateY(-1px);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>