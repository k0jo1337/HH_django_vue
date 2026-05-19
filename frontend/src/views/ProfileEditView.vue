<script setup>
import { computed, reactive, ref, onMounted, onUnmounted, watch } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import FormField from "../components/FormField.vue";
import ProfileSidebar from "../components/ProfileSidebar.vue";
import { editableProfileFields, profileInitialValues } from "../forms/profileFields";
import { isEmployeeUser } from "../auth";

const router = useRouter();

const loading = ref(true);
const saving = ref(false);
const error = ref("");
const success = ref("");
const selectedAvatarFile = ref(null);
const avatarPreviewUrl = ref("");
const isEmployee = computed(() => isEmployeeUser());

const form = reactive({
  ...profileInitialValues,
  has_no_middle_name: false,
  avatar: "",
});

// Поля, которые нужно скрыть для сотрудников
const hiddenForEmployee = ['room_number', 'hostel'];

const fieldGroups = computed(() => {
  const groups = {
    name: [],
    contacts: [],
  };

  editableProfileFields.forEach((field) => {
    // Пропускаем скрытые поля для сотрудников
    if (isEmployee.value && hiddenForEmployee.includes(field.name)) {
      return;
    }

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

const sidebarUser = computed(() => ({
  ...form,
  avatar: avatarPreviewUrl.value || form.avatar,
}));

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

const selectAvatar = (file) => {
  selectedAvatarFile.value = file;
  if (avatarPreviewUrl.value) {
    URL.revokeObjectURL(avatarPreviewUrl.value);
  }
  avatarPreviewUrl.value = URL.createObjectURL(file);
};

onUnmounted(() => {
  if (avatarPreviewUrl.value) {
    URL.revokeObjectURL(avatarPreviewUrl.value);
  }
});

const saveProfile = async () => {
  error.value = "";
  success.value = "";
  saving.value = true;

  try {
    const data = new FormData();

    Object.entries({
      ...form,
      middle_name: form.has_no_middle_name ? "" : form.middle_name,
    }).forEach(([key, value]) => {
      if (key !== "avatar") {
        data.append(key, value ?? "");
      }
    });

    if (selectedAvatarFile.value) {
      data.append("avatar", selectedAvatarFile.value);
    }

    const response = await api.patch("/account/profile/", data);

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

    <div v-else class="profile-layout">
      <ProfileSidebar
        :user="sidebarUser"
        editable
        :uploading="saving"
        @avatar-change="selectAvatar"
      />

      <form class="profil_item_2" @submit.prevent="saveProfile">
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
    </div>
  </main>
</template>