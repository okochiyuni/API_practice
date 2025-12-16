<template>
  <header class="app-header">
    <div class="branding">
      <div class="badge" aria-hidden="true">TODO</div>
      <div>
        <p class="subtitle">{{ subtitle }}</p>
        <h1 class="title">{{ title }}</h1>
      </div>
    </div>
    <div class="actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup>
const { title, subtitle } = defineProps({
  title: {
    type: String,
    default: "My Tasks",
  },
  subtitle: {
    type: String,
    default: "今日のタスクを整理しましょう",
  },
});
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, #1e1f2f, #2f3248);
  color: #f8fbff;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.18);
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
}

.branding {
  display: flex;
  align-items: center;
  gap: 12px;
}

.badge {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.08);
  display: grid;
  place-items: center;
  font-weight: 700;
  letter-spacing: 0.8px;
  border: 1px solid rgba(255, 255, 255, 0.14);
}

.subtitle {
  margin: 0;
  font-size: 12px;
  opacity: 0.8;
}

.title {
  margin: 2px 0 0;
  font-size: 22px;
  line-height: 1.2;
  letter-spacing: 0.3px;
}

.actions :deep(> *) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>
