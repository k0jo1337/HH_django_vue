<script setup>
import { ref, onMounted } from "vue";
import api from "../../api";
import ExecutorManager from "../../components/ExecutorManager.vue";

const appeals = ref([]);
const loading = ref(true);
const selectedAppeal = ref(null);
const showModal = ref(false);
const showReportModal = ref(false);
const showExecutorsModal = ref(false);
const showFilters = ref(false);

// Фильтры
const filters = ref({
  status: "",
  specialist: "",
  executor: "",
  date_from: "",
  date_to: "",
});

// Списки для фильтров
const executorsList = ref([]);
const specialistsList = [
  { value: "", label: "Все специалисты" },
  { value: "plumber", label: "Сантехник" },
  { value: "carpenter", label: "Плотник" },
  { value: "electrician", label: "Электрик" },
  { value: "other", label: "Другое" },
];

const statusList = [
  { value: "", label: "Все статусы" },
  { value: "new", label: "Новые" },
  { value: "in_progress", label: "В работе" },
  { value: "completed", label: "Завершённые" },
];

// Отчет
const reportData = ref(null);
const reportLoading = ref(false);
const reportPeriod = ref({
  date_from: "",
  date_to: "",
});

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

// Загрузка списка исполнителей
async function loadExecutors() {
  try {
    const response = await api.get("/executors/");
    executorsList.value = response.data.executors;
  } catch (error) {
    console.error("Ошибка загрузки исполнителей:", error);
  }
}

// Загрузка заявок с фильтрацией
async function loadAppeals() {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    if (filters.value.status) params.append("status", filters.value.status);
    if (filters.value.specialist) params.append("specialist", filters.value.specialist);
    if (filters.value.executor) params.append("executor", filters.value.executor);
    if (filters.value.date_from) params.append("date_from", filters.value.date_from);
    if (filters.value.date_to) params.append("date_to", filters.value.date_to);

    const url = `/appeals/all/${params.toString() ? `?${params.toString()}` : ""}`;
    const response = await api.get(url);
    appeals.value = response.data.appeals;
  } catch (error) {
    console.error("Ошибка загрузки заявок:", error);
  } finally {
    loading.value = false;
  }
}

// Сброс фильтров
function resetFilters() {
  filters.value = {
    status: "",
    specialist: "",
    executor: "",
    date_from: "",
    date_to: "",
  };
  loadAppeals();
}

// Обновление статуса
async function updateStatus(appealId, newStatus) {
  try {
    await api.patch(`/appeals/${appealId}/status/`, { status: newStatus });
    await loadAppeals();
    if (showModal.value && selectedAppeal.value?.appeal?.id === appealId) {
      await viewAppealDetails(appealId);
    }
  } catch (error) {
    console.error("Ошибка обновления статуса:", error);
  }
}

// Назначение исполнителя
async function assignExecutor(appealId, executorId) {
  try {
    await api.patch(`/appeals/${appealId}/assign/`, { executor: executorId });
    await loadAppeals();
    if (showModal.value && selectedAppeal.value?.appeal?.id === appealId) {
      await viewAppealDetails(appealId);
    }
  } catch (error) {
    console.error("Ошибка назначения исполнителя:", error);
  }
}

// Детали заявки
async function viewAppealDetails(appealId) {
  try {
    const response = await api.get(`/appeals/${appealId}/detail/`);
    selectedAppeal.value = response.data;
    showModal.value = true;
  } catch (error) {
    console.error("Ошибка загрузки деталей:", error);
  }
}

// Закрытие модального окна
function closeModal() {
  showModal.value = false;
  selectedAppeal.value = null;
}

// Формирование отчета
async function generateReport() {
  reportLoading.value = true;
  try {
    const params = new URLSearchParams();
    if (reportPeriod.value.date_from) params.append("date_from", reportPeriod.value.date_from);
    if (reportPeriod.value.date_to) params.append("date_to", reportPeriod.value.date_to);

    const response = await api.get(`/report/by-executor/${params.toString() ? `?${params.toString()}` : ""}`);
    reportData.value = response.data;
    showReportModal.value = true;
  } catch (error) {
    console.error("Ошибка загрузки отчета:", error);
  } finally {
    reportLoading.value = false;
  }
}

