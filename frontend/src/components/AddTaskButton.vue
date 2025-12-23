<template>
  <button type="button" class="add-task" @click="$emit('click')">
    <span class="icon" aria-hidden="true">＋</span>
    <span class="label">{{ label }}</span>
  </button>
</template>

<script setup>
const { label } = defineProps({
  label: {
    type: String,
    default: "タスクを追加",
  },
});

defineEmits(["click"]);
</script>

<style scoped>
.add-task {
  position: fixed;
  right: 20px;
  bottom: 24px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border-radius: 18px;
  border: none;
  background: linear-gradient(135deg, #00bfa5, #00a1ff);
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.3px;
  box-shadow: 0 14px 30px rgba(0, 161, 255, 0.3);
}

.icon {
  width: 28px;
  height: 28px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.16);
  display: grid;
  place-items: center;
  font-size: 18px;
}

.label {
  font-size: 15px;
}
</style>
