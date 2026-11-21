<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { api } from '@/api/endpoints'
import { useAsyncQuery } from '@/composables/useAsyncQuery'
import { useFilterStore } from '@/stores/filter'
import { formatCount, salaryStatusLabel } from '@/utils/format'
import StateBlock from './StateBlock.vue'
import DataTable from './DataTable.vue'
import type { DataTableColumn } from './table-types'
import Pagination from './Pagination.vue'
import Tag from './Tag.vue'

/** C05：分页明细与来源证据；解析状态原样展示，不把不可用报价显示成 0 */
const store = useFilterStore()
const page = ref(1)
const pageSize = 20

const query = useAsyncQuery((signal) => api.records(store.filters, page.value, pageSize, signal))

watch(() => store.queryKey, () => {
  page.value = 1
  void query.run()
}, { immediate: true })

const total = computed(() => query.data.value?.total ?? 0)
const maxPage = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const rows = computed(() => query.data.value?.items ?? [])

const columns: DataTableColumn[] = [
  { key: 'sourceRow', label: '来源行号', align: 'right', width: '76px' },
  { key: 'recordId', label: 'record_id', width: '112px' },
  { key: 'jobTitle', label: 'job_title', width: '84px' },
  { key: 'city', label: 'city', width: '72px' },
  { key: 'companyType', label: 'company_type', width: '104px' },
  { key: 'education', label: 'education', width: '80px' },
  { key: 'experience', label: 'experience', width: '84px' },
  { key: 'salary', label: 'salary（原串）', width: '112px' },
  { key: 'mid', label: '生效区间', width: '156px' },
  { key: 'status', label: '解析状态', width: '96px' },
  { key: 'duplicate', label: '重复', width: '72px' },
]

function go(next: number) {
  page.value = next
  void query.run()
}
</script>

<template>
  <div>
    <StateBlock :status="query.status.value" :error="query.error.value" :empty="rows.length === 0" empty-text="当前条件下没有明细记录，请放宽筛选条件或重置。">
      <DataTable :columns="columns" :rows="rows" :row-key="(row) => row.recordId">
        <template #cell="{ row, column }">
          <template v-if="column.key === 'sourceRow'">{{ row.sourceRow }}</template>
          <template v-else-if="column.key === 'recordId'"><span class="mono">{{ row.recordId }}</span></template>
          <template v-else-if="column.key === 'jobTitle'"><span class="mono">{{ row.jobTitle }}</span></template>
          <template v-else-if="column.key === 'city'"><span class="mono">{{ row.city }}</span></template>
          <template v-else-if="column.key === 'companyType'"><span class="mono">{{ row.companyType }}</span></template>
          <template v-else-if="column.key === 'education'"><span class="mono">{{ row.education }}</span></template>
          <template v-else-if="column.key === 'experience'"><span class="mono">{{ row.experience }}</span></template>
          <template v-else-if="column.key === 'salary'"><span class="mono">{{ row.salary }}</span></template>
          <template v-else-if="column.key === 'mid'">
            <span v-if="row.salaryMid === null" class="text-muted">—（{{ salaryStatusLabel(row.salaryStatus) }}）</span>
            <span v-else class="num">{{ row.salaryLower }}～{{ row.salaryUpper }}（中点 {{ row.salaryMid }}）</span>
          </template>
          <template v-else-if="column.key === 'status'">
            <Tag :tone="row.salaryStatus === 'ok' ? 'positive' : row.salaryStatus === 'invalid' ? 'warning' : 'negative'">
              {{ salaryStatusLabel(row.salaryStatus) }}
            </Tag>
          </template>
          <template v-else>
            <Tag v-if="row.isExtraDuplicate" tone="neutral">额外重复</Tag>
            <span v-else class="text-muted">—</span>
          </template>
        </template>
      </DataTable>

      <Pagination :page="page" :page-size="pageSize" :total="total" :max-page="maxPage" @change="go" class="record__pagination" />
    </StateBlock>
  </div>
</template>

<style scoped>
.record__pagination {
  margin-top: var(--space-3);
}
</style>
