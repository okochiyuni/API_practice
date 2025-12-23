<template>
  <div class="page">
    <Header title="今日のタスク" subtitle="バックエンドとつながるTODOアプリ">
      <template #actions>
        <div class="filter-bar" aria-label="絞り込み">
          <label class="field">
            <span>状態</span>
            <select v-model="statusFilter" @change="loadTodos">
              <option value="all">すべて</option>
              <option value="pending">未完了</option>
              <option value="completed">完了</option>
            </select>
          </label>
          <label class="field">
            <span>分類</span>
            <select v-model="categoryFilter" @change="loadTodos">
              <option value="all">すべて</option>
              <option v-for="cat in categories" :key="cat.name" :value="cat.name">
                {{ cat.name }}
              </option>
            </select>
          </label>
        </div>
      </template>
    </Header>

    <main class="content">
      <section class="panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">最新のTODO</p>
            <h2>タスク一覧</h2>
          </div>
          <button type="button" class="ghost" @click="loadTodos" :disabled="loading">
            更新
          </button>
        </div>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-else-if="loading" class="muted">読み込み中...</p>
        <p v-else-if="todos.length === 0" class="muted">登録されたタスクはありません。</p>

        <div class="task-grid" v-else>
          <Task
            v-for="todo in todos"
            :key="todo.id"
            :todo="todo"
            @toggle="toggleComplete"
            @delete="deleteTodo"
            @edit="startEdit"
          />
        </div>
      </section>

      <section class="panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">新規作成 / 編集</p>
            <h2>{{ editingId ? "タスクを更新" : "タスクを追加" }}</h2>
          </div>
          <span class="muted">API: {{ apiBase }}</span>
        </div>

        <form class="task-form" @submit.prevent="handleSubmit">
          <label class="field">
            <span>タイトル</span>
            <input v-model.trim="form.title" type="text" placeholder="例: 企画書を仕上げる" required />
          </label>

          <label class="field">
            <span>締切</span>
            <input v-model="form.deadline" type="date" />
          </label>

          <label class="field">
            <span>分類</span>
            <input
              v-model.trim="form.category"
              type="text"
              list="category-options"
              placeholder="例: 仕事"
              required
            />
            <datalist id="category-options">
              <option v-for="cat in categories" :key="cat.name" :value="cat.name" />
            </datalist>
          </label>

          <div class="actions">
            <button type="submit" class="primary" :disabled="loading">
              {{ editingId ? "更新する" : "追加する" }}
            </button>
            <button type="button" class="ghost" @click="resetForm">リセット</button>
          </div>
        </form>
      </section>
    </main>

    <AddTaskButton :label="editingId ? '編集中...' : 'タスクを追加'" @click="scrollToForm" />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import AddTaskButton from "./components/AddTaskButton.vue";
import Header from "./components/Header.vue";
import Task from "./components/Task.vue";

const apiBase = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

const todos = ref([]);
const categories = ref([]);
const statusFilter = ref("all");
const categoryFilter = ref("all");
const loading = ref(false);
const error = ref("");
const editingId = ref(null);
const form = reactive({ title: "", deadline: "", category: "" });

const scrollToForm = () => {
  document.querySelector(".task-form")?.scrollIntoView({ behavior: "smooth" });
};

const resetForm = () => {
  editingId.value = null;
  form.title = "";
  form.deadline = "";
  form.category = "";
};

const handleSubmit = async () => {
  error.value = "";
  loading.value = true;
  try {
    await ensureCategory(form.category);

    if (editingId.value) {
      await fetch(`${apiBase}/todos/${editingId.value}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      }).then(checkResponse);
    } else {
      await fetch(`${apiBase}/todos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      }).then(checkResponse);
    }

    await loadTodos();
    resetForm();
  } catch (err) {
    error.value = err.message || "保存に失敗しました";
  } finally {
    loading.value = false;
  }
};

const ensureCategory = async (name) => {
  if (!name) return;
  if (categories.value.some((cat) => cat.name === name)) return;

  await fetch(`${apiBase}/categories`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  }).then(checkResponse);
  await loadCategories();
};

const loadCategories = async () => {
  const response = await fetch(`${apiBase}/categories`);
  if (!response.ok) throw new Error("分類の取得に失敗しました");
  categories.value = await response.json();
};

const loadTodos = async () => {
  loading.value = true;
  error.value = "";
  try {
    const params = new URLSearchParams();
    params.set("status", statusFilter.value);
    if (categoryFilter.value !== "all") {
      params.set("category", categoryFilter.value);
    }

    const response = await fetch(`${apiBase}/todos?${params.toString()}`);
    if (!response.ok) throw new Error("TODOの取得に失敗しました");
    todos.value = await response.json();
  } catch (err) {
    error.value = err.message || "読み込みに失敗しました";
  } finally {
    loading.value = false;
  }
};

const toggleComplete = async (id) => {
  const target = todos.value.find((todo) => todo.id === id);
  if (!target) return;

  try {
    await fetch(`${apiBase}/todos/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed: !target.completed }),
    }).then(checkResponse);
    await loadTodos();
  } catch (err) {
    error.value = err.message || "更新に失敗しました";
  }
};

const deleteTodo = async (id) => {
  try {
    await fetch(`${apiBase}/todos/${id}`, { method: "DELETE" }).then(checkResponse);
    todos.value = todos.value.filter((todo) => todo.id !== id);
  } catch (err) {
    error.value = err.message || "削除に失敗しました";
  }
};

const startEdit = (id) => {
  const target = todos.value.find((todo) => todo.id === id);
  if (!target) return;
  editingId.value = id;
  form.title = target.title;
  form.deadline = target.deadline;
  form.category = target.category;
  scrollToForm();
};

const checkResponse = async (response) => {
  if (response.ok) return response;
  const detail = await response.json().catch(() => ({}));
  const message = detail?.detail || "リクエストが失敗しました";
  throw new Error(message);
};

onMounted(async () => {
  try {
    await loadCategories();
  } catch (err) {
    error.value = err.message;
  }
  await loadTodos();
});
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding-bottom: 120px;
}

.content {
  max-width: 1000px;
  margin: 24px auto;
  display: grid;
  gap: 18px;
  padding: 0 18px;
}

.panel {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 20px;
  padding: 18px;
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.18);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel h2 {
  margin: 4px 0 0;
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  font-size: 12px;
  color: #6b7280;
}

.filter-bar {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.field {
  display: grid;
  gap: 6px;
  font-size: 13px;
  color: #4b5563;
}

.field input,
.field select {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid #d8e3f0;
  background: #f9fbff;
  font-size: 14px;
}

.task-grid {
  display: grid;
  gap: 12px;
  margin-top: 12px;
}

.task-form {
  display: grid;
  gap: 14px;
  margin-top: 12px;
}

.actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

button.primary {
  background: linear-gradient(135deg, #3d6df7, #00a1ff);
  color: #fff;
  border: none;
  padding: 12px 16px;
  border-radius: 12px;
  font-weight: 700;
  box-shadow: 0 12px 30px rgba(0, 161, 255, 0.35);
}

button.ghost {
  background: #f8fbff;
  border: 1px solid #dce7f5;
  color: #1f2937;
  padding: 10px 14px;
  border-radius: 12px;
  font-weight: 600;
}

.error {
  color: #b91c1c;
  font-weight: 600;
}

.muted {
  color: #6b7280;
}
</style>
