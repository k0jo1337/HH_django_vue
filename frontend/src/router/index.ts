import { createRouter, createWebHistory } from "vue-router";
import api from "../api";

import EntranceView from "../views/EntranceView.vue";
import RegisterView from "../views/RegisterView.vue";
import HomeView from "../views/HomeView.vue";
import ProfileView from "../views/ProfileView.vue";

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
    }
  ],
});

router.beforeEach(async (to) => {

  try {

    const response = await api.get("/account/me/")

    const isAuthenticated =
      response.data.isAuthenticated
    console.log(isAuthenticated)
    if (to.meta.requiresAuth && !isAuthenticated) {
      return "/"
    }

    if (to.meta.guestOnly && isAuthenticated) {
      return "/home"
    }

  } catch {

    if (to.meta.requiresAuth) {
      return "/"
    }

  }

})

export default router;
