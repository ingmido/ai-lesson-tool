<template>
  <div>
    <h1 class="text-2xl font-bold text-slate-800 mb-1">គ្រប់គ្រងអ្នកប្រើប្រាស់</h1>
    <p class="text-slate-400 text-sm mb-6">មើល កែប្រែសិទ្ធិ ផ្អាក ឬលុបគណនីគ្រូបង្រៀន</p>

    <div v-if="message" class="rounded-xl bg-emerald-50 text-emerald-600 text-sm px-4 py-3 mb-4">{{ message }}</div>

    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-slate-400 border-b border-slate-100">
            <th class="py-2 pr-4">ឈ្មោះ</th>
            <th class="py-2 pr-4">Username</th>
            <th class="py-2 pr-4">សាលា</th>
            <th class="py-2 pr-4">មុខវិជ្ជា</th>
            <th class="py-2 pr-4">តួនាទី</th>
            <th class="py-2 pr-4">សកម្មភាព</th>
            <th class="py-2 pr-4"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id" class="border-b border-slate-50">
            <td class="py-3 pr-4 font-medium text-slate-700">{{ u.full_name }}</td>
            <td class="py-3 pr-4 text-slate-500">{{ u.username }}</td>
            <td class="py-3 pr-4 text-slate-500">{{ u.school_name || "—" }}</td>
            <td class="py-3 pr-4 text-slate-500">{{ u.subject || "—" }}</td>
            <td class="py-3 pr-4">
              <select
                :value="u.role"
                @change="updateUser(u, { role: $event.target.value })"
                class="input-field py-1 text-xs"
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </td>
            <td class="py-3 pr-4">
              <button
                class="text-xs px-3 py-1.5 rounded-lg font-medium"
                :class="u.is_active ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-400'"
                @click="updateUser(u, { is_active: !u.is_active })"
              >
                {{ u.is_active ? "សកម្ម" : "ផ្អាក" }}
              </button>
            </td>
            <td class="py-3 pr-4">
              <button class="text-red-500 hover:text-red-700 text-xs font-medium" @click="removeUser(u)">លុប</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!users.length" class="text-center text-slate-400 py-8">មិនទាន់មានអ្នកប្រើប្រាស់</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api/axios";

const users = ref([]);
const message = ref("");

async function load() {
  const { data } = await api.get("/admin/users");
  users.value = data;
}

async function updateUser(u, patch) {
  await api.put(`/admin/users/${u.id}`, patch);
  message.value = `បានធ្វើបច្ចុប្បន្នភាព ${u.full_name}`;
  await load();
  setTimeout(() => (message.value = ""), 2500);
}

async function removeUser(u) {
  if (!confirm(`តើអ្នកប្រាកដទេថាចង់លុប ${u.full_name}?`)) return;
  await api.delete(`/admin/users/${u.id}`);
  await load();
}

onMounted(load);
</script>
