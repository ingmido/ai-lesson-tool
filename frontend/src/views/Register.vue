<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-brand-50 via-white to-accent-400/10 px-4 py-10">
    <div class="w-full max-w-lg">
      <div class="text-center mb-8">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-500 to-accent-500 mx-auto flex items-center justify-center text-white text-xl font-bold shadow-soft mb-3">
          AI
        </div>
        <h1 class="text-2xl font-bold text-slate-800">បង្កើតគណនីថ្មី</h1>
        <p class="text-slate-400 text-sm mt-1">សម្រាប់គ្រូបង្រៀន</p>
      </div>

      <form @submit.prevent="handleRegister" class="card space-y-4" enctype="multipart/form-data">
        <div v-if="error" class="rounded-xl bg-red-50 text-red-600 text-sm px-4 py-3">{{ error }}</div>

        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-full bg-slate-100 overflow-hidden flex items-center justify-center shrink-0">
            <img v-if="photoPreview" :src="photoPreview" class="w-full h-full object-cover" />
            <span v-else class="text-slate-300 text-2xl">📷</span>
          </div>
          <div class="flex-1">
            <label class="label mb-1">រូបថត</label>
            <input type="file" accept="image/*" @change="onPhoto" class="text-sm text-slate-500" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="col-span-2">
            <label class="label">ឈ្មោះពេញ</label>
            <input v-model="form.full_name" type="text" class="input-field" required />
          </div>
          <div>
            <label class="label">ភេទ</label>
            <select v-model="form.gender" class="input-field">
              <option value="">ជ្រើសរើស</option>
              <option value="ប្រុស">ប្រុស</option>
              <option value="ស្រី">ស្រី</option>
            </select>
          </div>
          <div>
            <label class="label">ថ្ងៃខែឆ្នាំកំណើត</label>
            <input v-model="form.date_of_birth" type="date" class="input-field" />
          </div>
          <div class="col-span-2">
            <label class="label">ឈ្មោះសាលា</label>
            <input v-model="form.school_name" type="text" class="input-field" />
          </div>
          <div class="col-span-2">
            <label class="label">មុខវិជ្ជា</label>
            <input v-model="form.subject" type="text" class="input-field" />
          </div>
          <div class="col-span-2">
            <label class="label">ឈ្មោះអ្នកប្រើ (Username)</label>
            <input v-model="form.username" type="text" class="input-field" required />
          </div>
          <div class="col-span-2">
            <label class="label">ពាក្យសម្ងាត់</label>
            <input v-model="form.password" type="password" class="input-field" required minlength="6" />
          </div>
        </div>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? "កំពុងបង្កើត..." : "ចុះឈ្មោះ" }}
        </button>

        <p class="text-center text-sm text-slate-500">
          មានគណនីរួចហើយ?
          <RouterLink to="/login" class="text-brand-600 font-medium hover:underline">ចូលប្រើ</RouterLink>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";

const auth = useAuthStore();
const router = useRouter();

const form = reactive({
  username: "",
  password: "",
  full_name: "",
  gender: "",
  date_of_birth: "",
  school_name: "",
  subject: "",
});
const photoFile = ref(null);
const photoPreview = ref("");
const loading = ref(false);
const error = ref("");

function onPhoto(e) {
  const file = e.target.files[0];
  if (!file) return;
  photoFile.value = file;
  photoPreview.value = URL.createObjectURL(file);
}

async function handleRegister() {
  loading.value = true;
  error.value = "";
  try {
    const fd = new FormData();
    Object.entries(form).forEach(([k, v]) => fd.append(k, v));
    if (photoFile.value) fd.append("photo", photoFile.value);
    await auth.register(fd);
    router.push("/");
  } catch (e) {
    error.value = e.response?.data?.error || "ការចុះឈ្មោះបរាជ័យ";
  } finally {
    loading.value = false;
  }
}
</script>
