<template>
  <div class="max-w-3xl mx-auto">
    <!-- Hero -->
    <div class="relative rounded-xl2 overflow-hidden mb-6 bg-gradient-to-br from-brand-600 via-brand-500 to-accent-500 text-white">
      <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(circle at 20% 20%, white 1px, transparent 1px); background-size: 24px 24px;"></div>
      <div class="relative px-6 py-10 sm:px-10 sm:py-14 text-center">
        <div class="w-16 h-16 rounded-2xl bg-white/15 backdrop-blur mx-auto flex items-center justify-center text-2xl font-bold mb-4 border border-white/20">
          AI
        </div>
        <h1 class="text-2xl sm:text-3xl font-bold">ជំនួយការគ្រូ AI</h1>
        <p class="text-white/80 text-sm mt-1">AI Teaching Toolkit សម្រាប់គ្រូបង្រៀនកម្ពុជា</p>
      </div>
    </div>

    <div class="card mb-6">
      <h2 class="font-semibold text-slate-800 mb-2 flex items-center gap-2">🎯 បេសកកម្ម</h2>
      <p class="text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">{{ settings.mission_text }}</p>
    </div>

    <div class="card mb-6">
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

    <!-- Contact person card -->
    <div class="card mb-6 overflow-hidden !p-0">
      <div class="bg-gradient-to-r from-brand-50 to-accent-400/10 px-6 pt-8 pb-6 sm:px-8 flex flex-col sm:flex-row items-center sm:items-end gap-5">
        <div class="w-28 h-28 rounded-2xl bg-white shadow-soft overflow-hidden shrink-0 border-4 border-white">
          <img v-if="settings.contact_photo_url" :src="resolvePhotoUrl(settings.contact_photo_url)" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center bg-brand-100 text-brand-600 text-3xl font-bold">
            {{ (settings.contact_name || "?").charAt(0) }}
          </div>
        </div>
        <div class="text-center sm:text-left">
          <p class="text-xl font-bold text-slate-800">{{ settings.contact_name }}</p>
          <p class="text-sm text-slate-500 mt-0.5">{{ settings.contact_specialty }} · {{ settings.contact_school }}</p>
        </div>
      </div>

      <div class="px-6 py-5 sm:px-8">
        <p class="text-sm text-slate-600 leading-relaxed mb-4">
          មានសំណួរ ឬជួបបញ្ហាក្នុងការប្រើប្រាស់? ទាក់ទងមកកាន់ពួកយើងតាមរយៈ Chat ក្នុងកម្មវិធីបានផ្ទាល់ ឬតាមរយៈបណ្តាញសង្គមខាងក្រោម។
        </p>
        <div class="flex flex-wrap gap-2 mb-5">
          <a
            v-if="settings.contact_facebook"
            :href="`https://facebook.com/${settings.contact_facebook}`"
            target="_blank"
            class="inline-flex items-center gap-1.5 text-xs font-medium bg-blue-50 text-blue-600 px-3 py-1.5 rounded-lg hover:bg-blue-100 transition-colors"
          >
            📘 {{ settings.contact_facebook }}
          </a>
          <span
            v-if="settings.contact_telegram"
            class="inline-flex items-center gap-1.5 text-xs font-medium bg-sky-50 text-sky-600 px-3 py-1.5 rounded-lg"
          >
            ✈️ {{ settings.contact_telegram }}
          </span>
        </div>
        <RouterLink to="/chat" class="btn-primary inline-flex text-sm">💬 ជជែកជាមួយ Admin</RouterLink>
      </div>
    </div>

    <p v-if="auth.isAdmin" class="text-center mb-5">
      <RouterLink to="/admin/about-editor" class="text-sm text-brand-600 hover:underline">✏️ កែសម្រួលព័ត៌មានទំព័រនេះ</RouterLink>
    </p>

    <p class="text-center text-xs text-slate-300">កំណែ 1.0 · បង្កើតឡើងសម្រាប់គ្រូបង្រៀនកម្ពុជា</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api, { resolvePhotoUrl } from "../api/axios";
import { useAuthStore } from "../store/auth";

const auth = useAuthStore();
const settings = ref({});

onMounted(async () => {
  const { data } = await api.get("/settings/about");
  settings.value = data;
});
</script>
