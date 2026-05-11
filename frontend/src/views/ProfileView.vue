<script setup>
import { ref, onMounted } from "vue";
import api from "../api";

const user = ref(null);
const loading = ref(true);

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
          <div
            v-for="field in user.profile_fields.slice(0, 4)"
            :key="field.label"
            class="profil_list_item"
          >
            <p>{{ field.label }}</p>
            <input readonly type="text" :value="field.value || '-'">
          </div>
        </div>

        <div class="profil_list">
          <div
            v-for="field in user.profile_fields.slice(4)"
            :key="field.label"
            class="profil_list_item"
          >
            <p>{{ field.label }}</p>
            <input readonly type="text" :value="field.value || '-'">
          </div>
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
