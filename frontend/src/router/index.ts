import { createRouter, createWebHistory } from "vue-router";
import api from "../api";
import { hasAuthenticatedSession, setAuthenticated, setEmployee, isEmployeeUser } from "../auth";

import EntranceView from "../views/EntranceView.vue";
import RegisterView from "../views/RegisterView.vue";
import HomeView from "../views/HomeView.vue";
import InfoView from "../views/InfoView.vue";
import ProfileView from "../views/ProfileView.vue";
import ProfileEditView from "../views/ProfileEditView.vue";
import AppealCreateView from "../views/AppealCreateView.vue";
import AppealListView from "../views/AppealListView.vue";
import ResetPasswordView from "../views/ResetPasswordView.vue";
import AllAppealsView from "../views/employee/AllAppealsView.vue";

const router = createRouter({
  history: createWebHistory(),

  routes: [
    {
      path: "/",
      component: EntranceView,
      meta: { guestOnly: true }
    },
    {
      path: "/registration",
      component: RegisterView,
      meta: { guestOnly: true }
    },
    {
      path: "/home",
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: "/info",
      component: InfoView,
      meta: { requiresAuth: true }
    },
    {
      path: "/profile",
      component: ProfileView,
      meta: { requiresAuth: true }
    },
    {
      path: "/profile/edit",
      component: ProfileEditView,
      meta: { requiresAuth: true }
    },
    {
      path: "/appeal",
      component: AppealListView,
      meta: { requiresAuth: true, appealMode: "active" }
    },
    {
      path: "/appeal/history",
      component: AppealListView,
      meta: { requiresAuth: true, appealMode: "history" }
    },
    {
      path: "/appeal/new",
      component: AppealCreateView,
      meta: { requiresAuth: true }
    },
    {
      path: "/reset-password/:uid/:token/",
      component: ResetPasswordView,
      meta: { guestOnly: true }
    },
    {
      path: "/employee/appeals",
      component: AllAppealsView,
      meta: { requiresAuth: true, employeeOnly: true }
    }
  ],
});

router.beforeEach(async (to) => {
  // Если уже есть сессия
  if (to.meta.requiresAuth && hasAuthenticatedSession()) {
    if (to.meta.employeeOnly && !isEmployeeUser()) {
      return "/home";
    }
    return true;
  }

  try {
    const response = await api.get("/account/me/");
    const isAuthenticated = response.data.isAuthenticated;
    setAuthenticated(isAuthenticated);

    // Получаем роль пользователя
    try {
      const roleResponse = await api.get("/account/role/");
      setEmployee(roleResponse.data.is_employee);
    } catch {
      setEmployee(false);
    }

    if (to.meta.requiresAuth && !isAuthenticated) {
      return "/";
    }
    if (to.meta.guestOnly && isAuthenticated) {
      return "/home";
    }
    if (to.meta.employeeOnly && !isEmployeeUser()) {
      return "/home";
    }
  } catch {
    setAuthenticated(false);
    setEmployee(false);
    if (to.meta.requiresAuth) {
      return "/";
    }
  }
});

export default router;
