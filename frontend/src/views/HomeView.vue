<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import api from "../api";
import { isEmployeeUser } from "../auth";

const news = ref([]);
const loading = ref(true);
const error = ref("");
const search = ref("");
const selectedPost = ref(null);
const isCreateModalOpen = ref(false);
const isAddButtonHovered = ref(false);
const isEditingPost = ref(false);
const createError = ref("");
const editError = ref("");
const createSubmitting = ref(false);
const editSubmitting = ref(false);
const deleteSubmitting = ref(false);
const imageInput = ref(null);
const editImageInput = ref(null);
const newsForm = reactive({
  title: "",
  summary: "",
  content: "",
  image: null,
});
const editForm = reactive({
  title: "",
  summary: "",
  content: "",
  image: null,
});

const canManageNews = computed(() => isEmployeeUser());

const filteredNews = computed(() => {
  const query = search.value.trim().toLowerCase();

  if (!query) {
    return news.value;
  }

  return news.value.filter((post) => {
    return [post.title, post.summary, post.content]
      .filter(Boolean)
      .some((value) => value.toLowerCase().includes(query));
  });
});

function formatDate(value) {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function openPost(post) {
  selectedPost.value = post;
  isEditingPost.value = false;
  editError.value = "";
}

function closePost() {
  if (editSubmitting.value || deleteSubmitting.value) {
    return;
  }

  selectedPost.value = null;
  isEditingPost.value = false;
  editError.value = "";
}

function resetNewsForm() {
  newsForm.title = "";
  newsForm.summary = "";
  newsForm.content = "";
  newsForm.image = null;
  createError.value = "";

  if (imageInput.value) {
    imageInput.value.value = "";
  }
}

function resetEditForm() {
  editForm.title = "";
  editForm.summary = "";
  editForm.content = "";
  editForm.image = null;
  editError.value = "";

  if (editImageInput.value) {
    editImageInput.value.value = "";
  }
}

function openCreateNews() {
  resetNewsForm();
  isCreateModalOpen.value = true;
}

function closeCreateNews() {
  if (createSubmitting.value) {
    return;
  }

  isCreateModalOpen.value = false;
  resetNewsForm();
}

function startEditPost() {
  if (!selectedPost.value) {
    return;
  }

  editForm.title = selectedPost.value.title || "";
  editForm.summary = selectedPost.value.summary || "";
  editForm.content = selectedPost.value.content || "";
  editForm.image = null;
  editError.value = "";
  isEditingPost.value = true;

  if (editImageInput.value) {
    editImageInput.value.value = "";
  }
}

function cancelEditPost() {
  if (editSubmitting.value) {
    return;
  }

  isEditingPost.value = false;
  resetEditForm();
}

function handleModalOverlayClick(event) {
  if (event.target === event.currentTarget) {
    closePost();
  }
}

function handleCreateOverlayClick(event) {
  if (event.target === event.currentTarget) {
    closeCreateNews();
  }
}

function handleImageChange(event) {
  const [file] = event.target.files || [];
  newsForm.image = file || null;
}

function handleEditImageChange(event) {
  const [file] = event.target.files || [];
  editForm.image = file || null;
}

function buildNewsFormData(form) {
  const formData = new FormData();
  formData.append("title", form.title.trim());
  formData.append("summary", form.summary.trim());
  formData.append("content", form.content.trim());

  if (form.image) {
    formData.append("image", form.image);
  }

  return formData;
}

function replaceNewsPost(updatedPost) {
  news.value = news.value.map((post) => (
    post.id === updatedPost.id ? updatedPost : post
  ));
  selectedPost.value = updatedPost;
}

async function loadNews() {
  loading.value = true;
  error.value = "";

  try {
    const response = await api.get("/news/");
    news.value = response.data.news || [];
  } catch {
    error.value = "Не удалось загрузить новости";
  } finally {
    loading.value = false;
  }
}

async function createNews() {
  createError.value = "";

  if (!newsForm.title.trim() || !newsForm.summary.trim()) {
    createError.value = "Заполните заголовок и краткое описание.";
    return;
  }

  createSubmitting.value = true;

  try {
    const response = await api.post("/news/", buildNewsFormData(newsForm));
    const createdPost = response.data.news;

    if (createdPost) {
      news.value = [createdPost, ...news.value];
    } else {
      await loadNews();
    }

    isCreateModalOpen.value = false;
    resetNewsForm();
  } catch (err) {
    const errors = err.response?.data?.errors;
    createError.value = errors
      ? Object.values(errors).join(" ")
      : "Не удалось добавить новость.";
  } finally {
    createSubmitting.value = false;
  }
}

async function updateNews() {
  if (!selectedPost.value) {
    return;
  }

  editError.value = "";

  if (!editForm.title.trim() || !editForm.summary.trim()) {
    editError.value = "Заполните заголовок и краткое описание.";
    return;
  }

  editSubmitting.value = true;

  try {
    const response = await api.patch(
      `/news/${selectedPost.value.id}/`,
      buildNewsFormData(editForm),
    );
    const updatedPost = response.data.news;

    if (updatedPost) {
      replaceNewsPost(updatedPost);
    } else {
      await loadNews();
    }

    isEditingPost.value = false;
    resetEditForm();
  } catch (err) {
    const errors = err.response?.data?.errors;
    editError.value = errors
      ? Object.values(errors).join(" ")
      : "Не удалось сохранить изменения.";
  } finally {
    editSubmitting.value = false;
  }
}

async function deleteNews() {
  if (!selectedPost.value) {
    return;
  }

  const shouldDelete = window.confirm("Удалить эту новость?");
  if (!shouldDelete) {
    return;
  }

  deleteSubmitting.value = true;

  try {
    const deletedId = selectedPost.value.id;
    await api.delete(`/news/${deletedId}/`);
    news.value = news.value.filter((post) => post.id !== deletedId);
    selectedPost.value = null;
    isEditingPost.value = false;
    editError.value = "";
  } catch {
    editError.value = "Не удалось удалить новость.";
  } finally {
    deleteSubmitting.value = false;
  }
}

onMounted(loadNews);
</script>

<template>
  <main class="news-page">
    <section class="news-shell">
      <div class="news-brand">
        <img src="/Hostel_logo.png" alt="Hostel Helper">
      </div>

      <form class="news-search" @submit.prevent>
        <input v-model="search" type="search" placeholder="Ваш запрос" aria-label="Поиск новостей">
        <button type="submit">Поиск</button>
      </form>

      <p v-if="loading" class="news-state">Загрузка новостей...</p>
      <p v-else-if="error" class="news-state news-state-error">{{ error }}</p>
      <p v-else-if="!filteredNews.length" class="news-state">Новостей пока нет</p>

      <div v-else class="news-list custom-scroll">
        <article v-for="post in filteredNews" :key="post.id" class="news-card">
          <div v-if="post.image" class="news-card-image">
            <img :src="post.image" :alt="post.title">
          </div>

          <div class="news-card-body">
            <time class="news-date" :datetime="post.created_at">
              {{ formatDate(post.created_at) }}
            </time>

            <div class="news-card-main">
              <p class="news-summary">{{ post.summary }}</p>
              <h2>{{ post.title }}</h2>
            </div>

            <button
              v-if="post.content || canManageNews"
              class="news-more"
              type="button"
              @click="openPost(post)"
            >
              Подробнее...
            </button>
          </div>
        </article>
      </div>
    </section>

    <button
      v-if="canManageNews"
      class="news-add-button"
      type="button"
      aria-label="Добавить новость"
      title="Добавить новость"
      @mouseenter="isAddButtonHovered = true"
      @mouseleave="isAddButtonHovered = false"
      @click="openCreateNews"
    >
      <img
        class="news-add-icon"
        :src="isAddButtonHovered ? '/edit-pencil.gif' : '/edit-pencil-static.png'"
        alt=""
      >
    </button>

    <div v-if="selectedPost" class="news-modal-overlay" @click="handleModalOverlayClick">
      <article class="news-modal">
        <header class="news-modal-header">
          <div>
            <time class="news-modal-date" :datetime="selectedPost.created_at">
              {{ formatDate(selectedPost.created_at) }}
            </time>
            <h2>{{ isEditingPost ? "Редактировать новость" : selectedPost.title }}</h2>
          </div>

          <button class="news-modal-close" type="button" aria-label="Закрыть" @click="closePost">
            &times;
          </button>
        </header>

        <div v-if="!isEditingPost" class="news-modal-body custom-scroll">
          <img v-if="selectedPost.image" :src="selectedPost.image" :alt="selectedPost.title">
          <p class="news-modal-summary">{{ selectedPost.summary }}</p>
          <p class="news-modal-content">{{ selectedPost.content }}</p>

          <p v-if="editError" class="news-create-error">{{ editError }}</p>

          <div v-if="canManageNews" class="news-manage-actions">
            <button class="news-create-secondary" type="button" @click="startEditPost">
              Редактировать
            </button>
            <button
              class="news-delete-button"
              type="button"
              :disabled="deleteSubmitting"
              @click="deleteNews"
            >
              {{ deleteSubmitting ? "Удаление..." : "Удалить" }}
            </button>
          </div>
        </div>

        <form v-else class="news-create-form custom-scroll" @submit.prevent="updateNews">
          <label>
            <span>Заголовок</span>
            <input v-model="editForm.title" type="text" maxlength="160" required>
          </label>

          <label>
            <span>Краткое описание</span>
            <textarea v-model="editForm.summary" maxlength="280" rows="3" required></textarea>
          </label>

          <label>
            <span>Текст новости</span>
            <textarea v-model="editForm.content" rows="6"></textarea>
          </label>

          <label>
            <span>Новое изображение</span>
            <input ref="editImageInput" type="file" accept="image/*" @change="handleEditImageChange">
          </label>

          <p v-if="editError" class="news-create-error">{{ editError }}</p>

          <div class="news-create-actions">
            <button class="news-create-secondary" type="button" @click="cancelEditPost">
              Отмена
            </button>
            <button class="news-create-submit" type="submit" :disabled="editSubmitting">
              {{ editSubmitting ? "Сохранение..." : "Сохранить" }}
            </button>
          </div>
        </form>
      </article>
    </div>

    <div v-if="isCreateModalOpen" class="news-modal-overlay" @click="handleCreateOverlayClick">
      <article class="news-modal news-create-modal">
        <header class="news-modal-header">
          <div>
            <span class="news-modal-date">Новая публикация</span>
            <h2>Добавить новость</h2>
          </div>

          <button class="news-modal-close" type="button" aria-label="Закрыть" @click="closeCreateNews">
            &times;
          </button>
        </header>

        <form class="news-create-form custom-scroll" @submit.prevent="createNews">
          <label>
            <span>Заголовок</span>
            <input v-model="newsForm.title" type="text" maxlength="160" required>
          </label>

          <label>
            <span>Краткое описание</span>
            <textarea v-model="newsForm.summary" maxlength="280" rows="3" required></textarea>
          </label>

          <label>
            <span>Текст новости</span>
            <textarea v-model="newsForm.content" rows="6"></textarea>
          </label>

          <label>
            <span>Изображение</span>
            <input ref="imageInput" type="file" accept="image/*" @change="handleImageChange">
          </label>

          <p v-if="createError" class="news-create-error">{{ createError }}</p>

          <div class="news-create-actions">
            <button class="news-create-secondary" type="button" @click="closeCreateNews">
              Отмена
            </button>
            <button class="news-create-submit" type="submit" :disabled="createSubmitting">
              {{ createSubmitting ? "Сохранение..." : "Опубликовать" }}
            </button>
          </div>
        </form>
      </article>
    </div>
  </main>
</template>
