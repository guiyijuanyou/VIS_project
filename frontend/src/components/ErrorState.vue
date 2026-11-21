<script setup lang="ts">
/** 错误态：说明失败原因与后果，不引导用户以模拟数据顶替 */
withDefaults(defineProps<{ title?: string; message?: string; hint?: string }>(), {
  title: '数据加载失败',
  message: '',
  hint: 'real 模式请确认人员二的后端已启动；界面不会用模拟数据顶替失败的请求。',
})
</script>

<template>
  <div class="error" role="alert">
    <svg class="error__icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true">
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 8v5M12 15.6v.6" stroke-linecap="round" />
    </svg>
    <div class="error__text">
      <strong class="error__title">{{ title }}</strong>
      <span v-if="message" class="error__message mono">{{ message }}</span>
      <span v-if="hint" class="error__hint">{{ hint }}</span>
    </div>
  </div>
</template>

<style scoped>
.error {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-3);
  border: var(--border-width) solid #ecd3cf;
  border-radius: var(--radius-sm);
  background: var(--color-negative-soft);
  color: var(--color-negative);
}

.error__icon {
  flex: none;
  margin-top: 1px;
}

.error__text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.error__title {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
}

.error__message {
  font-size: var(--text-xs);
  word-break: break-all;
}

.error__hint {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}
</style>
