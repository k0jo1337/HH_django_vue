<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import FormField from "../components/FormField.vue";
import { registerFields, registerInitialValues } from "../forms/profileFields";

const router = useRouter();

const form = reactive({ ...registerInitialValues });
const success = ref("");
const error = ref("");
const loading = ref(false);

const visibleFields = computed(() =>
  registerFields.map((field) => {
    if (field.name !== "middle_name") {
      return field;
    }

    return {
      ...field,
      disabled: form.has_no_middle_name,
      required: !form.has_no_middle_name,
    };
  })
);

watch(
  () => form.has_no_middle_name,
  (value) => {
    if (value) {
      form.middle_name = "";
    }
  }
);

function firstError(data) {
  const fields = [
    "username",
    "email",
    "last_name",
    "first_name",
    "middle_name",
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

  if (form.password !== form.password_confirm) {
    error.value = "Пароли не совпадают";
    return;
  }

  try {
    loading.value = true;

    const response = await api.post("/account/register/", {
      ...form,
      middle_name: form.has_no_middle_name ? "" : form.middle_name,
    });

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
          <template v-for="field in visibleFields" :key="field.name">
            <FormField
              v-model="form[field.name]"
              :field="field"
            />

            <FormField
              v-if="field.name === 'middle_name'"
              v-model="form.has_no_middle_name"
              :field="{
                name: 'has_no_middle_name',
                label: 'Отчество отсутствует',
                type: 'checkbox',
                class: 'checkbox_form',
              }"
            />
          </template>

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
