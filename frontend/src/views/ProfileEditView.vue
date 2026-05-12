<script setup>
import { computed, reactive, ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import FormField from "../components/FormField.vue";
import { editableProfileFields, profileInitialValues } from "../forms/profileFields";

const router = useRouter();

const loading = ref(true);
const saving = ref(false);
const error = ref("");
const success = ref("");

const form = reactive({
  ...profileInitialValues,
  has_no_middle_name: false,
});

const fieldGroups = computed(() => {
  const groups = {
    name: [],
    contacts: [],
  };

  editableProfileFields.forEach((field) => {
    const nextField = field.name === "middle_name"
      ? {
          ...field,
          disabled: form.has_no_middle_name,
          required: !form.has_no_middle_name,
        }
      : field;

    groups[nextField.group].push(nextField);
  });

  return groups;
});

watch(
  () => form.has_no_middle_name,
  (value) => {
    if (value) {
      form.middle_name = "";
    }
  }
);

onMounted(async () => {
  try {
    const response = await api.get("/account/profile/");
    Object.assign(form, response.data.user || response.data);
  } catch {
    error.value = "Не удалось загрузить профиль";
  } finally {
    loading.value = false;
  }
});

const saveProfile = async () => {
  error.value = "";
  success.value = "";
  saving.value = true;

  try {
    const response = await api.patch("/account/profile/", {
      ...form,
      middle_name: form.has_no_middle_name ? "" : form.middle_name,
    });

    success.value = response.data.message || "Профиль сохранен";
    await router.push("/profile");
  } catch (err) {
    const data = err.response?.data;
    error.value =
      typeof data === "string"
        ? data
        : data?.detail || data?.middle_name || data?.phone || "Не удалось сохранить профиль";
  } finally {
    saving.value = false;
  }
};
</script>

<template>
  <main class="profile-page">
    <div v-if="loading" class="profile-loading">
      Загрузка...
    </div>

    <form v-else class="profil_item_2" @submit.prevent="saveProfile">
      <div class="profil_fields">
        <div class="profil_list">
          <template v-for="field in fieldGroups.name" :key="field.name">
            <FormField
              v-model="form[field.name]"
              :field="{ ...field, class: 'profil_list_item' }"
            />

            <FormField
              v-if="field.name === 'middle_name'"
              v-model="form.has_no_middle_name"
              :field="{
                name: 'has_no_middle_name',
                label: 'Нет отчества',
                type: 'checkbox',
                class: 'profile-checkbox',
              }"
            />
          </template>
        </div>

        <div class="profil_list">
          <FormField
            v-for="field in fieldGroups.contacts"
            :key="field.name"
            v-model="form[field.name]"
            :field="{ ...field, class: 'profil_list_item' }"
          />
        </div>
      </div>

      <p v-if="error" class="profile-message profile-message-error">{{ error }}</p>
      <p v-if="success" class="profile-message profile-message-success">{{ success }}</p>

      <div class="profil_change">
        <button type="submit" :disabled="saving">
          {{ saving ? "Сохранение..." : "Сохранить" }}
        </button>
        <RouterLink to="/profile">Отмена</RouterLink>
      </div>
    </form>
  </main>
</template>
