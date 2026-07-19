<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-brand-50 via-white to-accent-400/10 px-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-500 to-accent-500 mx-auto flex items-center justify-center text-white text-xl font-bold shadow-soft mb-3">
          AI
        </div>
        <h1 class="text-2xl font-bold text-slate-800">ជំនួយការគ្រូ AI</h1>
        <p class="text-slate-400 text-sm mt-1">ចូលគណនីរបស់អ្នក</p>
      </div>

      <form @submit.prevent="handleLogin" class="card space-y-4">
        <div v-if="error" class="rounded-xl bg-red-50 text-red-600 text-sm px-4 py-3">{{ error }}</div>

        <div>
          <label class="label">ឈ្មោះអ្នកប្រើ</label>
          <input v-model="username" type="text" class="input-field" required autofocus />
        </div>
        <div>
          <label class="label">ពាក្យសម្ងាត់</label>
          <input v-model="password" type="password" class="input-field" required />
        </div>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? "កំពុងចូល..." : "ចូលប្រើប្រាស់" }}
        </button>

        <p class="text-center text-sm text-slate-500">
          មិនទាន់មានគណនី?
          <RouterLink to="/register" class="text-brand-600 font-medium hover:underline">ចុះឈ្មោះ</RouterLink>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "../store/auth";

const username = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

async function handleLogin() {
  loading.value = true;
  error.value = "";
  try {
    await auth.login(username.value, password.value);
    router.push(route.query.redirect || "/");
  } catch (e) {
    error.value = e.response?.data?.error || "ការចូលបរាជ័យ សូមព្យាយាមម្តងទៀត";
  } finally {
    loading.value = false;
  }
}
</script>
