<template>
  <div>
    <h1 class="text-2xl font-bold text-slate-800 mb-1">💬 សារគាំទ្រ (Support Inbox)</h1>
    <p class="text-slate-400 text-sm mb-6">ឆ្លើយសំណួរ/បញ្ហារបស់គ្រូបង្រៀន</p>

    <div class="grid md:grid-cols-3 gap-4 h-[calc(100vh-12rem)]">
      <!-- Conversation list -->
      <div class="card p-0 overflow-hidden flex flex-col md:col-span-1">
        <div class="p-3 border-b border-slate-100 text-sm font-medium text-slate-500">
          ការសន្ទនា ({{ conversations.length }})
        </div>
        <div class="flex-1 overflow-y-auto">
          <button
            v-for="c in conversations"
            :key="c.user_id"
            class="w-full text-left px-4 py-3 border-b border-slate-50 hover:bg-slate-50 transition-colors"
            :class="activeUserId === c.user_id ? 'bg-brand-50' : ''"
            @click="openConversation(c.user_id)"
          >
            <div class="flex items-center justify-between">
              <span class="font-medium text-slate-700 text-sm truncate">{{ c.full_name }}</span>
              <span v-if="c.unread" class="text-[10px] bg-red-500 text-white rounded-full px-1.5 py-0.5 shrink-0 ml-2">
                {{ c.unread }}
              </span>
            </div>
            <p class="text-xs text-slate-400 truncate mt-0.5">{{ c.last_message }}</p>
            <span
              class="inline-block mt-1 text-[10px] px-1.5 py-0.5 rounded"
              :class="c.chat_ai_enabled ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-400'"
            >
              {{ c.chat_ai_enabled ? "🤖 AI សកម្ម" : "👤 Admin កំពុងគ្រប់គ្រង" }}
            </span>
          </button>
          <p v-if="!conversations.length" class="text-center text-slate-300 text-sm py-10">មិនទាន់មានសារទេ</p>
        </div>
      </div>

      <!-- Thread -->
      <div class="card p-0 overflow-hidden flex flex-col md:col-span-2">
        <div v-if="!activeUserId" class="flex-1 flex items-center justify-center text-slate-300 text-sm">
          ជ្រើសរើសការសន្ទនាមួយខាងឆ្វេង
        </div>
        <template v-else>
          <div class="p-3 border-b border-slate-100 flex items-center justify-between">
            <span class="text-sm font-medium text-slate-700">{{ activeUserName }}</span>
            <label class="flex items-center gap-2 text-xs text-slate-500 cursor-pointer select-none">
              <span>🤖 AI</span>
              <button
                type="button"
                role="switch"
                :aria-checked="activeAiEnabled"
                @click="toggleActiveAi"
                class="w-9 h-5 rounded-full transition-colors relative"
                :class="activeAiEnabled ? 'bg-brand-600' : 'bg-slate-300'"
              >
                <span
                  class="absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform"
                  :class="activeAiEnabled ? 'translate-x-4' : 'translate-x-0.5'"
                ></span>
              </button>
            </label>
          </div>
          <div ref="scrollArea" class="flex-1 overflow-y-auto p-4 space-y-3">
            <div
              v-for="m in thread"
              :key="m.id"
              class="flex"
              :class="m.sender_role === 'admin' ? 'justify-end' : 'justify-start'"
            >
              <div class="max-w-[75%]">
                <p v-if="m.sender_role === 'ai'" class="text-[10px] text-brand-500 font-medium mb-0.5 px-1">🤖 AI ជំនួយការ</p>
                <p v-else-if="m.sender_role === 'user'" class="text-[10px] text-slate-400 font-medium mb-0.5 px-1">{{ activeUserName }}</p>
                <div
                  class="rounded-2xl px-4 py-2.5 text-sm"
                  :class="[
                    m.sender_role === 'admin' ? 'bg-brand-600 text-white' : '',
                    m.sender_role === 'user' ? 'bg-slate-100 text-slate-700' : '',
                    m.sender_role === 'ai' ? 'bg-emerald-50 text-emerald-800 border border-emerald-100' : '',
                  ]"
                >
                  <p class="whitespace-pre-wrap break-words">{{ m.content }}</p>
                  <p class="text-[10px] mt-1 opacity-60">{{ formatTime(m.created_at) }}</p>
                </div>
              </div>
            </div>
          </div>
          <form @submit.prevent="handleReply" class="border-t border-slate-100 p-3 flex gap-2">
            <input v-model="draft" type="text" class="input-field flex-1" placeholder="សរសេរចម្លើយ..." :disabled="sending" />
            <button type="submit" class="btn-primary px-5" :disabled="sending || !draft.trim()">ផ្ញើ</button>
          </form>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from "vue";
import api from "../api/axios";

const conversations = ref([]);
const thread = ref([]);
const activeUserId = ref(null);
const activeUserName = ref("");
const draft = ref("");
const sending = ref(false);
const scrollArea = ref(null);
let pollTimer = null;

const activeAiEnabled = computed(() => {
  const c = conversations.value.find((x) => x.user_id === activeUserId.value);
  return c ? c.chat_ai_enabled : true;
});

async function loadConversations() {
  const { data } = await api.get("/chat/admin/conversations");
  conversations.value = data;
}

async function openConversation(userId) {
  activeUserId.value = userId;
  const c = conversations.value.find((x) => x.user_id === userId);
  activeUserName.value = c ? c.full_name : "";
  await loadThread();
}

async function loadThread() {
  if (!activeUserId.value) return;
  const { data } = await api.get(`/chat/admin/conversations/${activeUserId.value}`);
  thread.value = data;
  await loadConversations();
  await nextTick();
  if (scrollArea.value) scrollArea.value.scrollTop = scrollArea.value.scrollHeight;
}

async function toggleActiveAi() {
  if (!activeUserId.value) return;
  const next = !activeAiEnabled.value;
  await api.put(`/chat/admin/conversations/${activeUserId.value}/ai-toggle`, { chat_ai_enabled: next });
  await loadConversations();
}

async function handleReply() {
  const content = draft.value.trim();
  if (!content || !activeUserId.value) return;
  sending.value = true;
  try {
    draft.value = "";
    await api.post(`/chat/admin/conversations/${activeUserId.value}/reply`, { content });
    await loadThread();
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
  await loadConversations();
  pollTimer = setInterval(async () => {
    await loadConversations();
    if (activeUserId.value) await loadThread();
  }, 6000);
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
});
</script>
