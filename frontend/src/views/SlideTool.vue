<template>
  <div class="max-w-5xl mx-auto">
    <h1 class="text-2xl font-bold text-slate-800 mb-1">🖥️ បង្កើត Slide AI</h1>
    <p class="text-slate-400 text-sm mb-6">ទាញយកមេរៀនចេញពីឯកសារ/កិច្ចតែងការ ហើយបំបែងទៅជាស្លាយបង្ហាញ</p>

    <div class="grid lg:grid-cols-2 gap-6">
      <form @submit.prevent="handleGenerate" class="card space-y-4 h-fit">
        <div v-if="error" class="rounded-xl bg-red-50 text-red-600 text-sm px-4 py-3">{{ error }}</div>

        <div>
          <label class="label">ឯកសារមេរៀន / កិច្ចតែងការ (រូបថត ឬ PDF)</label>
          <input type="file" multiple accept="image/*,application/pdf" @change="onFiles" class="text-sm text-slate-500" required />
          <div v-if="files.length" class="flex flex-wrap gap-2 mt-2">
            <span v-for="(f, i) in files" :key="i" class="text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded-lg">{{ f.name }}</span>
          </div>
        </div>

        <div>
          <label class="label">រចនាប័ទ្មស្លាយ</label>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="opt in styleOptions"
              :key="opt.value"
              type="button"
              @click="form.style = opt.value"
              class="text-left rounded-xl border p-2.5 transition-colors"
              :class="form.style === opt.value ? 'border-brand-500 ring-2 ring-brand-100' : 'border-slate-200 hover:border-slate-300'"
            >
              <div class="h-8 rounded-lg mb-1.5 flex overflow-hidden">
                <div class="flex-1" :style="{ background: opt.swatch[0] }"></div>
                <div class="flex-1" :style="{ background: opt.swatch[1] }"></div>
              </div>
              <div class="text-xs font-medium text-slate-700">{{ opt.label }}</div>
            </button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">ចំនួនម៉ោងបង្រៀន</label>
            <input v-model="form.hours" type="number" step="0.5" class="input-field" />
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
            <option value="student_centered">បែបសិស្សមជ្ឈមណ្ឌល</option>
          </select>
        </div>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? "AI កំពុងបង្កើត..." : "✨ បង្កើត Slide" }}
        </button>
      </form>

      <div v-if="result" class="card space-y-4">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <h3 class="font-semibold text-slate-800">{{ result.title }}</h3>
          <div class="flex gap-2">
            <button class="btn-secondary text-xs px-3 py-1.5" @click="doDownload('pptx')" :disabled="downloading">⬇ PowerPoint</button>
            <button class="btn-secondary text-xs px-3 py-1.5" @click="doDownload('docx')" :disabled="downloading">⬇ Word</button>
            <button class="btn-secondary text-xs px-3 py-1.5" @click="doDownload('pdf')" :disabled="downloading">⬇ PDF</button>
          </div>
        </div>

        <div class="max-h-[560px] overflow-y-auto pr-1 space-y-2">
          <div v-for="(s, i) in result.slides" :key="i" class="border border-slate-100 rounded-xl p-3">
            <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>ស្លាយទី {{ i + 1 }}</span>
              <span class="bg-slate-100 text-slate-500 px-2 py-0.5 rounded-md">{{ typeLabel(s.type) }}</span>
            </div>
            <div class="font-medium text-slate-800 mb-1">{{ s.heading || s.title }}</div>

            <ul v-if="s.type === 'bullets'" class="list-disc list-inside text-sm text-slate-600 space-y-1">
              <li v-for="(it, j) in s.items" :key="j"><b>{{ it.title }}</b> {{ it.desc }}</li>
            </ul>
            <p v-else-if="s.type === 'two_column'" class="text-sm text-slate-600">{{ (s.paragraphs || []).join(" ") }}</p>
            <ul v-else-if="s.type === 'cards'" class="list-disc list-inside text-sm text-slate-600 space-y-1">
              <li v-for="(c, j) in s.cards" :key="j">{{ c.icon }} <b>{{ c.title }}</b> — {{ c.desc }}</li>
            </ul>
            <ul v-else-if="s.type === 'timeline'" class="list-disc list-inside text-sm text-slate-600 space-y-1">
              <li v-for="(st, j) in s.stages" :key="j"><b>{{ st.title }}</b> ({{ st.subtitle }}) — {{ st.desc }}</li>
            </ul>
            <p v-else-if="s.type === 'closing'" class="text-sm text-slate-600">
              {{ (s.questions || []).length }} សំណួរពិនិត្យឡើងវិញ
            </p>
            <p v-else class="text-sm text-slate-400">{{ s.subheading }}</p>
          </div>
        </div>
      </div>
      <div v-else class="card flex items-center justify-center text-slate-300 text-sm min-h-[300px]">
        លទ្ធផលនឹងបង្ហាញនៅទីនេះ
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import api from "../api/axios";
import { downloadExport } from "../utils/download";

const styleOptions = [
  { value: "teal_light", label: "ទំនើប · ភ្លឺ", swatch: ["#ECF4F5", "#148F8C"] },
  { value: "navy_dark", label: "ទំនើប · ងងឹត", swatch: ["#0B1322", "#22C58B"] },
  { value: "moeys_formal", label: "ផ្លូវការ (MOEYS)", swatch: ["#FFFFFF", "#1B3A8F"] },
  { value: "playful", label: "រីករាយ", swatch: ["#FDF6EC", "#F26B38"] },
];

const files = ref([]);
const form = reactive({ hours: "1", lesson_date: "", method: "inquiry", style: "teal_light" });
const loading = ref(false);
const error = ref("");
const result = ref(null);
const genId = ref(null);
const downloading = ref(false);

function onFiles(e) {
  files.value = Array.from(e.target.files);
}

function typeLabel(t) {
  const labels = {
    cover: "គម្រប",
    bullets: "ចំណុចសំខាន់",
    two_column: "ការពន្យល់",
    cards: "កាតជាជួរ",
    timeline: "ដំណាក់កាល",
    table: "តារាង",
    compare: "ប្រៀបធៀប",
    section: "ផ្តាច់វគ្គ",
    closing: "បញ្ចប់",
  };
  return labels[t] || t;
}

async function handleGenerate() {
  if (!files.value.length) {
    error.value = "សូមភ្ជាប់ឯកសារយ៉ាងហោចណាស់មួយ";
    return;
  }
  loading.value = true;
  error.value = "";
  try {
    const fd = new FormData();
    files.value.forEach((f) => fd.append("files", f));
    Object.entries(form).forEach(([k, v]) => fd.append(k, v));
    const { data } = await api.post("/ai/slide/generate", fd, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 120000,
    });
    result.value = data.content;
    genId.value = data.generation.id;
  } catch (e) {
    error.value = e.response?.data?.error || "ការបង្កើតបរាជ័យ";
  } finally {
    loading.value = false;
  }
}

async function doDownload(format) {
  downloading.value = true;
  error.value = "";
  try {
    await downloadExport(genId.value, format, `slide_${genId.value}.${format}`);
  } catch (e) {
    error.value =
      format === "pdf"
        ? "ការទាញយក PDF បរាជ័យ (ប្រហែលជាកម្មវិធីមេមិនទាន់ដំឡើង LibreOffice ទេ)។ សូមសាកល្បងទាញយកជា PowerPoint វិញ។"
        : "ការទាញយកបរាជ័យ សូមព្យាយាមម្តងទៀត";
  } finally {
    downloading.value = false;
  }
}
</script>
