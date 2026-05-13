import { createRouter, createWebHistory } from "vue-router";
import api from "../api";
import { hasAuthenticatedSession, setAuthenticated } from "../auth";

import EntranceView from "../views/EntranceView.vue";
import RegisterView from "../views/RegisterView.vue";
import HomeView from "../views/HomeView.vue";
import ProfileView from "../views/ProfileView.vue";
import ProfileEditView from "../views/ProfileEditView.vue"; // Добавляем импорт
import AppealCreateView from "../views/AppealCreateView.vue";
import AppealListView from "../views/AppealListView.vue";

const router = createRouter({
  history: createWebHistory(),

  routes: [
    {
      path: "/",
      component: EntranceView,
      meta: {
        guestOnly: true
      }
    },
    {
      path: "/registration",
      component: RegisterView,
      meta: {
        guestOnly: true
      }
    },
    {
      path: "/home",
      component: HomeView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: "/profile",
      component: ProfileView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: "/profile/edit",  // Добавляем маршрут редактирования
      component: ProfileEditView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: "/appeal",
      component: AppealListView,
      meta: {
        requiresAuth: true,
        appealMode: "active"
      }
    },
    {
      path: "/appeal/history",
      component: AppealListView,
      meta: {
        requiresAuth: true,
        appealMode: "history"
      }
    },
    {
      path: "/appeal/new",
      component: AppealCreateView,
      meta: {
        requiresAuth: true
      }
    }
  ],
});

router.beforeEach(async (to) => {
  if (to.meta.requiresAuth && hasAuthenticatedSession()) {
    return true;
  }

  try {
    const response = await api.get("/account/me/");
    const isAuthenticated = response.data.isAuthenticated;
    setAuthenticated(isAuthenticated);

    if (to.meta.requiresAuth && !isAuthenticated) {
      return "/";
    }
    if (to.meta.guestOnly && isAuthenticated) {
      return "/home";
    }
  } catch {
    setAuthenticated(false);

    if (to.meta.requiresAuth) {
      return "/";
    }
  }
});

export default router;
