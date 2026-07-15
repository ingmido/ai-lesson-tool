<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-2xl font-bold text-slate-800 mb-1">🗂️ បំបែងចែកកម្មវិធីសិក្សា AI</h1>
    <p class="text-slate-400 text-sm mb-6">ទាញយកខ្លឹមសារពីសៀវភៅសិក្សា ហើយបំបែងជាតារាងកម្មវិធីសិក្សាតាមខែ/សប្តាហ៍</p>

    <div class="grid lg:grid-cols-5 gap-6">
      <form @submit.prevent="handleGenerate" class="card space-y-4 h-fit lg:col-span-2">
        <div v-if="error" class="rounded-xl bg-red-50 text-red-600 text-sm px-4 py-3">{{ error }}</div>

        <div>
          <label class="label">ឯកសារសៀវភៅសិក្សា (រូបថត ឬ PDF, ជ្រើសបានច្រើនទំព័រ)</label>
          <input type="file" multiple accept="image/*,application/pdf" @change="onFiles" class="text-sm text-slate-500" required />
          <div v-if="files.length" class="flex flex-wrap gap-2 mt-2">
            <span v-for="(f, i) in files" :key="i" class="text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded-lg">{{ f.name }}</span>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">ចំនួនម៉ោង/សប្តាហ៍</label>
            <input v-model="form.hours" type="number" step="0.5" class="input-field" />
          </div>
          <div>
            <label class="label">ចាប់ផ្តើមឆ្នាំសិក្សា</label>
            <input v-model="form.lesson_date" type="date" class="input-field" />
          </div>
        </div>

        <div>
          <label class="label">កំណត់ចំណាំបន្ថែម</label>
          <textarea v-model="form.extra_notes" rows="2" class="input-field" placeholder="ឧ. ថ្នាក់ទី១០ ឆ្នាំសិក្សា ២០២៥-២០២៦..."></textarea>
        </div>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? "AI កំពុងបង្កើត..." : "✨ បង្កើតកម្មវិធីសិក្សា" }}
        </button>
      </form>

      <div v-if="result" class="card space-y-4 lg:col-span-3">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold text-slate-800">{{ result.subject }} — {{ result.grade }}</h3>
          <div class="flex gap-2">
            <button class="btn-secondary text-xs px-3 py-1.5" @click="doDownload('docx')" :disabled="downloading">⬇ Word</button>
            <button class="btn-secondary text-xs px-3 py-1.5" @click="doDownload('pdf')" :disabled="downloading">⬇ PDF</button>
          </div>
        </div>
        <div class="max-h-[600px] overflow-y-auto pr-1">
          <table class="w-full text-xs border-collapse">
            <thead class="sticky top-0 bg-white">
              <tr class="text-left text-slate-400 border-b border-slate-100">
                <th class="py-2 pr-2">ខែ</th>
                <th class="py-2 pr-2">សប្តាហ៍</th>
                <th class="py-2 pr-2">ខ្លឹមសារមេរៀន</th>
                <th class="py-2 pr-2">លទ្ធផលការសិក្សា</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(r, i) in result.rows" :key="i" class="border-b border-slate-50 align-top">
                <td class="py-2 pr-2 font-medium text-slate-600">{{ r.month }}</td>
                <td class="py-2 pr-2 text-slate-500">{{ r.week_hours }}</td>
                <td class="py-2 pr-2 text-slate-600">{{ r.lesson_content }}</td>
                <td class="py-2 pr-2 text-slate-500">{{ r.learning_outcome }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div v-else class="card flex items-center justify-center text-slate-300 text-sm min-h-[300px] lg:col-span-3">
        លទ្ធផលនឹងបង្ហាញនៅទីនេះ
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import api from "../api/axios";
import { downloadExport } from "../utils/download";

const files = ref([]);
const form = reactive({ hours: "1", lesson_date: "", extra_notes: "" });
const loading = ref(false);
const error = ref("");
const result = ref(null);
const genId = ref(null);
const downloading = ref(false);

async function doDownload(format) {
  downloading.value = true;
  error.value = "";
  try {
    await downloadExport(genId.value, format, `curriculum_${genId.value}.${format}`);
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
    const { data } = await api.post("/ai/curriculum/generate", fd, {
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
</script>
