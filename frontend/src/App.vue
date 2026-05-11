<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "./api";

const route = useRoute();
const router = useRouter();

const showSidebar = computed(() => !route.meta.guestOnly);

async function logoutUser() {
  await api.post("/account/logout/", {});

  router.push("/");
}
</script>

<template>
  <div v-if="showSidebar" class="app-layout">
    <aside class="out">
      <div class="sidebar_logo">
        <RouterLink to="/home">
          <img src="/Logo.png" alt="Logo">
        </RouterLink>
      </div>

      <nav class="side">
        <ul class="nav_list">
          <li class="nav_list-item">
            <RouterLink to="/profile" class="nav_list-link">
              <img src="/profil.png" alt="Профиль">
            </RouterLink>
          </li>

          <li class="nav_list-item">
            <RouterLink to="/chat" class="nav_list-link">
              <img src="/chat.png" alt="Чат">
            </RouterLink>
          </li>

          <li class="nav_list-item">
            <RouterLink to="/appeal" class="nav_list-link">
              <img src="/complaint.png" alt="Обращение">
            </RouterLink>
          </li>
        </ul>
      </nav>

      <div class="exit">
        <a href="#" class="exit-link" @click.prevent="logoutUser">
          <img src="/exit.png" alt="Выход">
        </a>
      </div>
    </aside>

    <div class="app-content">
      <RouterView />
    </div>
  </div>

  <RouterView v-else />
</template>
