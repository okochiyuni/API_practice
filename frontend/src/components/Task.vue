<template>
  <article class="task-card" :class="{ completed: todo.completed }">
    <div class="task-main">
      <button
        type="button"
        class="toggle"
        :aria-pressed="todo.completed"
        @click="$emit('toggle', todo.id)"
      >
        <span class="checkmark" aria-hidden="true">✓</span>
      </button>
      <div class="task-body">
        <p class="category">{{ todo.category }}</p>
        <h2 class="title">{{ todo.title }}</h2>
        <p class="deadline">締切: {{ formattedDeadline }}</p>
      </div>
    </div>
    <div class="actions" aria-label="タスクの操作">
      <button type="button" class="ghost" @click="$emit('edit', todo.id)">編集</button>
      <button type="button" class="danger" @click="$emit('delete', todo.id)">削除</button>
    </div>
  </article>
</template>

<script setup>
import { computed } from "vue";

const { todo } = defineProps({
  todo: {
    type: Object,
    required: true,
  },
});

defineEmits(["toggle", "edit", "delete"]);

const formattedDeadline = computed(() => {
  if (!todo.deadline) {
    return "未設定";
  }

  const parsed = new Date(todo.deadline);
  if (Number.isNaN(parsed.getTime())) {
    return todo.deadline;
  }

  return parsed.toLocaleDateString("ja-JP", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
});
</script>

<style scoped>
.task-card {
  background: #ffffff;
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: 0 10px 32px rgba(18, 42, 66, 0.08);
  display: flex;
  flex-direction: column;
  gap: 12px;
  border: 1px solid rgba(20, 42, 70, 0.05);
  transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
}

.task-card:active {
  transform: translateY(1px);
}

.task-card.completed {
  border-color: #d8e3f0;
  background: #f7fbff;
}

.task-main {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  align-items: center;
}

.toggle {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  border: 1px solid #d7def0;
  background: linear-gradient(135deg, #edf2ff, #f7f9ff);
  display: grid;
  place-items: center;
  color: #3d6df7;
  font-weight: 700;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.task-card.completed .toggle {
  background: linear-gradient(135deg, #3d6df7, #6b8cff);
  color: #fff;
  border-color: rgba(61, 109, 247, 0.35);
  box-shadow: 0 8px 18px rgba(61, 109, 247, 0.2);
}

.checkmark {
  font-size: 18px;
}

.task-body {
  display: grid;
  gap: 2px;
}

.category {
  margin: 0;
  font-size: 12px;
  color: #6a7086;
  letter-spacing: 0.4px;
  text-transform: uppercase;
}

.title {
  margin: 2px 0;
  font-size: 17px;
  color: #1c2340;
  line-height: 1.4;
}

.deadline {
  margin: 0;
  font-size: 13px;
  color: #40506b;
}

.task-card.completed .title,
.task-card.completed .deadline {
  color: #7a86a0;
  text-decoration: line-through;
}

.actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.actions button {
  border-radius: 12px;
  padding: 10px 12px;
  border: 1px solid transparent;
  font-weight: 600;
  font-size: 14px;
}

.actions .ghost {
  border-color: #dfe7f5;
  color: #2f3655;
  background: #f9fbff;
}

.actions .danger {
  color: #fff;
  background: linear-gradient(135deg, #f45c43, #eb3349);
  box-shadow: 0 10px 24px rgba(244, 92, 67, 0.25);
}
</style>
