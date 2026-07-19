<template>
  <div class="max-w-2xl mx-auto flex flex-col h-[calc(100vh-8rem)]">
    <div class="flex items-center justify-between mb-1">
      <h1 class="text-2xl font-bold text-slate-800">💬 ជជែកជាមួយ Admin</h1>
      <label class="flex items-center gap-2 text-xs text-slate-500 cursor-pointer select-none">
        <span>🤖 AI ឆ្លើយស្វ័យប្រវត្តិ</span>
        <button
          type="button"
          role="switch"
          :aria-checked="aiEnabled"
          @click="toggleAi"
          class="w-9 h-5 rounded-full transition-colors relative"
          :class="aiEnabled ? 'bg-brand-600' : 'bg-slate-300'"
        >
          <span
            class="absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform"
            :class="aiEnabled ? 'translate-x-4' : 'translate-x-0.5'"
          ></span>
        </button>
      </label>
    </div>
    <p class="text-slate-400 text-sm mb-4">
      {{ aiEnabled ? "AI ជំនួយការនឹងឆ្លើយភ្លាមៗ — admin អាចចូលចូលរួមបានគ្រប់ពេល" : "AI បិទ — សារនឹងទៅដល់ admin ផ្ទាល់តែម្តង" }}
    </p>

    <div class="card flex-1 flex flex-col overflow-hidden p-0">
      <div ref="scrollArea" class="flex-1 overflow-y-auto p-4 space-y-3">
        <div v-if="!messages.length" class="text-center text-slate-300 text-sm py-10">
          មិនទាន់មានសារនៅឡើយ សរសេរសួរអ្វីមួយខាងក្រោមបាន
        </div>
        <div
          v-for="m in messages"
          :key="m.id"
          class="flex"
          :class="m.sender_role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div class="max-w-[75%]">
            <p v-if="m.sender_role === 'ai'" class="text-[10px] text-brand-500 font-medium mb-0.5 px-1">🤖 AI ជំនួយការ</p>
            <p v-else-if="m.sender_role === 'admin'" class="text-[10px] text-slate-400 font-medium mb-0.5 px-1">👤 Admin</p>
            <div
              class="rounded-2xl px-4 py-2.5 text-sm"
              :class="[
                m.sender_role === 'user' ? 'bg-brand-600 text-white' : '',
                m.sender_role === 'admin' ? 'bg-slate-100 text-slate-700' : '',
                m.sender_role === 'ai' ? 'bg-emerald-50 text-emerald-800 border border-emerald-100' : '',
              ]"
            >
              <p class="whitespace-pre-wrap break-words">{{ m.content }}</p>
              <p class="text-[10px] mt-1 opacity-60">{{ formatTime(m.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>

      <form @submit.prevent="handleSend" class="border-t border-slate-100 p-3 flex gap-2">
        <input
          v-model="draft"
          type="text"
          class="input-field flex-1"
          placeholder="សរសេរសារ..."
          :disabled="sending"
        />
        <button type="submit" class="btn-primary px-5" :disabled="sending || !draft.trim()">ផ្ញើ</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import api from "../api/axios";

const messages = ref([]);
const draft = ref("");
const sending = ref(false);
const scrollArea = ref(null);
const aiEnabled = ref(true);
let pollTimer = null;

async function loadMessages() {
  const { data } = await api.get("/chat/messages");
  const grew = data.length !== messages.value.length;
  messages.value = data;
  if (grew) {
    await nextTick();
    if (scrollArea.value) scrollArea.value.scrollTop = scrollArea.value.scrollHeight;
  }
}

async function loadAiSetting() {
  const { data } = await api.get("/chat/ai-setting");
  aiEnabled.value = data.chat_ai_enabled;
}

async function toggleAi() {
  aiEnabled.value = !aiEnabled.value;
  await api.put("/chat/ai-setting", { chat_ai_enabled: aiEnabled.value });
}

async function handleSend() {
  const content = draft.value.trim();
  if (!content) return;
  sending.value = true;
  try {
    draft.value = "";
    await api.post("/chat/messages", { content });
    await loadMessages();
  } finally {
    sending.value = false;
  }
}

function formatTime(iso) {
  if (!iso) return "";
  const d = new Date(iso + (iso.endsWith("Z") ? "" : "Z"));
  return d.toLocaleString("km-KH", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "2-digit" });
}

onMounted(async () => {
  await Promise.all([loadMessages(), loadAiSetting()]);
  await nextTick();
  if (scrollArea.value) scrollArea.value.scrollTop = scrollArea.value.scrollHeight;
  pollTimer = setInterval(loadMessages, 5000);
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
});
</script>

