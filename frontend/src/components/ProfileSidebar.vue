<script setup>
import { computed, ref } from "vue";
import { isEmployeeUser } from "../auth";
import api from "../api";

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
const debtorsFileInput = ref(null);
const imageLoadFailed = ref(false);
const debtorsUploading = ref(false);
const debtorsUploadMessage = ref("");
const debtorsUploadFailed = ref(false);

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

const moneyFormatter = new Intl.NumberFormat("ru-RU", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const balanceLabel = computed(() => {
  const debit = Number(props.user.balance_debit || 0);
  const credit = Number(props.user.balance_credit || 0);
  const balance = credit - debit;

  if (balance < 0) {
    return `Баланс: долг ${moneyFormatter.format(Math.abs(balance))} ₽`;
  }
  if (balance > 0) {
    return `Баланс: переплата ${moneyFormatter.format(balance)} ₽`;
  }
  return "Баланс: долга нет";
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

const openDebtorsFileDialog = () => {
  if (!debtorsUploading.value) {
    debtorsFileInput.value?.click();
  }
};

const onDebtorsFileChange = async (event) => {
  const file = event.target.files?.[0];
  event.target.value = "";
  if (!file) {
    return;
  }

  debtorsUploading.value = true;
  debtorsUploadMessage.value = "";
  debtorsUploadFailed.value = false;

  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post("/account/debtors/upload/", formData);
    const firstUnmatched = response.data.unmatched?.[0];
    const details = firstUnmatched
      ? ` Первая несопоставленная строка ${firstUnmatched.row}: ${firstUnmatched.reason}.`
      : "";
    debtorsUploadFailed.value = response.data.unmatched_count > 0;
    debtorsUploadMessage.value = `${response.data.message}${details}`;
  } catch (error) {
    const data = error.response?.data;
    const firstUnmatched = data?.unmatched?.[0];
    const details = firstUnmatched
      ? ` Строка ${firstUnmatched.row}: ${firstUnmatched.reason}.`
      : "";
    debtorsUploadFailed.value = true;
    debtorsUploadMessage.value = `${data?.error || "Не удалось обработать Excel-файл."}${details}`;
  } finally {
    debtorsUploading.value = false;
  }
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
        <p v-if="!isEmployee">{{ balanceLabel }}</p>
      </div>
    </div>

    <div class="profil_list_item_2">
      <!-- Загрузка должников для сотрудников, активные обращения для студентов -->
      <div class="profil_inf">
        <div v-if="isEmployee" class="debtors-upload-control">
          <button
            class="debtors-upload-button"
            type="button"
            :disabled="debtorsUploading"
            @click="openDebtorsFileDialog"
          >
            {{ debtorsUploading ? "Обработка файла..." : "Загрузить должников" }}
          </button>
          <input
            ref="debtorsFileInput"
            class="debtors-file-input"
            type="file"
            accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            @change="onDebtorsFileChange"
          >
          <p
            v-if="debtorsUploadMessage"
            class="debtors-upload-message"
            :class="{ 'debtors-upload-message-error': debtorsUploadFailed }"
            role="status"
          >
            {{ debtorsUploadMessage }}
          </p>
        </div>
        <RouterLink v-else to="/appeal">Активные обращения</RouterLink>
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

.debtors-upload-button {
  padding: 0;
  border: 0;
  background: transparent;
  color: #3c5ba4;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.debtors-upload-button:disabled {
  cursor: wait;
  opacity: 0.65;
}

.debtors-upload-control {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  width: 100%;
}

.debtors-file-input {
  display: none;
}

.debtors-upload-message {
  margin: 0;
  color: #287a42;
  font-size: 12px;
  line-height: 1.3;
}

.debtors-upload-message-error {
  color: #b42318;
}
</style>
