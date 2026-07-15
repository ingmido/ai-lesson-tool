<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-slate-800 mb-1">ប្រវត្តិរូប</h1>
    <p class="text-slate-400 text-sm mb-6">គ្រប់គ្រងព័ត៌មានផ្ទាល់ខ្លួនរបស់អ្នក</p>

    <form @submit.prevent="handleSave" class="card space-y-4">
      <div v-if="message" :class="messageOk ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'" class="rounded-xl text-sm px-4 py-3">
        {{ message }}
      </div>

      <div class="flex items-center gap-4">
        <div class="w-20 h-20 rounded-full bg-slate-100 overflow-hidden flex items-center justify-center shrink-0">
          <img v-if="photoPreview" :src="photoPreview" class="w-full h-full object-cover" />
          <span v-else class="text-slate-300 text-3xl">📷</span>
        </div>
        <div class="flex-1">
          <label class="label mb-1">ប្តូររូបថត</label>
          <input type="file" accept="image/*" @change="onPhoto" class="text-sm text-slate-500" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="col-span-2">
          <label class="label">ឈ្មោះពេញ</label>
          <input v-model="form.full_name" type="text" class="input-field" />
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
          <label class="label">ពាក្យសម្ងាត់ថ្មី (ទុកទទេ បើមិនប្តូរ)</label>
          <input v-model="form.password" type="password" class="input-field" />
        </div>
      </div>

      <button type="submit" class="btn-primary" :disabled="loading">
        {{ loading ? "កំពុងរក្សាទុក..." : "រក្សាទុកការផ្លាស់ប្តូរ" }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useAuthStore } from "../store/auth";
import api from "../api/axios";

const auth = useAuthStore();
const form = reactive({
  full_name: "",
  gender: "",
  date_of_birth: "",
  school_name: "",
  subject: "",
  password: "",
});
const photoFile = ref(null);
const photoPreview = ref("");
const loading = ref(false);
const message = ref("");
const messageOk = ref(true);

onMounted(() => {
  const u = auth.user;
  if (u) {
    form.full_name = u.full_name || "";
    form.gender = u.gender || "";
    form.date_of_birth = u.date_of_birth || "";
    form.school_name = u.school_name || "";
    form.subject = u.subject || "";
    if (u.photo_path) photoPreview.value = `/uploads/${u.photo_path}`;
  }
});

function onPhoto(e) {
  const file = e.target.files[0];
  if (!file) return;
  photoFile.value = file;
  photoPreview.value = URL.createObjectURL(file);
}

async function handleSave() {
  loading.value = true;
  message.value = "";
  try {
    const fd = new FormData();
    Object.entries(form).forEach(([k, v]) => {
      if (v) fd.append(k, v);
    });
    if (photoFile.value) fd.append("photo", photoFile.value);
    const { data } = await api.put("/profile/me", fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    auth.user = data;
    localStorage.setItem("user", JSON.stringify(data));
    message.value = "រក្សាទុកជោគជ័យ!";
    messageOk.value = true;
    form.password = "";
  } catch (e) {
    message.value = e.response?.data?.error || "មានបញ្ហា សូមព្យាយាមម្តងទៀត";
    messageOk.value = false;
  } finally {
    loading.value = false;
  }
}
</script>
