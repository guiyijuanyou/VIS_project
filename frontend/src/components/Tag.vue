<script setup lang="ts">
/** 标签：筛选值、状态与元信息共用；圆角 4px，不使用胶囊形态 */
withDefaults(
  defineProps<{ tone?: 'neutral' | 'brand' | 'positive' | 'negative' | 'warning'; removable?: boolean; title?: string; active?: boolean }>(),
  { tone: 'neutral', removable: false, active: false },
)
const emit = defineEmits<{ (e: 'remove'): void }>()
</script>

<template>
  <span class="tag" :class="[`tag--${tone}`, { 'tag--active': active }]" :title="title">
    <slot />
    <button v-if="removable" class="tag__remove" type="button" aria-label="移除" @click.stop="emit('remove')">×</button>
  </span>
</template>

<style scoped>
.tag {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  height: 22px;
  padding: 0 var(--space-2);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  font-size: var(--text-xs);
  line-height: 1;
  white-space: nowrap;
}

.tag--brand {
  border-color: var(--color-brand);
  background: var(--color-brand-soft);
  color: var(--color-brand);
}

.tag--positive {
  border-color: #cfe4dd;
  background: var(--color-positive-soft);
  color: var(--color-positive);
}

.tag--negative {
  border-color: #ecd3cf;
  background: var(--color-negative-soft);
  color: var(--color-negative);
}

.tag--warning {
  border-color: #e8d9bf;
  background: var(--color-warning-soft);
  color: var(--color-warning);
}

.tag--active {
  border-color: var(--color-brand);
  color: var(--color-brand);
}

.tag__remove {
  border: none;
  background: transparent;
  padding: 0;
  margin-left: 2px;
  font-size: 12px;
  line-height: 1;
  color: inherit;
  opacity: 0.7;
}

.tag__remove:hover {
  opacity: 1;
}
</style>
