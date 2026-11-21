<script setup lang="ts">
import type { QueryStatus } from '@/composables/useAsyncQuery'
import EmptyState from './EmptyState.vue'
import LoadingState from './LoadingState.vue'
import ErrorState from './ErrorState.vue'

/** 三态组合：加载 / 错误 / 空结果 / 正常内容。所有数据区块都经由它呈现状态。 */
withDefaults(
  defineProps<{
    status: QueryStatus
    error?: string
    empty?: boolean
    emptyText?: string
    emptyTitle?: string
    loadingText?: string
  }>(),
  {
    error: '',
    empty: false,
    emptyText: '接口返回空结果，不是 0；请放宽筛选条件或重置。',
    emptyTitle: '当前条件下没有数据',
    loadingText: '加载中…',
  },
)
</script>

<template>
  <LoadingState v-if="status === 'loading'" :label="loadingText" />
  <ErrorState v-else-if="status === 'error'" :message="error" />
  <EmptyState v-else-if="status === 'success' && empty" :title="emptyTitle" :hint="emptyText" />
  <slot v-else />
</template>
