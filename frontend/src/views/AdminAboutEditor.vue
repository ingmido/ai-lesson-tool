<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-slate-800 mb-1">✏️ កែសម្រួលទំព័រ "អំពីយើង"</h1>
    <p class="text-slate-400 text-sm mb-6">ព័ត៌មាននេះនឹងបង្ហាញដល់អ្នកប្រើទាំងអស់</p>

    <form @submit.prevent="handleSave" class="card space-y-4">
      <div v-if="message" :class="messageOk ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'" class="rounded-xl text-sm px-4 py-3">
        {{ message }}
      </div>

      <div>
        <label class="label">អត្ថបទបេសកកម្ម</label>
        <textarea v-model="form.mission_text" rows="5" class="input-field"></textarea>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="label">ឈ្មោះទំនាក់ទំនង</label>
          <input v-model="form.contact_name" type="text" class="input-field" />
        </div>
        <div>
          <label class="label">ឯកទេស</label>
          <input v-model="form.contact_specialty" type="text" class="input-field" />
        </div>
        <div class="col-span-2">
          <label class="label">ឈ្មោះសាលា</label>
          <input v-model="form.contact_school" type="text" class="input-field" />
        </div>
        <div>
          <label class="label">Facebook</label>
          <input v-model="form.contact_facebook" type="text" class="input-field" />
        </div>
        <div>
          <label class="label">Telegram</label>
          <input v-model="form.contact_telegram" type="text" class="input-field" />
        </div>
      </div>

      <div class="flex gap-3">
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? "កំពុងរក្សាទុក..." : "រក្សាទុក" }}
        </button>
        <RouterLink to="/about" class="btn-secondary">មើលទំព័រ</RouterLink>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import api from "../api/axios";

const form = reactive({
  mission_text: "",
  contact_name: "",
  contact_school: "",
  contact_specialty: "",
  contact_facebook: "",
  contact_telegram: "",
});
const loading = ref(false);
const message = ref("");
const messageOk = ref(true);

async function load() {
  const { data } = await api.get("/settings/about");
  Object.assign(form, data);
}

async function handleSave() {
  loading.value = true;
  message.value = "";
  try {
    await api.put("/settings/admin/about", { ...form });
    message.value = "រក្សាទុកជោគជ័យ!";
    messageOk.value = true;
  } catch (e) {
    message.value = e.response?.data?.error || "មានបញ្ហា សូមព្យាយាមម្តងទៀត";
    messageOk.value = false;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>
