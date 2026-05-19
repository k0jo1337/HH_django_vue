<script setup>
import { computed, ref, onMounted } from "vue";
import api from "../api";
import FormField from "../components/FormField.vue";
import ProfileSidebar from "../components/ProfileSidebar.vue";
import ChangePasswordModal from "../components/ChangePasswordModal.vue";
import { editableProfileFields } from "../forms/profileFields";
import { isEmployeeUser } from "../auth";

const user = ref(null);
const loading = ref(true);
const showChangePassword = ref(false);
const isEmployee = computed(() => isEmployeeUser());

const fieldGroups = computed(() => {
  const source = user.value || {};
  const groups = {
    name: [],
    contacts: [],
  };

  // Поля, которые нужно скрыть для сотрудников
  const hiddenForEmployee = ['room_number', 'hostel'];

  editableProfileFields.forEach((field) => {
    // Пропускаем скрытые поля для сотрудников
    if (isEmployee.value && hiddenForEmployee.includes(field.name)) {
      return;
    }

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

function openChangePassword() {
  showChangePassword.value = true;
}

function closeChangePassword() {
  showChangePassword.value = false;
}
</script>

<template>
  <main class="profile-page">
    <div v-if="loading" class="profile-loading">
      Загрузка...
    </div>

    <div v-else-if="user" class="profile-layout">
      <ProfileSidebar :user="user" />

      <div class="profil_item_2">
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
          <a href="#" @click.prevent="openChangePassword">Смена пароля</a>
        </div>
      </div>
    </div>

    <ChangePasswordModal
      v-if="showChangePassword"
      @close="closeChangePassword"
    />
  </main>
</template>