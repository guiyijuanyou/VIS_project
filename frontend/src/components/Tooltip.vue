<script setup lang="ts">
/** 轻量文本提示：仅用于补充口径/原代码，不使用装饰性动效 */
defineProps<{ text: string; tone?: 'dark' | 'light' }>()
</script>

<template>
  <span class="tooltip" :class="tone === 'light' ? 'tooltip--light' : undefined">
    <slot />
    <span class="tooltip__bubble" role="tooltip">{{ text }}</span>
  </span>
</template>

<style scoped>
.tooltip {
  position: relative;
  display: inline-flex;
  align-items: center;
  max-width: 100%;
}

.tooltip__bubble {
  position: absolute;
  left: 0;
  bottom: calc(100% + 6px);
  z-index: 30;
  max-width: 280px;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  background: var(--color-text);
  color: #ffffff;
  font-size: var(--text-xs);
  line-height: var(--line-normal);
  white-space: normal;
  opacity: 0;
  visibility: hidden;
  transition: opacity var(--transition-fast);
  box-shadow: var(--shadow-overlay);
  pointer-events: none;
}

.tooltip--light .tooltip__bubble {
  background: var(--color-surface);
  color: var(--color-text);
  border: var(--border-width) solid var(--color-border);
}

.tooltip:hover .tooltip__bubble,
.tooltip:focus-within .tooltip__bubble {
  opacity: 1;
  visibility: visible;
}
</style>
