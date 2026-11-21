<script setup lang="ts">
/** 页内视图切换：下划线式，低饱和选中态 */
defineProps<{ items: { key: string; label: string }[]; modelValue: string }>()
const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>()
</script>

<template>
  <div class="tabs" role="tablist">
    <button
      v-for="item in items"
      :key="item.key"
      type="button"
      role="tab"
      class="tabs__item"
      :class="{ 'tabs__item--active': item.key === modelValue }"
      :aria-selected="item.key === modelValue"
      @click="emit('update:modelValue', item.key)"
    >
      {{ item.label }}
    </button>
  </div>
</template>

<style scoped>
.tabs {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  border-bottom: var(--border-width) solid var(--color-border);
}

.tabs__item {
  position: relative;
  padding: var(--space-2) 0;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  transition: color var(--transition-fast);
}

.tabs__item:hover {
  color: var(--color-text);
}

.tabs__item--active {
  color: var(--color-brand);
  font-weight: var(--weight-semibold);
}

.tabs__item--active::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1px;
  height: 2px;
  background: var(--color-brand);
}
</style>
