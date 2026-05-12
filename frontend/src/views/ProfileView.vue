<script setup>
import { computed, ref, onMounted } from "vue";
import api from "../api";
import FormField from "../components/FormField.vue";
import { editableProfileFields } from "../forms/profileFields";

const user = ref(null);
const loading = ref(true);

const fieldGroups = computed(() => {
  const source = user.value || {};
  const groups = {
    name: [],
    contacts: [],
  };

  editableProfileFields.forEach((field) => {
    groups[field.group].push({
      ...field,
      readonly: true,
      required: false,
      value: source[field.name] || "-",
    });
  });

  return groups;
});

onMounted(async () => {
  try {
    const response = await api.get("/account/me/");
    user.value = response.data.user;
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <main class="profile-page">
    <div v-if="loading" class="profile-loading">
      Загрузка...
    </div>

    <div v-else-if="user" class="profil_item_2">
      <div class="profil_fields">
        <div class="profil_list">
          <FormField
            v-for="field in fieldGroups.name"
            :key="field.name"
            :model-value="field.value"
            :field="{ ...field, class: 'profil_list_item' }"
          />
        </div>

        <div class="profil_list">
          <FormField
            v-for="field in fieldGroups.contacts"
            :key="field.name"
            :model-value="field.value"
            :field="{ ...field, class: 'profil_list_item' }"
          />
        </div>
      </div>

      <div class="profil_change">
        <RouterLink to="/profile/edit">Редактировать профиль</RouterLink>
        <br>
        <RouterLink to="/password-change">Смена пароля</RouterLink>
      </div>
    </div>
  </main>
</template>
