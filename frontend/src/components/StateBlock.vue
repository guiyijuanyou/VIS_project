<script setup lang="ts">
import type { QueryStatus } from '@/composables/useAsyncQuery'

/** 加载 / 错误 / 空结果三态统一呈现：任何图都必须能说明“现在为什么没有数据” */
withDefaults(
  defineProps<{
    status: QueryStatus
    error?: string
    empty?: boolean
    emptyText?: string
    loadingText?: string
  }>(),
  {
    error: '',
    empty: false,
    emptyText: '当前条件下没有数据（接口返回空结果，不是 0）。',
    loadingText: '加载中…',
  },
)
</script>

<template>
  <div v-if="status === 'loading'" class="state state--loading">{{ loadingText }}</div>
  <div v-else-if="status === 'error'" class="state state--error">
    <strong>数据加载失败</strong>
    <p class="state__message">{{ error }}</p>
    <p class="state__hint">real 模式请确认人员二的后端已启动；界面不会用模拟数据顶替失败的请求。</p>
  </div>
  <div v-else-if="status === 'success' && empty" class="state state--empty">{{ emptyText }}</div>
  <slot v-else />
</template>

<style scoped>
.state {
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
  font-size: 12.5px;
  color: var(--color-text-muted);
  text-align: center;
}

.state--error {
  border-color: #f0c9c6;
  background: var(--color-danger-soft);
  color: var(--color-danger);
  text-align: left;
}

.state__message { margin: 4px 0; }

.state__hint { margin: 0; font-size: 11.5px; opacity: 0.85; }
</style>
