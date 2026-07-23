<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-2xl font-bold text-slate-800 mb-1">🗃️ ធនាគារសំណួរប្រលង</h1>
    <p class="text-slate-400 text-sm mb-6">រក្សាទុកសំណួរចាស់ ជ្រើសរើសបង្កើតតេស្តថ្មីលឿន</p>

    <div class="grid lg:grid-cols-3 gap-6">
      <!-- Filters + Add form -->
      <div class="space-y-4">
        <div class="card space-y-3">
          <h3 class="font-semibold text-slate-800 text-sm">ស្វែងរក / ត្រង</h3>
          <input v-model="search" @input="debouncedLoad" type="text" class="input-field text-sm" placeholder="ស្វែងរកខ្លឹមសារសំណួរ..." />
          <select v-model="filterSubject" @change="load" class="input-field text-sm">
            <option value="">គ្រប់មុខវិជ្ជា</option>
            <option v-for="s in subjects" :key="s" :value="s">{{ s }}</option>
          </select>
          <input v-model="filterTag" @input="debouncedLoad" type="text" class="input-field text-sm" placeholder="Tag (ឧ. ជំពូក១)" />
        </div>

        <div class="card space-y-3">
          <h3 class="font-semibold text-slate-800 text-sm">➕ បន្ថែមសំណួរដោយដៃ</h3>
          <div v-if="addError" class="rounded-lg bg-red-50 text-red-600 text-xs px-3 py-2">{{ addError }}</div>
          <select v-model="newQ.question_type" class="input-field text-sm">
            <option value="mcq">ជម្រើសពហុគុណ</option>
            <option value="short">សំណួរខ្លី</option>
          </select>
          <input v-model="newQ.subject" type="text" class="input-field text-sm" placeholder="មុខវិជ្ជា" />
          <input v-model="newQ.grade" type="text" class="input-field text-sm" placeholder="ថ្នាក់ទី" />
          <textarea v-model="newQ.question_text" rows="2" class="input-field text-sm" placeholder="ខ្លឹមសារសំណួរ"></textarea>
          <div v-if="newQ.question_type === 'mcq'" class="space-y-1">
            <input
              v-for="(c, i) in newQ.choices"
              :key="i"
              v-model="newQ.choices[i]"
              type="text"
              class="input-field text-xs"
              :placeholder="`ជម្រើសទី ${i + 1}`"
            />
            <button type="button" class="text-xs text-brand-600" @click="newQ.choices.push('')">+ បន្ថែមជម្រើស</button>
          </div>
          <input v-model="newQ.answer" type="text" class="input-field text-sm" placeholder="ចម្លើយត្រឹមត្រូវ" />
          <input v-model="newQ.tagsText" type="text" class="input-field text-sm" placeholder="Tags (ខណ្ឌដោយក្បៀស)" />
          <button class="btn-primary w-full text-sm" @click="handleAdd" :disabled="adding">
            {{ adding ? "កំពុងបន្ថែម..." : "បន្ថែមទៅធនាគារ" }}
          </button>
        </div>
      </div>

      <!-- Question list + build test -->
      <div class="lg:col-span-2 space-y-4">
        <div class="card">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-slate-800 text-sm">សំណួរដែលបានរក្សាទុក ({{ questions.length }})</h3>
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-400">បានជ្រើសរើស {{ selected.length }}</span>
              <button
                class="btn-primary text-xs px-3 py-1.5"
                :disabled="!selected.length || building"
                @click="handleBuildTest"
              >
                {{ building ? "កំពុងបង្កើត..." : "🧪 បង្កើតតេស្តពីសំណួរដែលបានជ្រើស" }}
              </button>
            </div>
          </div>

          <div v-if="!questions.length" class="text-center text-slate-300 text-sm py-10">
            មិនទាន់មានសំណួរនៅឡើយ បន្ថែមតាមទម្រង់ខាងឆ្វេង ឬរក្សាទុកពី tool តេស្ត AI
          </div>

          <div class="max-h-[600px] overflow-y-auto space-y-2">
            <label
              v-for="q in questions"
              :key="q.id"
              class="flex items-start gap-3 border border-slate-100 rounded-xl p-3 cursor-pointer hover:bg-slate-50"
            >
              <input type="checkbox" :value="q.id" v-model="selected" class="mt-1" />
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 text-[10px] text-slate-400 mb-1">
                  <span v-if="q.subject" class="bg-slate-100 px-1.5 py-0.5 rounded">{{ q.subject }}</span>
                  <span v-if="q.grade" class="bg-slate-100 px-1.5 py-0.5 rounded">ថ្នាក់ទី{{ q.grade }}</span>
                  <span v-for="t in q.tags" :key="t" class="bg-brand-50 text-brand-600 px-1.5 py-0.5 rounded">{{ t }}</span>
                </div>
                <p class="text-sm text-slate-700">{{ q.question_text }}</p>
                <ul v-if="q.choices" class="text-xs text-slate-500 mt-1 list-none">
                  <li v-for="(c, i) in q.choices" :key="i">{{ c }}</li>
                </ul>
                <p class="text-xs text-emerald-600 mt-1">ចម្លើយ៖ {{ q.answer }}</p>
              </div>
              <button type="button" class="text-red-400 hover:text-red-600 text-xs shrink-0" @click.prevent="handleDelete(q.id)">
                លុប
              </button>
            </label>
          </div>
        </div>

        <div v-if="builtGenId" class="card">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold text-slate-800 text-sm">✅ បង្កើតតេស្តជោគជ័យ!</h3>
            <div class="flex gap-2">
              <button class="btn-secondary text-xs px-3 py-1.5" @click="doDownload('docx')">⬇ Word</button>
              <button class="btn-secondary text-xs px-3 py-1.5" @click="doDownload('pdf')">⬇ PDF</button>
              <button class="btn-secondary text-xs px-3 py-1.5" @click="doDownload('google-form-script')">📤 Google Form</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import api from "../api/axios";
