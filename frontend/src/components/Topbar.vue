<script setup lang="ts">
/** 顶部条：模块位置、当前条件摘要、全局重置 */
defineProps<{ title: string; summary: string; activeCount: number; dataVersion?: string }>()
const emit = defineEmits<{ (e: 'reset'): void }>()
</script>

<template>
  <header class="topbar">
    <div class="topbar__left">
      <span class="topbar__crumb">工作区</span>
      <span class="topbar__sep">/</span>
      <span class="topbar__title">{{ title }}</span>
    </div>

    <div class="topbar__right">
      <span class="topbar__summary" :title="summary">
        <span class="topbar__summary-label">条件</span>
        {{ summary }}
      </span>
      <span v-if="activeCount > 0" class="topbar__count num">{{ activeCount }} 项</span>
      <button class="btn btn--ghost" type="button" :disabled="activeCount === 0" @click="emit('reset')">
        清除筛选
      </button>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  height: var(--topbar-height);
  padding: 0 var(--space-6);
  background: var(--color-surface);
  border-bottom: var(--border-width) solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 10;
}

.topbar__left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
}

.topbar__crumb {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.topbar__sep {
  color: var(--color-border-strong);
}

.topbar__title {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
}

.topbar__right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
}

.topbar__summary {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  max-width: 46vw;
  padding: 2px var(--space-2);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface-alt);
  color: var(--color-text-secondary);
  font-size: var(--text-xs);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.topbar__summary-label {
  color: var(--color-text-muted);
}

.topbar__count {
  font-size: var(--text-xs);
  color: var(--color-brand);
  border: var(--border-width) solid var(--color-brand-soft);
  background: var(--color-brand-soft);
  border-radius: var(--radius-sm);
  padding: 1px var(--space-2);
}
</style>
