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
          <div class="profil_list_item">
            <p>Фамилия</p>
            <input readonly type="text" :value="user.last_name || '-'">
          </div>
          <div class="profil_list_item">
            <p>Имя</p>
            <input readonly type="text" :value="user.first_name || '-'">
          </div>
          <div class="profil_list_item">
            <p>Отчество</p>
            <input readonly type="text" :value="user.middle_name || '-'">
          </div>
          <div class="profil_list_item">
            <p>Телефон</p>
            <input readonly type="text" :value="user.phone || '-'">
          </div>
        </div>

        <div class="profil_list">
          <div class="profil_list_item">
            <p>Email</p>
            <input readonly type="text" :value="user.email || '-'">
          </div>
          <div class="profil_list_item">
            <p>Комната</p>
            <input readonly type="text" :value="user.room_number || '-'">
          </div>
          <div class="profil_list_item">
            <p>Общежитие</p>
            <input readonly type="text" :value="user.hostel || '-'">
          </div>
          <div class="profil_list_item">
            <p>Институт</p>
            <input readonly type="text" :value="user.university || '-'">
          </div>
        </div>
      </div>

      <div class="profil_change">
        <RouterLink to="/profile/edit">✏️ Редактировать профиль</RouterLink>
        <br>
        <RouterLink to="/password-change">🔒 Смена пароля</RouterLink>
      </div>
    </div>
  </main>
</template>