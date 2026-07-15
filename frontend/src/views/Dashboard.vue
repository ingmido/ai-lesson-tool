<template>
  <div>
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-slate-800">សួស្តី, {{ auth.user?.full_name }} 👋</h1>
      <p class="text-slate-400 mt-1">ជ្រើសរើសឧបករណ៍ AI ខាងក្រោមដើម្បីចាប់ផ្តើម</p>
    </div>

    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
      <RouterLink
        v-for="tool in tools"
        :key="tool.to"
        :to="tool.to"
        class="card hover:shadow-soft hover:-translate-y-0.5 transition-all group"
      >
        <div
          class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-4"
          :class="tool.bg"
        >
          {{ tool.icon }}
        </div>
        <h3 class="font-semibold text-slate-800 group-hover:text-brand-700">{{ tool.title }}</h3>
        <p class="text-sm text-slate-400 mt-1 leading-relaxed">{{ tool.desc }}</p>
      </RouterLink>
    </div>

    <div class="card mt-8">
      <h3 class="font-semibold text-slate-800 mb-3">របៀបប្រើប្រាស់</h3>
      <ol class="text-sm text-slate-500 space-y-1.5 list-decimal list-inside">
        <li>ជ្រើសរើសឧបករណ៍ដែលអ្នកចង់ប្រើពីខាងលើ</li>
        <li>បញ្ចូល ឬថតរូបឯកសារមេរៀន (ទំព័រសៀវភៅ, កិច្ចតែងការចាស់ ។ល។)</li>
        <li>បំពេញម៉ោងបង្រៀន កាលបរិច្ឆេទ និងជ្រើសរើសវិធីសាស្ត្របង្រៀន</li>
        <li>ចុច "បង្កើតដោយ AI" រួចរង់ចាំលទ្ធផល</li>
        <li>ពិនិត្យ កែសម្រួល រួចទាញយកជា Word ឬ PDF</li>
      </ol>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from "../store/auth";

const auth = useAuthStore();

const tools = [
  {
    to: "/tools/lesson-plan",
    icon: "📝",
    bg: "bg-brand-50",
    title: "កិច្ចតែងការបង្រៀន",
    desc: "បង្កើតកិច្ចតែងការបង្រៀនពេញលេញពីរូបថត ឬឯកសារមេរៀន",
  },
  {
    to: "/tools/slide",
    icon: "🖥️",
    bg: "bg-accent-400/20",
    title: "បង្កើត Slide",
    desc: "បំបែងកិច្ចតែងការទៅជាស្លាយបង្ហាញសម្រាប់ថ្នាក់រៀន",
  },
  {
    to: "/tools/test",
    icon: "🧪",
    bg: "bg-emerald-50",
    title: "តេស្តស្តង់ដារ",
    desc: "បង្កើតតេស្តព្រមទាំងចម្លើយគំរូពីខ្លឹមសារមេរៀន",
  },
  {
    to: "/tools/curriculum",
    icon: "🗂️",
    bg: "bg-purple-50",
    title: "បំបែងចែកកម្មវិធីសិក្សា",
    desc: "បង្កើតតារាងបំបែងកម្មវិធីសិក្សាតាមខែ/សប្តាហ៍",
  },
];
</script>
