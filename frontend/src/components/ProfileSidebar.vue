<script setup>
import { computed, ref } from "vue";
import { isEmployeeUser } from "../auth";

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
  editable: {
    type: Boolean,
    default: false,
  },
  uploading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["avatar-change"]);

const fileInput = ref(null);
const imageLoadFailed = ref(false);

const isEmployee = computed(() => isEmployeeUser());

const avatarSrc = computed(() => (
  !imageLoadFailed.value && props.user.avatar ? props.user.avatar : "/profil.png"
));

const fullName = computed(() => {
  const parts = [
    props.user.last_name,
    props.user.first_name,
    props.user.middle_name,
  ].filter(Boolean);

  return parts.length ? parts.join(" ") : props.user.username || "-";
});

const roleLabel = computed(() => {
  if (isEmployee.value) {
    return "Сотрудник";
  }
  return "Студент";
});

const hostelLabel = computed(() => {
  const hostel = props.user.hostel || "0";
  return `Общежитие №${hostel}`;
});

const roomLabel = computed(() => {
  const room = props.user.room_number || "-";
  return `Комната №${room}`;
});

const openFileDialog = () => {
  if (props.editable && !props.uploading) {
    fileInput.value?.click();
  }
};

const onFileChange = (event) => {
  const file = event.target.files?.[0];
  if (file) {
    imageLoadFailed.value = false;
    emit("avatar-change", file);
  }
  event.target.value = "";
};

const useDefaultAvatar = () => {
  imageLoadFailed.value = true;
};
</script>

<template>
  <aside class="profil_item_1">
    <div class="profil_list_item_1">
      <div class="Profil_foto">
        <button
          v-if="editable"
          class="profile-avatar-button"
          type="button"
          :disabled="uploading"
          @click="openFileDialog"
        >
          <img :src="avatarSrc" alt="Фото профиля" @error="useDefaultAvatar">
          <span>{{ uploading ? "Загрузка..." : "Изменить фото" }}</span>
        </button>

        <img v-else :src="avatarSrc" alt="Фото профиля" @error="useDefaultAvatar">

        <input
          ref="fileInput"
          class="profile-avatar-input"
          type="file"
          accept="image/*"
          @change="onFileChange"
        >
      </div>

      <div class="profil_name">
        <h3>{{ fullName }}</h3>
        <p class="role-badge">{{ roleLabel }}</p>
        <p>{{ hostelLabel }}</p>
        <!-- Скрываем комнату для сотрудников -->
        <p v-if="!isEmployee">{{ roomLabel }}</p>
      </div>
    </div>

    <div class="profil_list_item_2">
      <!-- Активные обращения для ВСЕХ пользователей -->
      <div class="profil_inf">
        <RouterLink to="/appeal">Активные обращения</RouterLink>
      </div>

      <!-- История обращений для ВСЕХ пользователей -->
      <div class="profil_inf ind">
        <RouterLink to="/appeal/history">История обращений</RouterLink>
      </div>

      <!-- Все заявки (только для сотрудников) -->
      <div v-if="isEmployee" class="profil_inf">
        <RouterLink to="/employee/appeals">📋 Все заявки</RouterLink>
      </div>

      <!-- Управление новостями (только для сотрудников) -->
      <div v-if="isEmployee" class="profil_inf ind">
        <RouterLink to="/home">📰 Управление новостями</RouterLink>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.role-badge {
  color: #3c5ba4;
  font-weight: bold;
  margin-top: 5px;
}
</style>