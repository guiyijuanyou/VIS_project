<script setup lang="ts">
/** 空结果：说明“当前条件下没有数据”，不显示为 0 */
withDefaults(defineProps<{ title?: string; hint?: string }>(), {
  title: '当前条件下没有数据',
  hint: '接口返回空结果，不是 0；请放宽筛选条件或重置。',
})
</script>

<template>
  <div class="empty">
    <svg class="empty__icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true">
      <rect x="3.5" y="5.5" width="17" height="13" rx="1.5" />
      <path d="M3.5 10.5h17M8 15h3" stroke-linecap="round" />
    </svg>
    <div class="empty__text">
      <strong class="empty__title">{{ title }}</strong>
      <span v-if="hint" class="empty__hint">{{ hint }}</span>
    </div>
    <slot />
  </div>
</template>

<style scoped>
.empty {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-4);
  border: var(--border-width) dashed var(--color-border-strong);
  border-radius: var(--radius-sm);
  background: var(--color-bg);
  color: var(--color-text-secondary);
}

.empty__icon {
  flex: none;
  margin-top: 1px;
  color: var(--color-text-muted);
}

.empty__text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.empty__title {
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--color-text);
}

.empty__hint {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}
</style>
