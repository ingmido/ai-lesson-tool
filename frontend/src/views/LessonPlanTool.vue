<template>
  <div class="max-w-5xl mx-auto">
    <h1 class="text-2xl font-bold text-slate-800 mb-1">📝 កិច្ចតែងការបង្រៀន AI</h1>
    <p class="text-slate-400 text-sm mb-6">ថតរូប/បញ្ចូលឯកសារ ឬសរសេរខ្លឹមសារមេរៀនផ្ទាល់ ហើយឲ្យ AI បង្កើតកិច្ចតែងការពេញលេញ</p>

    <div class="grid lg:grid-cols-2 gap-6">
      <!-- Input form -->
      <form @submit.prevent="handleGenerate" class="card space-y-4 h-fit">
        <div v-if="error" class="rounded-xl bg-red-50 text-red-600 text-sm px-4 py-3">{{ error }}</div>

        <div class="flex gap-2 p-1 bg-slate-100 rounded-xl">
          <button
            type="button"
            class="flex-1 text-sm font-medium py-2 rounded-lg transition-colors"
            :class="inputMode === 'file' ? 'bg-white text-brand-700 shadow-sm' : 'text-slate-500'"
            @click="inputMode = 'file'"
          >
            📎 ផ្ទុកឯកសារ/រូបថត
          </button>
          <button
            type="button"
            class="flex-1 text-sm font-medium py-2 rounded-lg transition-colors"
            :class="inputMode === 'text' ? 'bg-white text-brand-700 shadow-sm' : 'text-slate-500'"
            @click="inputMode = 'text'"
          >
            ✍️ សរសេរផ្ទាល់
          </button>
        </div>

        <div v-if="inputMode === 'file'">
          <label class="label">ឯកសារ ឬរូបថតមេរៀន (ជ្រើសបានច្រើន)</label>
          <input type="file" multiple accept="image/*,application/pdf" @change="onFiles" class="text-sm text-slate-500" />
          <div v-if="files.length" class="flex flex-wrap gap-2 mt-2">
            <span v-for="(f, i) in files" :key="i" class="text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded-lg">{{ f.name }}</span>
          </div>
        </div>

        <div v-else>
          <label class="label">សរសេរខ្លឹមសារមេរៀនផ្ទាល់</label>
          <textarea
            v-model="form.lesson_text"
            rows="6"
            class="input-field"
            placeholder="ឧ. ជំពូកទី២ មេរៀនទី៣៖ ការគ្រប់គ្រងប្រព័ន្ធនិងបណ្ដាញ។ គោលបំណង៖ សិស្សអាចកំណត់មុខងាររបស់ប្រព័ន្ធ... (សរសេរខ្លឹមសារ ឬចម្លងអត្ថបទពីសៀវភៅមកដាក់ទីនេះ)"
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">ចំនួនម៉ោងបង្រៀន</label>
            <input v-model="form.hours" type="number" step="0.5" min="0.5" class="input-field" placeholder="ឧ. 1" />
          </div>
          <div>
            <label class="label">កាលបរិច្ឆេទបង្រៀន</label>
            <input v-model="form.lesson_date" type="date" class="input-field" />
          </div>
        </div>

        <div>
          <label class="label">វិធីសាស្ត្របង្រៀន</label>
          <select v-model="form.method" class="input-field">
            <option value="inquiry">បែបរិះរក (Inquiry-Based)</option>
            <option value="bloom">បែប Bloom's Taxonomy</option>
            <option value="student_centered">បែបសិស្សមជ្ឈមណ្ឌល (Student-Centered)</option>
          </select>
        </div>

        <div>
          <label class="label">កំណត់ចំណាំបន្ថែម (មិនចាំបាច់)</label>
          <textarea v-model="form.extra_notes" rows="2" class="input-field" placeholder="ឧ. ចង់ឲ្យសង្កត់ធ្ងន់លើសកម្មភាពជាក្រុម..."></textarea>
        </div>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? "AI កំពុងបង្កើត..." : "✨ បង្កើតដោយ AI" }}
        </button>
      </form>

      <!-- Result -->
      <div v-if="result" class="card space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold text-slate-800">លទ្ធផល</h3>
          <div class="flex gap-2">
            <button class="btn-secondary text-xs px-3 py-1.5" @click="saveEdits" :disabled="saving">
              {{ saving ? "កំពុងរក្សា..." : "រក្សាទុកការកែប្រែ" }}
            </button>
            <button class="btn-secondary text-xs px-3 py-1.5" @click="doDownload('docx')" :disabled="downloading">⬇ Word</button>
            <button class="btn-secondary text-xs px-3 py-1.5" @click="doDownload('pdf')" :disabled="downloading">⬇ PDF</button>
          </div>
        </div>

        <div class="space-y-3 text-sm max-h-[600px] overflow-y-auto pr-1">
          <div class="grid grid-cols-2 gap-3">
            <FieldEdit label="កាលបរិច្ឆេទ" v-model="result.date" />
            <FieldEdit label="ថ្នាក់ទី" v-model="result.grade" />
            <FieldEdit label="មុខវិជ្ជា" v-model="result.subject" />
            <FieldEdit label="រយៈពេល" v-model="result.duration" />
            <FieldEdit label="ជំពូកទី" v-model="result.chapter" class="col-span-2" />
            <FieldEdit label="មេរៀនទី" v-model="result.lesson" class="col-span-2" />
            <FieldEdit label="សិក្សាអំពី" v-model="result.topic" class="col-span-2" />
          </div>

          <div>
            <p class="label mb-2">វត្ថុបំណង</p>
            <FieldEdit label="វិជ្ជាទស្សន៍" v-model="result.objectives.knowledge" textarea />
            <FieldEdit label="បំណិន" v-model="result.objectives.skills" textarea />
            <FieldEdit label="ចរិយា" v-model="result.objectives.attitude" textarea />
          </div>

          <div>
            <p class="label mb-2">សម្ភារៈឧបទេស</p>
            <FieldEdit label="ឯកសារ" v-model="result.materials.documents" textarea />
            <FieldEdit label="ឧបករណ៍" v-model="result.materials.tools" textarea />
          </div>

          <div>
            <p class="label mb-2">សកម្មភាពបង្រៀន និងសិក្សា</p>
            <div v-for="(act, i) in result.activities" :key="i" class="border border-slate-100 rounded-xl p-3 mb-2">
              <div class="flex justify-between text-xs text-slate-400 mb-2">
                <span class="font-medium text-slate-600">{{ act.step_title }}</span>
                <span>{{ act.time }}</span>
              </div>
              <FieldEdit label="សកម្មភាពគ្រូ" v-model="act.teacher_activity" textarea small />
              <FieldEdit label="ខ្លឹមសារ" v-model="act.content" textarea small />
              <FieldEdit label="សកម្មភាពសិស្ស" v-model="act.student_activity" textarea small />
            </div>
          </div>
        </div>
      </div>

      <div v-else class="card flex items-center justify-center text-slate-300 text-sm min-h-[300px]">
        លទ្ធផលនឹងបង្ហាញនៅទីនេះ
      </div>
    </div>

    <!-- History -->
    <div class="card mt-6" v-if="history.length">
      <h3 class="font-semibold text-slate-800 mb-3">ប្រវត្តិការបង្កើតថ្មីៗ</h3>
      <ul class="divide-y divide-slate-50 text-sm">
        <li v-for="h in history" :key="h.id" class="py-2 flex items-center justify-between">
          <button class="text-slate-600 hover:text-brand-600 text-left" @click="loadFromHistory(h.id)">
            {{ h.title }} <span class="text-slate-300">· {{ formatDate(h.created_at) }}</span>
          </button>
          <div class="flex gap-2">
            <button class="text-xs text-brand-600 hover:underline" @click="downloadExport(h.id, 'docx')">Word</button>
            <button class="text-xs text-red-400 hover:underline" @click="deleteHistoryItem(h.id)">លុប</button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, defineComponent, h } from "vue";
