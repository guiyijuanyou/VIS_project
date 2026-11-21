<script setup lang="ts">
/** 指标卡：名称清晰、数值突出、单位与口径在次级层级 */
defineProps<{ label: string; value: string; unit?: string; caption?: string; tone?: 'default' | 'positive' | 'negative' | 'warning' }>()
</script>

<template>
  <div class="metric">
    <span class="metric__label">{{ label }}</span>
    <span class="metric__value num" :class="tone && tone !== 'default' ? `metric__value--${tone}` : undefined">
      {{ value }}
      <span v-if="unit" class="metric__unit">{{ unit }}</span>
    </span>
    <span v-if="caption" class="metric__caption">{{ caption }}</span>
  </div>
</template>

<style scoped>
.metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: var(--space-3);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  min-width: 0;
}

.metric__label {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.metric__value {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
}

.metric__value--positive {
  color: var(--color-positive);
}

.metric__value--negative {
  color: var(--color-negative);
}

.metric__value--warning {
  color: var(--color-warning);
}

.metric__unit {
  font-size: var(--text-xs);
  font-weight: var(--weight-normal);
  color: var(--color-text-secondary);
}

.metric__caption {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
