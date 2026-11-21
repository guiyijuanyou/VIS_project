<script setup lang="ts">
/** 图表容器：统一标题、口径说明、右上角元信息与内容留白 */
defineProps<{ title: string; hint?: string; meta?: string }>()
</script>

<template>
  <section class="panel chart">
    <header class="chart__head">
      <div class="chart__titles">
        <h2 class="chart__title">{{ title }}</h2>
        <p v-if="hint" class="chart__hint">{{ hint }}</p>
      </div>
      <div class="chart__meta">
        <slot name="meta">
          <span v-if="meta" class="chart__meta-text">{{ meta }}</span>
        </slot>
      </div>
    </header>
    <div class="chart__body">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.chart {
  padding: var(--space-4);
}

.chart__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: var(--border-width) solid var(--color-border);
  margin-bottom: var(--space-3);
}

.chart__titles {
  min-width: 0;
}

.chart__title {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
}

.chart__hint {
  margin-top: 2px;
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.chart__meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex: none;
}

.chart__meta-text {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}
</style>
