<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { api } from '@/api/endpoints'
import { useAsyncQuery } from '@/composables/useAsyncQuery'
import { useFilterStore } from '@/stores/filter'
import { formatCount, salaryStatusLabel } from '@/utils/format'
import StateBlock from './StateBlock.vue'

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

function go(next: number) {
  if (next < 1 || next > maxPage.value) return
  page.value = next
  void query.run()
}
</script>

<template>
  <div class="record-table">
    <div class="record-table__toolbar">
      <span class="muted">共 {{ formatCount(total) }} 条 · 每页 {{ pageSize }} 条 · 第 {{ page }} / {{ maxPage }} 页</span>
      <div class="record-table__pager">
        <button class="btn" type="button" :disabled="page <= 1" @click="go(page - 1)">上一页</button>
        <button class="btn" type="button" :disabled="page >= maxPage" @click="go(page + 1)">下一页</button>
      </div>
    </div>

    <StateBlock :status="query.status.value" :error="query.error.value" :empty="rows.length === 0" empty-text="当前条件下没有明细记录。">
      <div class="record-table__scroll">
        <table class="table">
          <thead>
            <tr>
              <th>来源行号</th>
              <th>record_id</th>
              <th>job_title</th>
              <th>city</th>
              <th>company_type</th>
              <th>education</th>
              <th>experience</th>
              <th>salary（原串）</th>
              <th>生效区间</th>
              <th>解析状态</th>
              <th>重复</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.recordId">
              <td>{{ row.sourceRow }}</td>
              <td class="mono">{{ row.recordId }}</td>
              <td class="mono">{{ row.jobTitle }}</td>
              <td class="mono">{{ row.city }}</td>
              <td class="mono">{{ row.companyType }}</td>
              <td class="mono">{{ row.education }}</td>
              <td class="mono">{{ row.experience }}</td>
              <td class="mono">{{ row.salary }}</td>
              <td class="mono">
                {{ row.salaryMid === null ? '—（' + salaryStatusLabel(row.salaryStatus) + '）' : `${row.salaryLower}～${row.salaryUpper}（中点 ${row.salaryMid}）` }}
              </td>
              <td>{{ salaryStatusLabel(row.salaryStatus) }}</td>
              <td>{{ row.isExtraDuplicate ? '额外重复' : '' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </StateBlock>
  </div>
</template>

<style scoped>
.record-table__toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2); font-size: 12px; }

.record-table__pager { display: flex; gap: var(--space-2); }

.record-table__scroll { overflow-x: auto; }
</style>
