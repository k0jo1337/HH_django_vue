<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import api from "../api";

const route = useRoute();

const appeals = ref([]);
const loading = ref(true);
const error = ref("");

const mode = computed(() => route.meta.appealMode || "active");
const isHistory = computed(() => mode.value === "history");
const title = computed(() => (isHistory.value ? "История обращений" : "Активные обращения"));
const emptyText = computed(() => (
  isHistory.value
    ? "Завершенных обращений пока нет"
    : "Активных обращений пока нет"
));

function formatDate(value) {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

async function loadAppeals() {
  loading.value = true;
  error.value = "";

  try {
    // Исправленный URL - убрал /appeals/ на /appeals/list/
    const response = await api.get("/appeals/list/", {
      params: {
        type: mode.value,
      },
    });
    appeals.value = response.data.appeals || [];
  } catch {
    error.value = "Не удалось загрузить обращения";
  } finally {
    loading.value = false;
  }
}

onMounted(loadAppeals);
watch(mode, loadAppeals);
</script>

<template>
  <main class="appeal-page">
    <section class="appeal-list">
      <div class="appeal-header appeal-list-header">
        <h1>{{ title }}</h1>
        <RouterLink class="appeal-create-link" to="/appeal/new">
          Создать обращение
        </RouterLink>
      </div>

      <div class="appeal-tabs" aria-label="Фильтр обращений">
        <RouterLink to="/appeal" class="appeal-tab">
          Активные
        </RouterLink>
        <RouterLink to="/appeal/history" class="appeal-tab">
          История
        </RouterLink>
      </div>

      <p v-if="loading" class="appeal-state">Загрузка...</p>
      <p v-else-if="error" class="appeal-message appeal-message-error">{{ error }}</p>
      <p v-else-if="!appeals.length" class="appeal-state">{{ emptyText }}</p>

      <div v-else class="appeal-cards custom-scroll">
        <article v-for="appeal in appeals" :key="appeal.id" class="appeal-card">
          <div class="appeal-card-top">
            <div>
              <h2>{{ appeal.subject }}</h2>
              <p>{{ appeal.specialist_label }}</p>
            </div>
            <span class="appeal-status">{{ appeal.status_label }}</span>
          </div>

          <p class="appeal-card-message">{{ appeal.message }}</p>

          <div class="appeal-card-meta">
            <span>Создано: {{ formatDate(appeal.created_at) }}</span>
            <span v-if="isHistory">Завершено: {{ formatDate(appeal.updated_at) }}</span>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>