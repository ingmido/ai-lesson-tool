<template>
  <div v-if="isBareLayout">
    <router-view />
  </div>

  <div v-else class="min-h-screen flex bg-slate-50">
    <!-- Sidebar -->
    <aside
      class="fixed lg:static inset-y-0 left-0 z-30 w-64 bg-white border-r border-slate-100 transform transition-transform lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="h-full flex flex-col">
        <div class="px-6 py-6 flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center text-white font-bold shadow-soft">
            AI
          </div>
          <div>
            <div class="font-semibold text-slate-800 leading-tight">ជំនួយការគ្រូ</div>
            <div class="text-xs text-slate-400">AI Teaching Toolkit</div>
          </div>
        </div>

        <nav class="flex-1 px-3 space-y-1 overflow-y-auto">
          <RouterLink to="/" class="nav-link" active-class="nav-link-active">
            <span>🏠</span> ទំព័រដើម
          </RouterLink>

          <div class="pt-4 pb-1 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wide">
            ឧបករណ៍ AI
          </div>
          <RouterLink to="/tools/lesson-plan" class="nav-link" active-class="nav-link-active">
            <span>📝</span> កិច្ចតែងការបង្រៀន
          </RouterLink>
          <RouterLink to="/tools/slide" class="nav-link" active-class="nav-link-active">
            <span>🖥️</span> បង្កើត Slide
          </RouterLink>
          <RouterLink to="/tools/test" class="nav-link" active-class="nav-link-active">
            <span>🧪</span> តេស្តស្តង់ដារ
          </RouterLink>
          <RouterLink to="/tools/curriculum" class="nav-link" active-class="nav-link-active">
            <span>🗂️</span> បំបែងចែកកម្មវិធីសិក្សា
          </RouterLink>

          <div class="pt-4 pb-1 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wide">
            គណនី
          </div>
          <RouterLink to="/profile" class="nav-link" active-class="nav-link-active">
            <span>👤</span> ប្រវត្តិរូប
          </RouterLink>
          <RouterLink v-if="!auth.isAdmin" to="/chat" class="nav-link" active-class="nav-link-active">
            <span>💬</span> ជជែកជាមួយ Admin
          </RouterLink>
          <RouterLink v-if="auth.isAdmin" to="/admin/chat" class="nav-link" active-class="nav-link-active">
            <span>💬</span> សារគាំទ្រ
            <span v-if="adminUnread" class="ml-auto text-[10px] bg-red-500 text-white rounded-full px-1.5 py-0.5">
              {{ adminUnread }}
            </span>
          </RouterLink>
          <RouterLink v-if="auth.isAdmin" to="/admin" class="nav-link" active-class="nav-link-active">
            <span>⚙️</span> គ្រប់គ្រងអ្នកប្រើ
          </RouterLink>
          <RouterLink to="/about" class="nav-link" active-class="nav-link-active">
            <span>ℹ️</span> អំពីយើង
          </RouterLink>
        </nav>

        <div class="p-4 border-t border-slate-100">
          <div class="flex items-center gap-3 mb-3">
            <img
              v-if="auth.user?.photo_path"
              :src="`${apiOrigin}/uploads/${auth.user.photo_path}`"
              class="w-9 h-9 rounded-full object-cover"
            />
            <div v-else class="w-9 h-9 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center font-semibold">
              {{ (auth.user?.full_name || "?").charAt(0) }}
            </div>
            <div class="min-w-0">
              <div class="text-sm font-medium text-slate-800 truncate">{{ auth.user?.full_name }}</div>
              <div class="text-xs text-slate-400 truncate">{{ auth.user?.role === 'admin' ? 'អ្នកគ្រប់គ្រង' : 'គ្រូបង្រៀន' }}</div>
            </div>
          </div>
          <button class="btn-secondary w-full text-sm" @click="handleLogout">ចាកចេញ</button>
        </div>
      </div>
    </aside>

    <div v-if="sidebarOpen" class="fixed inset-0 bg-black/30 z-20 lg:hidden" @click="sidebarOpen = false"></div>

    <!-- Main -->
    <div class="flex-1 min-w-0">
      <header class="sticky top-0 z-10 bg-white/80 backdrop-blur border-b border-slate-100 px-4 lg:px-8 py-3 flex items-center justify-between">
        <button class="lg:hidden text-slate-500" @click="sidebarOpen = true">☰</button>
        <div class="text-sm text-slate-400 hidden lg:block">សូមស្វាគមន៍មកកាន់ឧបករណ៍ AI សម្រាប់គ្រូបង្រៀន</div>
        <div></div>
      </header>
      <main class="p-4 lg:p-8">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "./store/auth";
import { API_ORIGIN } from "./api/axios";
import api from "./api/axios";

const apiOrigin = API_ORIGIN;
const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const sidebarOpen = ref(false);
const adminUnread = ref(0);

const isBareLayout = computed(() => ["login", "register"].includes(route.name));

function handleLogout() {
  auth.logout();
  router.push({ name: "login" });
}

let unreadTimer = null;

async function pollAdminUnread() {
  if (!auth.isAdmin) return;
  try {
    const { data } = await api.get("/chat/admin/unread-total");
    adminUnread.value = data.unread;
  } catch {
    // ignore transient errors
  }
}

onMounted(() => {
  if (auth.isAuthenticated && auth.isAdmin) {
    pollAdminUnread();
    unreadTimer = setInterval(pollAdminUnread, 8000);
  }
});

watch(
  () => auth.isAuthenticated,
  (isAuth) => {
    if (isAuth && auth.isAdmin && !unreadTimer) {
      pollAdminUnread();
      unreadTimer = setInterval(pollAdminUnread, 8000);
    }
  }
);

onUnmounted(() => {
  if (unreadTimer) clearInterval(unreadTimer);
});
</script>

<style scoped>
.nav-link {
  @apply flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-50 hover:text-brand-700 text-sm font-medium transition-colors;
}
.nav-link-active {
  @apply bg-brand-50 text-brand-700;
}
</style>
