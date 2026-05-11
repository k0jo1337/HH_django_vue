<script setup>
import { ref, watch } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const router = useRouter();

const username = ref("");
const email = ref("");
const lastName = ref("");
const firstName = ref("");
const middleName = ref("");
const hasNoMiddleName = ref(false);
const roomNumber = ref("");
const password = ref("");
const passwordConfirm = ref("");

const success = ref("");
const error = ref("");
const loading = ref(false);

watch(hasNoMiddleName, (value) => {
  if (value) {
    middleName.value = "";
  }
});

function firstError(data) {
  const fields = [
    "username",
    "email",
    "last_name",
    "first_name",
    "middle_name",
    "room_number",
    "password",
    "password_confirm",
    "non_field_errors",
  ];

  for (const field of fields) {
    if (data[field]) {
      return Array.isArray(data[field]) ? data[field][0] : data[field];
    }
  }

  return "Ошибка регистрации";
}

async function registerUser() {
  success.value = "";
  error.value = "";

  if (password.value !== passwordConfirm.value) {
    error.value = "Пароли не совпадают";
    return;
  }

  try {
    loading.value = true;

    const response = await api.post(
      "/account/register/",
      {
        username: username.value,
        email: email.value,
        last_name: lastName.value,
        first_name: firstName.value,
        middle_name: hasNoMiddleName.value ? "" : middleName.value,
        has_no_middle_name: hasNoMiddleName.value,
        room_number: roomNumber.value,
        password: password.value,
        password_confirm: passwordConfirm.value,
      }
    );

    success.value = response.data.message;

    setTimeout(() => {
      router.push("/");
    }, 1000);

  } catch (err) {
    if (err.response && err.response.data) {
      error.value = firstError(err.response.data);
    } else {
      error.value = "Сервер не отвечает";
    }
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main class="main register-main">
    <div class="parent_form">
      <div class="form_logo">
        <img src="/Hostel_logo.png" alt="Hostel Helper">
      </div>

      <div class="adaptiv_form">
        <div class="input_form">
          <h1>Регистрация</h1>
        </div>

        <hr>

        <form @submit.prevent="registerUser">
          <div class="input_form">
            <p>Логин:</p>
            <input v-model="username" type="text" required>
          </div>

          <div class="input_form">
            <p>Email:</p>
            <input v-model="email" type="email" required>
          </div>

          <div class="input_form">
            <p>Фамилия:</p>
            <input v-model="lastName" type="text" required>
          </div>

          <div class="input_form">
            <p>Имя:</p>
            <input v-model="firstName" type="text" required>
          </div>

          <div class="input_form">
            <p>Отчество:</p>
            <input
              v-model="middleName"
              type="text"
              :disabled="hasNoMiddleName"
              :required="!hasNoMiddleName"
            >
          </div>

          <label class="checkbox_form">
            <input v-model="hasNoMiddleName" type="checkbox">
            <span>Отчество отсутствует</span>
          </label>

          <div class="input_form">
            <p>Номер комнаты:</p>
            <input v-model="roomNumber" type="text" required>
          </div>

          <div class="input_form">
            <p>Пароль:</p>
            <input v-model="password" type="password" required>
          </div>

          <div class="input_form">
            <p>Повторите пароль:</p>
            <input v-model="passwordConfirm" type="password" required>
          </div>

          <div class="input_form">
            <input
              type="submit"
              :value="loading ? 'Регистрация...' : 'Зарегистрироваться'"
              class="btn-primary"
              :disabled="loading"
            >
          </div>
        </form>

        <div
          v-if="success"
          class="alert alert-success mt-3"
        >
          {{ success }}
        </div>

        <div
          v-if="error"
          class="alert alert-danger mt-3"
        >
          {{ error }}
        </div>

        <h6>
          Уже есть аккаунт?
          <RouterLink to="/">Авторизация</RouterLink>
        </h6>
      </div>
    </div>

    <div class="parent_entrance">
      <div class="adaptiv_entrance">
        <img src="/entrance_img.png" alt="registration">
      </div>
    </div>
  </main>
</template>
