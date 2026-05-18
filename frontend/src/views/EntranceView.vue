<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { setAuthenticated, setEmployee } from "../auth";
import FormField from "../components/FormField.vue";
import PasswordResetForm from "../components/PasswordResetForm.vue";

const router = useRouter();

const form = reactive({
  username: "",
  password: "",
});

const error = ref("");
const success = ref("");
const loading = ref(false);
const showResetModal = ref(false);

const loginFields = [
  { name: "username", label: "Логин:", type: "text", required: true, autocomplete: "username" },
  { name: "password", label: "Пароль:", type: "password", required: true, autocomplete: "current-password" },
];

async function loginUser() {
  error.value = "";
  success.value = "";

  try {
    loading.value = true;

    const response = await api.post("/account/login/", {
      username: form.username,
      password: form.password,
    });

    success.value = response.data.message;
    setAuthenticated(true);

    const roleResponse = await api.get("/account/role/");
    setEmployee(roleResponse.data.is_employee);

    await router.push("/home");

  } catch (err) {
    if (err.response?.data?.error) {
      error.value = err.response.data.error;
    } else {
      error.value = "Ошибка сервера";
    }
  } finally {
    loading.value = false;
  }
}

function openResetModal() {
  showResetModal.value = true;
}

function closeResetModal() {
  showResetModal.value = false;
}
</script>

<template>
  <main class="main">
    <div class="parent_form">
      <div class="form_logo">
        <img class="form-logo-full" src="/Hostel_logo.png" alt="Hostel Helper">
        <img class="form-logo-compact" src="/Hostel_logo.png" alt="Hostel Helper">
      </div>

      <div class="adaptiv_form">
        <div class="input_form">
          <h1>Авторизация</h1>
        </div>

        <hr>

        <form @submit.prevent="loginUser">
          <FormField
            v-for="field in loginFields"
            :key="field.name"
            v-model="form[field.name]"
            :field="field"
          />

          <div class="input_form">
            <input
              type="submit"
              :value="loading ? 'Вход...' : 'Авторизоваться'"
              class="btn-primary"
              :disabled="loading"
            >
          </div>
        </form>

        <div v-if="success" class="alert alert-success mt-3">
          {{ success }}
        </div>

        <div v-if="error" class="alert alert-danger mt-3">
          {{ error }}
        </div>

        <h6>
          Нет аккаунта?
          <RouterLink to="/registration">Регистрация</RouterLink>
        </h6>

        <div class="forgot-password">
          <a href="#" @click.prevent="openResetModal">Забыли пароль?</a>
        </div>
      </div>
    </div>

    <div class="parent_entrance">
      <div class="adaptiv_entrance">
        <img src="/entrance_img.png" alt="image">
      </div>
    </div>

    <!-- Модальное окно восстановления пароля -->
    <div v-if="showResetModal" class="modal-overlay" @click.self="closeResetModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Восстановление пароля</h3>
          <button class="modal-close" @click="closeResetModal">&times;</button>
        </div>
        <div class="modal-body">
          <PasswordResetForm @close="closeResetModal" />
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.forgot-password {
  text-align: left;
  margin-top: 4px;
}

.forgot-password a {
  color: #3c5ba4;
  font-size: 1rem;
  font-weight: 500;
  text-decoration: none;
}

.forgot-password a:hover {
  text-decoration: underline;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-close:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}
</style>
