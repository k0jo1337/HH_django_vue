<script setup>
import { ref, onMounted } from "vue";
import api from "../../api";

const appeals = ref([]);
const loading = ref(true);
const filterStatus = ref("all");
const selectedAppeal = ref(null);
const showModal = ref(false);

const statusLabels = {
  new: "Новое",
  in_progress: "В работе",
  completed: "Завершено",
};

const statusColors = {
  new: "warning",
  in_progress: "primary",
  completed: "success",
};

const allStatuses = [
  { value: "new", label: "Новое" },
  { value: "in_progress", label: "В работе" },
  { value: "completed", label: "Завершено" },
];

async function loadAppeals() {
  loading.value = true;
  try {
    let url = "/appeals/all/";
    if (filterStatus.value !== "all") {
      url += `?type=${filterStatus.value}`;
    }
    const response = await api.get(url);
    appeals.value = response.data.appeals;
  } catch (error) {
    console.error("Ошибка загрузки заявок:", error);
  } finally {
    loading.value = false;
  }
}

async function updateStatus(appealId, newStatus) {
  try {
    await api.patch(`/appeals/${appealId}/status/`, {
      status: newStatus,
    });
    await loadAppeals();
    if (showModal.value && selectedAppeal.value?.appeal?.id === appealId) {
      await viewAppealDetails(appealId);
    }
  } catch (error) {
    console.error("Ошибка обновления статуса:", error);
  }
}

async function viewAppealDetails(appealId) {
  try {
    const response = await api.get(`/appeals/${appealId}/detail/`);
    selectedAppeal.value = response.data;
    showModal.value = true;
  } catch (error) {
    console.error("Ошибка загрузки деталей:", error);
  }
}

function closeModal() {
  showModal.value = false;
  selectedAppeal.value = null;
}

onMounted(() => {
  loadAppeals();
});
</script>

<template>
  <div class="all-appeals">
    <div class="page-header">
      <h1>Все обращения</h1>
      <div class="filters">
        <select v-model="filterStatus" @change="loadAppeals" class="filter-select">
          <option value="all">Все статусы</option>
          <option value="new">Новые</option>
          <option value="in_progress">В работе</option>
          <option value="completed">Завершенные</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else-if="appeals.length === 0" class="empty-state">
      <p>Нет обращений</p>
    </div>

    <div v-else class="appeals-list">
      <div v-for="appeal in appeals" :key="appeal.id" class="appeal-card">
        <div class="appeal-header">
          <div class="appeal-title">
            <h3>{{ appeal.subject }}</h3>
            <span :class="['status-badge', statusColors[appeal.status]]">
              {{ statusLabels[appeal.status] }}
            </span>
          </div>
          <div class="appeal-date">{{ new Date(appeal.created_at).toLocaleString() }}</div>
        </div>

        <div class="appeal-info">
          <div class="info-row">
            <span class="info-label">Специалист:</span>
            <span class="info-value">{{ appeal.specialist_label }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Текст обращения:</span>
            <p class="appeal-message">{{ appeal.message }}</p>
          </div>
        </div>

        <div class="appeal-actions">
          <button class="btn-detail" @click="viewAppealDetails(appeal.id)">
            Подробнее
          </button>
          <select
            :value="appeal.status"
            @change="updateStatus(appeal.id, $event.target.value)"
            class="status-select"
            :style="{ backgroundColor: statusColors[appeal.status] + '20', borderColor: statusColors[appeal.status] }"
          >
            <option v-for="status in allStatuses" :key="status.value" :value="status.value">
              {{ status.label }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Модальное окно с деталями пользователя -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Информация о заявке</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body" v-if="selectedAppeal">
          <div class="info-section">
            <h4>📋 Информация о заявке</h4>
            <div class="info-item">
              <span class="label">Тема:</span>
              <span class="value">{{ selectedAppeal.appeal.subject }}</span>
            </div>
            <div class="info-item">
              <span class="label">Специалист:</span>
              <span class="value">{{ selectedAppeal.appeal.specialist_label }}</span>
            </div>
            <div class="info-item">
              <span class="label">Статус:</span>
              <select
                :value="selectedAppeal.appeal.status"
                @change="updateStatus(selectedAppeal.appeal.id, $event.target.value)"
                class="status-select-inline"
                :style="{ backgroundColor: statusColors[selectedAppeal.appeal.status] + '20', borderColor: statusColors[selectedAppeal.appeal.status] }"
              >
                <option v-for="status in allStatuses" :key="status.value" :value="status.value">
                  {{ status.label }}
                </option>
              </select>
            </div>
            <div class="info-item">
              <span class="label">Создано:</span>
              <span class="value">{{ new Date(selectedAppeal.appeal.created_at).toLocaleString() }}</span>
            </div>
            <div class="info-item">
              <span class="label">Текст заявки:</span>
              <p class="appeal-text">{{ selectedAppeal.appeal.message }}</p>
            </div>
          </div>

          <div class="info-section">
            <h4>👤 Данные отправителя</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">ФИО:</span>
                <span class="value">{{ selectedAppeal.user_info.full_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Email:</span>
                <span class="value">{{ selectedAppeal.user_info.email || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Телефон:</span>
                <span class="value">{{ selectedAppeal.user_info.phone || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Общежитие:</span>
                <span class="value">{{ selectedAppeal.user_info.hostel || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Комната:</span>
                <span class="value">{{ selectedAppeal.user_info.room_number || '-' }}</span>
              </div>
              <div class="info-item full-width">
                <span class="label">Институт:</span>
                <span class="value">{{ selectedAppeal.user_info.university || '-' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.all-appeals {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
  flex: 1;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 15px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
}

.appeals-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-bottom: 20px;
}

.appeal-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.appeal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
  flex-wrap: wrap;
  gap: 10px;
}

.appeal-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.appeal-title h3 {
  margin: 0;
  font-size: 18px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.warning {
  background: #fff3cd;
  color: #856404;
}

.status-badge.primary {
  background: #cce5ff;
  color: #004085;
}

.status-badge.success {
  background: #d4edda;
  color: #155724;
}

.appeal-date {
  color: #666;
  font-size: 12px;
}

.appeal-info {
  margin-bottom: 16px;
}

.info-row {
  margin-bottom: 12px;
}

.info-label {
  font-weight: bold;
  margin-right: 12px;
  color: #555;
}

.appeal-message {
  margin: 8px 0 0 0;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
  color: #333;
  line-height: 1.5;
}

.appeal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  align-items: center;
  flex-wrap: wrap;
}

.btn-detail {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  background: #6c757d;
  color: white;
}

.btn-detail:hover {
  background: #5a6268;
}

.status-select {
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  border: 1px solid;
}

.status-select-inline {
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  border: 1px solid;
}

.loading,
.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 650px;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  background: white;
  z-index: 1;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
}

.info-section {
  margin-bottom: 24px;
}

.info-section h4 {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
  color: #3c5ba4;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  margin-bottom: 8px;
}

.info-item.full-width {
  grid-column: span 2;
}

.info-item .label {
  font-weight: bold;
  margin-right: 8px;
  color: #555;
  display: inline-block;
  min-width: 90px;
}

.info-item .value {
  color: #333;
}

.appeal-text {
  margin-top: 8px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
  color: #333;
  line-height: 1.5;
}
</style>