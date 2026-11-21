<script setup lang="ts">
/** 单选下拉：用于在长列表（地区 / 职位代码）中追加一个值，不改变既有筛选语义 */
const props = withDefaults(
  defineProps<{ options: { value: string; label: string }[]; placeholder?: string; width?: string; disabled?: boolean }>(),
  { placeholder: '选择…', width: '100%', disabled: false },
)
const emit = defineEmits<{ (e: 'change', value: string): void }>()

function onChange(event: Event) {
  const target = event.target as HTMLSelectElement
  const value = target.value
  if (!value) return
  emit('change', value)
  // 复位为占位项：组件保持“一次性选择”的行为
  target.value = ''
}
</script>

<template>
  <span class="select" :style="{ width: props.width }">
    <select class="select__native field" :disabled="props.disabled" @change="onChange">
      <option value="" selected>{{ props.placeholder }}</option>
      <option v-for="option in props.options" :key="option.value" :value="option.value">{{ option.label }}</option>
    </select>
    <svg class="select__caret" viewBox="0 0 10 6" width="10" height="6" aria-hidden="true">
      <path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" />
    </svg>
  </span>
</template>

<style scoped>
.select {
  position: relative;
  display: inline-flex;
  min-width: 0;
}

.select__native {
  width: 100%;
  appearance: none;
  padding-right: var(--space-6);
  cursor: pointer;
}

.select__caret {
  position: absolute;
  right: var(--space-2);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  pointer-events: none;
}
</style>
