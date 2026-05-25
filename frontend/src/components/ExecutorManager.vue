<script setup>
import { ref, onMounted } from "vue";
import api from "../api";

const executors = ref([]);
const loading = ref(false);
const showModal = ref(false);
const isEditing = ref(false);
const currentExecutor = ref(null);

const form = ref({
  first_name: "",
  last_name: "",
  middle_name: "",
  position: "",
  phone: "",
  work_phone: "",
  email: "",
});

async function loadExecutors() {
  loading.value = true;
  try {
    const response = await api.get("/executors/");
    executors.value = response.data.executors;
  } catch (error) {
    console.error("Ошибка загрузки исполнителей:", error);
  } finally {
    loading.value = false;
  }
}

async function saveExecutor() {
  try {
    if (isEditing.value) {
      await api.put(`/executors/${currentExecutor.value.id}/`, form.value);
    } else {
      await api.post("/executors/create/", form.value);
    }
    await loadExecutors();
    closeModal();
  } catch (error) {
    console.error("Ошибка сохранения:", error);
    alert(error.response?.data?.errors || "Ошибка сохранения");
  }
}

function editExecutor(executor) {
  currentExecutor.value = executor;
  form.value = {
    first_name: executor.first_name,
    last_name: executor.last_name,
    middle_name: executor.middle_name || "",
    position: executor.position || "",
    phone: executor.phone || "",
    work_phone: executor.work_phone || "",
    email: executor.email || "",
  };
  isEditing.value = true;
  showModal.value = true;
}

async function deleteExecutor(executorId) {
  if (confirm("Удалить этого исполнителя?")) {
    try {
      await api.delete(`/executors/${executorId}/delete/`);
      await loadExecutors();
    } catch (error) {
      console.error("Ошибка удаления:", error);
      alert("Ошибка удаления");
    }
  }
}

function openCreateModal() {
  isEditing.value = false;
  currentExecutor.value = null;
  form.value = {
    first_name: "",
    last_name: "",
    middle_name: "",
    position: "",
    phone: "",
    work_phone: "",
    email: "",
  };
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
}

onMounted(() => {
  loadExecutors();
});
</script>

<template>
  <div class="executor-manager">
    <div class="manager-header">
      <h3>👥 Исполнители</h3>
      <button class="btn-add" @click="openCreateModal">+ Добавить исполнителя</button>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else-if="executors.length === 0" class="empty-state">
      <p>Нет добавленных исполнителей</p>
    </div>

    <div v-else class="executors-list">
      <div v-for="exec in executors" :key="exec.id" class="executor-card">
        <div class="executor-info">
          <div class="executor-name">{{ exec.full_name }}</div>
          <div class="executor-details">
            <span v-if="exec.position">📌 {{ exec.position }}</span>
            <span v-if="exec.phone">📞 {{ exec.phone }}</span>
            <span v-if="exec.work_phone">🏢 {{ exec.work_phone }}</span>
            <span v-if="exec.email">📧 {{ exec.email }}</span>
          </div>
        </div>
        <div class="executor-actions">
          <button class="btn-edit" @click="editExecutor(exec)">✏️</button>
          <button class="btn-delete" @click="deleteExecutor(exec.id)">🗑️</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ isEditing ? "Редактировать исполнителя" : "Добавить исполнителя" }}</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveExecutor">
            <div class="form-row">
              <div class="form-group">
                <label>Фамилия *</label>
                <input v-model="form.last_name" type="text" required>
              </div>
              <div class="form-group">
                <label>Имя *</label>
                <input v-model="form.first_name" type="text" required>
              </div>
            </div>
            <div class="form-group">
              <label>Отчество</label>
              <input v-model="form.middle_name" type="text">
            </div>
            <div class="form-group">
              <label>Должность</label>
              <input v-model="form.position" type="text" placeholder="Например: Сантехник">
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Телефон</label>
                <input v-model="form.phone" type="tel" placeholder="+7 XXX XXX-XX-XX">
              </div>
              <div class="form-group">
                <label>Рабочий телефон</label>
                <input v-model="form.work_phone" type="tel" placeholder="Внутренний номер">
              </div>
            </div>
            <div class="form-group">
              <label>Email</label>
              <input v-model="form.email" type="email">
            </div>
            <div class="form-actions">
              <button type="button" @click="closeModal">Отмена</button>
              <button type="submit">Сохранить</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.executor-manager {
  background: white;
  border-radius: 12px;
  padding: 20px;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.manager-header h3 {
  margin: 0;
}

.btn-add {
  padding: 8px 16px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.executors-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.executor-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.executor-name {
  font-weight: bold;
  font-size: 16px;
}

.executor-details {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 6px;
  font-size: 13px;
  color: #666;
}

.executor-actions {
  display: flex;
  gap: 8px;
}

.btn-edit, .btn-delete {
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-edit {
  background: #ffc107;
  color: #333;
}

.btn-delete {
  background: #dc3545;
  color: white;
}

.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.form-row .form-group {
  flex: 1;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.form-actions button {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.form-actions button[type="button"] {
  background: #6c757d;
  color: white;
}

.form-actions button[type="submit"] {
  background: #3c5ba4;
  color: white;
}

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
  max-width: 500px;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
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

.loading, .empty-state {
  text-align: center;
  padding: 30px;
  color: #666;
}
</style>