import { downloadExport } from "../utils/download";

const questions = ref([]);
const subjects = ref([]);
const selected = ref([]);
const search = ref("");
const filterSubject = ref("");
const filterTag = ref("");
const adding = ref(false);
const addError = ref("");
const building = ref(false);
const builtGenId = ref(null);

const newQ = reactive({
  question_type: "mcq",
  subject: "",
  grade: "",
  question_text: "",
  choices: ["", ""],
  answer: "",
  tagsText: "",
});

let debounceTimer = null;
function debouncedLoad() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(load, 350);
}

async function load() {
  const params = {};
  if (search.value) params.search = search.value;
  if (filterSubject.value) params.subject = filterSubject.value;
  if (filterTag.value) params.tag = filterTag.value;
  const { data } = await api.get("/question-bank", { params });
  questions.value = data;
}

async function loadSubjects() {
  const { data } = await api.get("/question-bank/subjects");
  subjects.value = data;
}

async function handleAdd() {
  addError.value = "";
  if (!newQ.question_text.trim()) {
    addError.value = "សូមបញ្ចូលខ្លឹមសារសំណួរ";
    return;
  }
  adding.value = true;
  try {
    const payload = {
      question_type: newQ.question_type,
      subject: newQ.subject,
      grade: newQ.grade,
      question_text: newQ.question_text,
      answer: newQ.answer,
      tags: newQ.tagsText.split(",").map((t) => t.trim()).filter(Boolean),
    };
    if (newQ.question_type === "mcq") {
      payload.choices = newQ.choices.filter((c) => c.trim());
    }
    await api.post("/question-bank", payload);
    Object.assign(newQ, {
      question_type: "mcq",
      subject: newQ.subject,
      grade: newQ.grade,
      question_text: "",
      choices: ["", ""],
      answer: "",
      tagsText: "",
    });
    await Promise.all([load(), loadSubjects()]);
  } catch (e) {
    addError.value = e.response?.data?.error || "មានបញ្ហា សូមព្យាយាមម្តងទៀត";
  } finally {
    adding.value = false;
  }
}

async function handleDelete(id) {
  if (!confirm("តើប្រាកដជាចង់លុបសំណួរនេះមែនទេ?")) return;
  await api.delete(`/question-bank/${id}`);
  selected.value = selected.value.filter((i) => i !== id);
  await load();
}

async function handleBuildTest() {
  building.value = true;
  try {
    const { data } = await api.post("/question-bank/build-test", {
      ids: selected.value,
      title: "តេស្តពីធនាគារសំណួរ",
    });
    builtGenId.value = data.generation.id;
  } finally {
    building.value = false;
  }
}

async function doDownload(format) {
  if (!builtGenId.value) return;
  await downloadExport(builtGenId.value, format, `test_${builtGenId.value}.${format === "google-form-script" ? "gs" : format}`);
}

onMounted(() => {
  load();
  loadSubjects();
});
</script>