// Экспорт в CSV
async function exportToCSV() {
  try {
    const params = new URLSearchParams();
    if (filters.value.status) params.append("status", filters.value.status);
    if (filters.value.date_from) params.append("date_from", filters.value.date_from);
    if (filters.value.date_to) params.append("date_to", filters.value.date_to);

    const response = await api.get(`/export/csv/${params.toString() ? `?${params.toString()}` : ""}`, {
      responseType: 'blob'
    });

    // Создаем ссылку для скачивания
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const filename = `appeals_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Ошибка экспорта:", error);
    alert("Ошибка экспорта заявок");
  }
}

// Форматирование даты
function formatDate(dateString) {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleString();
}

onMounted(() => {
  loadExecutors();
  loadAppeals();
});
</script>

<template>
  <div class="all-appeals">
    <div class="page-header">
      <h1>Все обращения</h1>
      <div class="header-buttons">
        <button class="btn-filter" @click="showFilters = !showFilters">
          {{ showFilters ? "Скрыть фильтры" : "Показать фильтры" }}
        </button>
        <button class="btn-report" @click="generateReport">📊 Отчет по исполнителям</button>
        <button class="btn-export" @click="exportToCSV">📎 Экспорт в CSV</button>
        <button class="btn-executors" @click="showExecutorsModal = true">👥 Исполнители</button>
      </div>
    </div>

    <!-- Панель фильтров -->
    <div v-if="showFilters" class="filters-panel">
      <div class="filter-row">
        <div class="filter-group">
          <label>Статус</label>
          <select v-model="filters.status" @change="loadAppeals">
            <option v-for="status in statusList" :key="status.value" :value="status.value">
              {{ status.label }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Специалист</label>
          <select v-model="filters.specialist" @change="loadAppeals">
            <option v-for="spec in specialistsList" :key="spec.value" :value="spec.value">
              {{ spec.label }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Исполнитель</label>
          <select v-model="filters.executor" @change="loadAppeals">
            <option value="">Все исполнители</option>
            <option v-for="exec in executorsList" :key="exec.id" :value="exec.id">
              {{ exec.full_name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Дата от</label>
          <input type="date" v-model="filters.date_from" @change="loadAppeals">
        </div>

        <div class="filter-group">
          <label>Дата до</label>
          <input type="date" v-model="filters.date_to" @change="loadAppeals">
        </div>

        <div class="filter-actions">
          <button class="btn-reset" @click="resetFilters">Сбросить</button>
        </div>
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
          <div class="appeal-date">{{ formatDate(appeal.created_at) }}</div>
        </div>

        <div class="appeal-info">
          <div class="info-row">
            <span class="info-label">Специалист:</span>
            <span class="info-value">{{ appeal.specialist_label }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Исполнитель:</span>
            <select
              :value="appeal.executor_id"
              @change="assignExecutor(appeal.id, $event.target.value)"
              class="executor-select"
            >
              <option :value="null">Не назначен</option>
              <option v-for="exec in executorsList" :key="exec.id" :value="exec.id">
                {{ exec.full_name }}
              </option>
            </select>
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

    <!-- Модальное окно с деталями заявки -->
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
              <span class="label">Исполнитель:</span>
              <select
                :value="selectedAppeal.appeal.executor_id"
                @change="assignExecutor(selectedAppeal.appeal.id, $event.target.value)"
                class="executor-select-inline"
              >
                <option :value="null">Не назначен</option>
                <option v-for="exec in executorsList" :key="exec.id" :value="exec.id">
                  {{ exec.full_name }}
                </option>
              </select>
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
              <span class="value">{{ formatDate(selectedAppeal.appeal.created_at) }}</span>
            </div>
            <div class="info-item" v-if="selectedAppeal.appeal.completed_at">
              <span class="label">Выполнено:</span>
              <span class="value">{{ formatDate(selectedAppeal.appeal.completed_at) }}</span>
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

    <!-- Модальное окно с отчетом -->
    <div v-if="showReportModal" class="modal-overlay" @click.self="showReportModal = false">
      <div class="modal-content report-modal">
        <div class="modal-header">
          <h3>Отчет по исполнителям</h3>
          <button class="close-btn" @click="showReportModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="report-period">
            <div class="filter-group">
              <label>Дата от</label>
              <input type="date" v-model="reportPeriod.date_from">
            </div>
            <div class="filter-group">
              <label>Дата до</label>
              <input type="date" v-model="reportPeriod.date_to">
            </div>
            <button class="btn-generate" @click="generateReport" :disabled="reportLoading">
              {{ reportLoading ? "Загрузка..." : "Обновить" }}
            </button>
          </div>

          <div v-if="reportData" class="report-results">
            <p class="report-period-info">
              Период: {{ reportData.period.date_from || "начало" }} — {{ reportData.period.date_to || "настоящее время" }}
            </p>
            <table class="report-table">
              <thead>
                <tr>
                  <th>Исполнитель</th>
                  <th>Выполнено заявок</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in reportData.report" :key="item.executor_id">
                  <td>{{ item.executor_name }}</td>
                  <td class="text-center">{{ item.total_completed }}</td>
                </tr>
                <tr v-if="reportData.report.length === 0">
                  <td colspan="2" class="text-center">Нет данных за выбранный период</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно управления исполнителями -->
    <div v-if="showExecutorsModal" class="modal-overlay" @click.self="showExecutorsModal = false">
      <div class="modal-content executor-modal">
        <div class="modal-header">
          <h3>Управление исполнителями</h3>
          <button class="close-btn" @click="showExecutorsModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <ExecutorManager />
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

.header-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-filter, .btn-report, .btn-export, .btn-executors {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-filter {
  background: #6c757d;
  color: white;
}

.btn-report {
  background: #28a745;
  color: white;
}

.btn-export {
  background: #17a2b8;
  color: white;
}

.btn-executors {
  background: #6f42c1;
  color: white;
}

.filters-panel {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-size: 12px;
  font-weight: bold;
  color: #555;
}

.filter-group select, .filter-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  min-width: 150px;
}

.filter-actions {
  display: flex;
  gap: 10px;
}

.btn-reset {
  padding: 8px 16px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
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

.status-select, .executor-select {
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  border: 1px solid;
}

.status-select-inline, .executor-select-inline {
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  border: 1px solid;
}

.loading, .empty-state {
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

.executor-modal {
  max-width: 700px;
}

.report-modal {
  max-width: 550px;
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

/* Отчет */
.report-period {
  display: flex;
  gap: 15px;
  align-items: flex-end;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.btn-generate {
  padding: 8px 16px;
  background: #3c5ba4;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.report-period-info {
  margin-bottom: 15px;
  color: #666;
  font-size: 14px;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
}

.report-table th, .report-table td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: left;
}

.report-table th {
  background: #f5f5f5;
  font-weight: bold;
}

.text-center {
  text-align: center;
}
</style>