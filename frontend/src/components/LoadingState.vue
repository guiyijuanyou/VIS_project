<script setup lang="ts">
/** 加载态：静态骨架条，不做循环高亮动画 */
withDefaults(defineProps<{ label?: string }>(), { label: '加载中…' })
</script>

<template>
  <div class="loading" role="status" aria-live="polite">
    <span class="loading__label">{{ label }}</span>
    <span class="loading__bars" aria-hidden="true">
      <span class="loading__bar loading__bar--wide"></span>
      <span class="loading__bar"></span>
      <span class="loading__bar loading__bar--narrow"></span>
    </span>
  </div>
</template>

<style scoped>
.loading {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-4);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg);
}

.loading__label {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.loading__bars {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.loading__bar {
  height: 8px;
  width: 62%;
  border-radius: var(--radius-sm);
  background: var(--color-surface-alt);
}

.loading__bar--wide {
  width: 88%;
}

.loading__bar--narrow {
  width: 40%;
}
</style>
