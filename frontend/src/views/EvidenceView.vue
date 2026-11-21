<script setup lang="ts">
import { computed, watch } from 'vue'
import { api } from '@/api/endpoints'
import { useAsyncQuery } from '@/composables/useAsyncQuery'
import { useFilterStore } from '@/stores/filter'
import PageHeader from '@/components/PageHeader.vue'
import ChartContainer from '@/components/ChartContainer.vue'
import RegionCompare from '@/components/RegionCompare.vue'
import RecordTable from '@/components/RecordTable.vue'
import StateBlock from '@/components/StateBlock.vue'
import Tag from '@/components/Tag.vue'

/** 页签 3：条件比较与证据（C05）—— 固定条件比较地区，并能翻页打开来源记录 */
const store = useFilterStore()

const regionsQuery = useAsyncQuery((signal) => api.regions(store.filters, signal))

watch(() => store.queryKey, () => { void regionsQuery.run() }, { immediate: true })

const regionRows = computed(() => regionsQuery.data.value?.items ?? [])
/** 条件比较：优先使用手动点选的地区，否则取记录量最高的前 3 个 */
const compared = computed(() => (store.compareRegions.length >= 2 ? store.compareRegions : regionRows.value.slice(0, 3).map((row) => row.region)))
</script>

<template>
  <PageHeader
    title="条件比较与证据核对"
    subtitle="固定当前条件比较地区数值，并逐页打开来源记录核对。任何结论都应能追溯到这里的分母与样本数。"
  >
    <template #actions>
      <Tag tone="neutral">{{ store.meta?.dataVersion ?? '版本未知' }}</Tag>
    </template>
  </PageHeader>

  <ChartContainer title="当前条件与数据版本" hint="条件、单位、重复口径与分位数方法必须与图表数值一致。">
    <dl class="conditions">
      <div><dt>筛选条件</dt><dd>{{ store.summary }}</dd></div>
      <div><dt>焦点职位</dt><dd class="mono">{{ store.focusJob || '未选择（职位页）' }}</dd></div>
      <div><dt>薪资单位</dt><dd>{{ store.salaryUnit }}</dd></div>
      <div><dt>重复口径</dt><dd>{{ store.meta?.duplicatePolicy ?? '—' }}</dd></div>
      <div><dt>分位数方法</dt><dd>{{ store.meta?.quantileMethod ?? '—' }}</dd></div>
      <div><dt>样本阈值</dt><dd class="num">{{ store.sampleThreshold }} 条（展示阈值，非统计显著性）</dd></div>
      <div><dt>版本</dt><dd class="num">{{ store.meta?.dataVersion ?? '—' }} / {{ store.meta?.apiVersion ?? '—' }}</dd></div>
    </dl>
  </ChartContainer>

  <ChartContainer
    title="固定条件下比较地区"
    :hint="`比较对象：${compared.join('、') || '无'}；分母为该条件下的记录数。`"
  >
    <StateBlock
      :status="regionsQuery.status.value"
      :error="regionsQuery.error.value"
      :empty="regionRows.length === 0"
      empty-text="当前条件下没有地区数据，无法比较。"
    >
      <RegionCompare :items="regionRows" :selected="compared" @remove="store.toggleCompareRegion" />
    </StateBlock>
  </ChartContainer>

  <ChartContainer title="来源记录明细" hint="展示原字段、解析状态与来源行号；条件与上方图表一致，翻页不丢条件。">
    <RecordTable />
  </ChartContainer>
</template>

<style scoped>
.conditions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-2) var(--space-4);
  margin: 0;
}

.conditions > div {
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding-bottom: var(--space-2);
  border-bottom: var(--border-width) solid var(--color-border);
}

.conditions dt {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.conditions dd {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--color-text);
  overflow-wrap: anywhere;
}
</style>
