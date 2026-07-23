import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../store/auth";

const routes = [
  { path: "/login", name: "login", component: () => import("../views/Login.vue"), meta: { guestOnly: true } },
  { path: "/register", name: "register", component: () => import("../views/Register.vue"), meta: { guestOnly: true } },
  { path: "/", name: "dashboard", component: () => import("../views/Dashboard.vue"), meta: { requiresAuth: true } },
  { path: "/profile", name: "profile", component: () => import("../views/Profile.vue"), meta: { requiresAuth: true } },
  { path: "/admin", name: "admin", component: () => import("../views/Admin.vue"), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: "/chat", name: "chat", component: () => import("../views/Chat.vue"), meta: { requiresAuth: true } },
  { path: "/about", name: "about", component: () => import("../views/About.vue"), meta: { requiresAuth: true } },
  { path: "/admin/about-editor", name: "admin-about-editor", component: () => import("../views/AdminAboutEditor.vue"), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: "/admin/chat", name: "admin-chat", component: () => import("../views/AdminChat.vue"), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: "/tools/lesson-plan", name: "lesson-plan", component: () => import("../views/LessonPlanTool.vue"), meta: { requiresAuth: true } },
  { path: "/tools/slide", name: "slide", component: () => import("../views/SlideTool.vue"), meta: { requiresAuth: true } },
  { path: "/tools/test", name: "test", component: () => import("../views/TestTool.vue"), meta: { requiresAuth: true } },
  { path: "/question-bank", name: "question-bank", component: () => import("../views/QuestionBank.vue"), meta: { requiresAuth: true } },
  { path: "/tools/curriculum", name: "curriculum", component: () => import("../views/CurriculumTool.vue"), meta: { requiresAuth: true } },
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const auth = useAuthStore();

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { name: "dashboard" };
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: "dashboard" };
  }
  return true;
});

export default router;
