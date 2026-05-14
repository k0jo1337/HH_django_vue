<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";

const route = useRoute();
const router = useRouter();

const uid = ref("");
const token = ref("");
const valid = ref(false);
const loading = ref(true);
const error = ref("");
const success = ref("");

const newPassword1 = ref("");
const newPassword2 = ref("");
const submitting = ref(false);

// Состояние видимости паролей
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);

onMounted(async () => {
  uid.value = route.params.uid;
  token.value = route.params.token;

  try {
    const response = await api.get(`/account/password-reset/verify/${uid.value}/${token.value}/`);
    valid.value = response.data.valid;
  } catch (err) {
    error.value = "Ссылка недействительна или устарела";
  } finally {
    loading.value = false;
  }
});

function togglePassword(field) {
  if (field === 'new') showNewPassword.value = !showNewPassword.value;
  if (field === 'confirm') showConfirmPassword.value = !showConfirmPassword.value;
}

async function resetPassword() {
  error.value = "";

  if (newPassword1.value !== newPassword2.value) {
    error.value = "Пароли не совпадают";
    return;
  }

  if (newPassword1.value.length < 6) {
    error.value = "Пароль должен содержать минимум 6 символов";
    return;
  }

  submitting.value = true;

  try {
    await api.post("/account/password-reset/confirm/", {
      uid: uid.value,
      token: token.value,
      new_password1: newPassword1.value,
      new_password2: newPassword2.value,
    });

    success.value = "Пароль успешно изменен!";

    setTimeout(() => {
      router.push("/");
    }, 2000);
  } catch (err) {
    if (err.response?.data?.error) {
      error.value = err.response.data.error;
    } else {
      error.value = "Ошибка сброса пароля";
    }
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <main class="reset-password-page">
    <div class="reset-container">
      <div class="reset-card">
        <h1>Сброс пароля</h1>

        <div v-if="loading" class="loading">
          Проверка ссылки...
        </div>

        <div v-else-if="error" class="error-message">
          {{ error }}
          <p><RouterLink to="/">Вернуться на главную</RouterLink></p>
        </div>

        <div v-else-if="valid" class="reset-form">
          <form @submit.prevent="resetPassword">
            <div class="form-group">
              <label>Новый пароль</label>
              <div class="password-wrapper">
                <input
                  v-model="newPassword1"
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
              <label>Подтверждение пароля</label>
              <div class="password-wrapper">
                <input
                  v-model="newPassword2"
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

            <div v-if="error" class="error-message">{{ error }}</div>
            <div v-if="success" class="success-message">{{ success }}</div>

            <button type="submit" :disabled="submitting" class="btn-submit">
              {{ submitting ? "Сохранение..." : "Сменить пароль" }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.reset-password-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F8FAFC;
}

.reset-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.reset-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

h1 {
  text-align: center;
  margin-bottom: 24px;
  color: #1E293B;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
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
}

.password-wrapper input:focus {
  outline: none;
  border-color: #3c5ba4;
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

.btn-submit {
  width: 100%;
  padding: 12px;
  background: #3c5ba4;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}

.btn-submit:hover:not(:disabled) {
  background: #2d4b91;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: red;
  font-size: 14px;
  margin-bottom: 16px;
  text-align: center;
}

.success-message {
  color: green;
  font-size: 14px;
  margin-bottom: 16px;
  text-align: center;
}

.loading {
  text-align: center;
  padding: 20px;
}
</style>