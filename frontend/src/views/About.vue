<template>
  <div class="max-w-3xl mx-auto">
    <div class="text-center mb-8">
      <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-500 to-accent-500 mx-auto flex items-center justify-center text-white text-2xl font-bold shadow-soft mb-4">
        AI
      </div>
      <h1 class="text-2xl font-bold text-slate-800">អំពី ជំនួយការគ្រូ AI</h1>
      <p class="text-slate-400 text-sm mt-1">AI Teaching Toolkit សម្រាប់គ្រូបង្រៀនកម្ពុជា</p>
    </div>

    <div class="card mb-5">
      <h2 class="font-semibold text-slate-800 mb-2 flex items-center gap-2">🎯 បេសកកម្ម</h2>
      <p class="text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">{{ settings.mission_text }}</p>
    </div>

    <div class="card mb-5">
      <h2 class="font-semibold text-slate-800 mb-3 flex items-center gap-2">✨ លក្ខណៈពិសេស</h2>
      <div class="grid sm:grid-cols-2 gap-3 text-sm">
        <div class="flex items-start gap-2">
          <span>📝</span>
          <div>
            <p class="font-medium text-slate-700">កិច្ចតែងការបង្រៀន</p>
            <p class="text-slate-400 text-xs">ពីរូបថត ឯកសារ ឬសរសេរផ្ទាល់</p>
          </div>
        </div>
        <div class="flex items-start gap-2">
          <span>🖥️</span>
          <div>
            <p class="font-medium text-slate-700">ស្លាយ PowerPoint</p>
            <p class="text-slate-400 text-xs">រចនាប័ទ្ម ៤ បែបឲ្យជ្រើសរើស</p>
          </div>
        </div>
        <div class="flex items-start gap-2">
          <span>🧪</span>
          <div>
            <p class="font-medium text-slate-700">តេស្តស្តង់ដារ</p>
            <p class="text-slate-400 text-xs">ជាមួយចម្លើយគំរូ</p>
          </div>
        </div>
        <div class="flex items-start gap-2">
          <span>🗂️</span>
          <div>
            <p class="font-medium text-slate-700">កម្មវិធីសិក្សា</p>
            <p class="text-slate-400 text-xs">បំបែងចែកតាមខែ/សប្តាហ៍</p>
          </div>
        </div>
        <div class="flex items-start gap-2">
          <span>💬</span>
          <div>
            <p class="font-medium text-slate-700">ជជែកជាមួយ Admin/AI</p>
            <p class="text-slate-400 text-xs">សំណួរ/បញ្ហាឆ្លើយភ្លាមៗ</p>
          </div>
        </div>
        <div class="flex items-start gap-2">
          <span>📄</span>
          <div>
            <p class="font-medium text-slate-700">ទាញយក Word/PDF/PPT</p>
            <p class="text-slate-400 text-xs">រក្សាទ្រង់ទ្រាយស្តង់ដារ</p>
          </div>
        </div>
      </div>
    </div>

    <div class="card mb-5">
      <h2 class="font-semibold text-slate-800 mb-2 flex items-center gap-2">📬 ទាក់ទង / ជំនួយ</h2>
      <p class="text-sm text-slate-600 leading-relaxed mb-3">
        មានសំណួរ ឬជួបបញ្ហាក្នុងការប្រើប្រាស់? ទាក់ទងមកកាន់ពួកយើងតាមរយៈ Chat ក្នុងកម្មវិធីបានផ្ទាល់ ឬតាមព័ត៌មានខាងក្រោម។
      </p>
      <div class="text-sm text-slate-600 space-y-1 mb-4">
        <p v-if="settings.contact_name"><span class="text-slate-400">ឈ្មោះ៖</span> {{ settings.contact_name }}</p>
        <p v-if="settings.contact_school"><span class="text-slate-400">សាលា៖</span> {{ settings.contact_school }}</p>
        <p v-if="settings.contact_specialty"><span class="text-slate-400">ឯកទេស៖</span> {{ settings.contact_specialty }}</p>
        <p v-if="settings.contact_facebook"><span class="text-slate-400">Facebook៖</span> {{ settings.contact_facebook }}</p>
        <p v-if="settings.contact_telegram"><span class="text-slate-400">Telegram៖</span> {{ settings.contact_telegram }}</p>
      </div>
      <RouterLink to="/chat" class="btn-primary inline-flex text-sm">💬 ជជែកជាមួយ Admin</RouterLink>
    </div>

    <p v-if="auth.isAdmin" class="text-center mb-5">
      <RouterLink to="/admin/about-editor" class="text-sm text-brand-600 hover:underline">✏️ កែសម្រួលព័ត៌មានទំព័រនេះ</RouterLink>
    </p>

    <p class="text-center text-xs text-slate-300">កំណែ 1.0 · បង្កើតឡើងសម្រាប់គ្រូបង្រៀនកម្ពុជា</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api/axios";
import { useAuthStore } from "../store/auth";

const auth = useAuthStore();
const settings = ref({});

onMounted(async () => {
  const { data } = await api.get("/settings/about");
  settings.value = data;
});
</script>