import api from "../api/axios";
import { downloadExport } from "../utils/download";

const TOOL_TYPE = "lesson_plan";

// Small inline editable field component
const FieldEdit = defineComponent({
  props: { label: String, modelValue: String, textarea: Boolean, small: Boolean },
  emits: ["update:modelValue"],
  setup(props, { emit, attrs }) {
    return () =>
      h("div", { class: attrs.class || "mb-2" }, [
        h("label", { class: "text-xs text-slate-400 mb-1 block" }, props.label),
        props.textarea
          ? h("textarea", {
              class: `input-field ${props.small ? "text-xs py-1.5" : "text-sm"}`,
              rows: props.small ? 2 : 2,
              value: props.modelValue,
              onInput: (e) => emit("update:modelValue", e.target.value),
            })
          : h("input", {
              class: "input-field text-sm",
              value: props.modelValue,
              onInput: (e) => emit("update:modelValue", e.target.value),
            }),
      ]);
  },
});

const inputMode = ref("file");
const files = ref([]);
const form = reactive({ hours: "1", lesson_date: "", method: "inquiry", extra_notes: "", lesson_text: "" });
const loading = ref(false);
const saving = ref(false);
const error = ref("");
const result = ref(null);
const genId = ref(null);
const history = ref([]);
const downloading = ref(false);

