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
      <button
        type="button"
        class="icon-button ghost"
        aria-label="タスクを編集"
        @click="$emit('edit', todo.id)"
      >
        <svg viewBox="0 0 24 24" class="icon" aria-hidden="true" focusable="false">
          <path
            d="M4 17.5V20h2.5l9.3-9.3-2.5-2.5L4 17.5Zm13.8-8.8c.2-.2.2-.5 0-.7l-2.8-2.8a.5.5 0 0 0-.7 0l-1.8 1.8 3.5 3.5 1.8-1.8Z"
            fill="currentColor"
          />
        </svg>
      </button>
      <button
        type="button"
        class="icon-button danger"
        aria-label="タスクを削除"
        @click="$emit('delete', todo.id)"
      >
        <svg viewBox="0 0 24 24" class="icon" aria-hidden="true" focusable="false">
          <path
            d="M18.3 5.7a1 1 0 0 0-1.4 0L12 10.6 7.1 5.7a1 1 0 0 0-1.4 1.4L10.6 12l-4.9 4.9a1 1 0 1 0 1.4 1.4L12 13.4l4.9 4.9a1 1 0 1 0 1.4-1.4L13.4 12l4.9-4.9a1 1 0 0 0 0-1.4Z"
            fill="currentColor"
          />
        </svg>
      </button>
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
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.icon-button {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid transparent;
  display: grid;
  place-items: center;
  padding: 0;
  transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease;
}

.icon-button:active {
  transform: translateY(1px);
}

.icon {
  width: 18px;
  height: 18px;
}

.icon-button.ghost {
  border-color: #dfe7f5;
  color: #2f3655;
  background: #f9fbff;
  box-shadow: 0 6px 18px rgba(47, 54, 85, 0.08);
}

.icon-button.danger {
  color: #fff;
  background: linear-gradient(135deg, #f45c43, #eb3349);
  box-shadow: 0 8px 18px rgba(244, 92, 67, 0.2);
}
</style>