async function doDownload(format) {
  downloading.value = true;
  error.value = "";
  try {
    await downloadExport(genId.value, format, `${TOOL_TYPE}_${genId.value}.${format}`);
  } catch (e) {
    error.value =
      format === "pdf"
        ? "ការទាញយក PDF បរាជ័យ (ប្រហែលជាកម្មវិធីមេមិនទាន់ដំឡើង LibreOffice ទេ)។ សូមសាកល្បងទាញយកជា Word វិញ។"
        : "ការទាញយកបរាជ័យ សូមព្យាយាមម្តងទៀត";
  } finally {
    downloading.value = false;
  }
}

function onFiles(e) {
  files.value = Array.from(e.target.files);
}

async function handleGenerate() {
  if (inputMode.value === "file" && !files.value.length) {
    error.value = "សូមភ្ជាប់ឯកសារ ឬរូបថតយ៉ាងហោចណាស់មួយ";
    return;
  }
  if (inputMode.value === "text" && !form.lesson_text.trim()) {
    error.value = "សូមសរសេរខ្លឹមសារមេរៀន";
    return;
  }
  loading.value = true;
  error.value = "";
  try {
    const fd = new FormData();
    if (inputMode.value === "file") {
      files.value.forEach((f) => fd.append("files", f));
    }
    Object.entries(form).forEach(([k, v]) => {
      if (k === "lesson_text" && inputMode.value === "file") return;
      fd.append(k, v);
    });

    const { data } = await api.post(`/ai/${TOOL_TYPE}/generate`, fd, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 120000,
    });
    result.value = data.content;
    genId.value = data.generation.id;
    await loadHistory();
  } catch (e) {
    error.value = e.response?.data?.error || "ការបង្កើតបរាជ័យ សូមព្យាយាមម្តងទៀត";
  } finally {
    loading.value = false;
  }
}

async function saveEdits() {
  saving.value = true;
  try {
    await api.put(`/ai/generation/${genId.value}`, { content: result.value });
  } finally {
    saving.value = false;
  }
}

async function loadHistory() {
  const { data } = await api.get(`/ai/${TOOL_TYPE}/history`);
  history.value = data.slice(0, 10);
}

async function loadFromHistory(id) {
  const { data } = await api.get(`/ai/generation/${id}`);
  result.value = data.content;
  genId.value = data.id;
}

async function deleteHistoryItem(id) {
  await api.delete(`/ai/generation/${id}`);
  await loadHistory();
}

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString("km-KH") : "";
}

onMounted(loadHistory);
</script>
