<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/endpoints'
import { emptyFilters, useFilterStore, type FilterDimension } from '@/stores/filter'
import Select from './Select.vue'
import Tag from './Tag.vue'

/** 分析条件面板：五个代码维度，全站唯一条件源；长列表用下拉追加，短列表直接点选 */
const store = useFilterStore()
const regionCodes = ref<string[]>([])
const jobCodes = ref<string[]>([])
const optionError = ref('')

onMounted(async () => {
  try {
    const [regions, jobs] = await Promise.all([api.regions(emptyFilters()), api.jobOptions('', 1, 50)])
    regionCodes.value = regions.items.map((item) => item.region)
    jobCodes.value = jobs.items.map((item) => item.code)
  } catch (caught) {
    optionError.value = caught instanceof Error ? caught.message : String(caught)
  }
})

interface DimensionView {
  key: FilterDimension
  title: string
  codes: string[]
  /** 选项较多时只提供下拉追加，避免长列表挤占版面 */
  compact: boolean
}

const dimensions = computed<DimensionView[]>(() => [
  { key: 'regions', title: '地区代码', codes: regionCodes.value, compact: true },
  { key: 'industries', title: '行业代码', codes: store.industryOptions, compact: false },
  { key: 'jobs', title: '职位代码', codes: jobCodes.value, compact: true },
  { key: 'educations', title: '学历代码', codes: store.educationOptions, compact: false },
  { key: 'experiences', title: '经验代码', codes: store.experienceOptions, compact: false },
])

function optionsFor(dimension: DimensionView) {
  const selected = store.filters[dimension.key]
  return dimension.codes.filter((code) => !selected.includes(code)).map((code) => ({ value: code, label: code }))
}
</script>

<template>
  <aside class="panel filter">
    <header class="filter__head">
      <h2 class="filter__title">分析条件</h2>
      <button class="btn btn--ghost" type="button" :disabled="store.activeCount === 0" @click="store.resetFilters()">
        重置
      </button>
    </header>
    <p class="filter__note">同字段多值 OR，不同字段 AND；代码精确匹配且区分大小写。</p>

    <div v-if="optionError" class="filter__error">{{ optionError }}</div>

    <section v-for="dimension in dimensions" :key="dimension.key" class="filter__group">
      <header class="filter__group-head">
        <span class="filter__group-title">{{ dimension.title }}</span>
        <span class="filter__group-count num">{{ store.filters[dimension.key].length }}</span>
      </header>

      <div v-if="store.filters[dimension.key].length" class="filter__values">
        <Tag
          v-for="code in store.filters[dimension.key]"
          :key="code"
          tone="brand"
          removable
          :title="code"
          @remove="store.toggle(dimension.key, code)"
        >
          {{ code }}
        </Tag>
      </div>

      <Select
        v-if="dimension.codes.length"
        :options="optionsFor(dimension)"
        :placeholder="dimension.compact ? `＋ 添加${dimension.title}` : `＋ 添加${dimension.title}`"
        @change="(value) => store.toggle(dimension.key, value)"
      />
      <p v-else class="filter__empty">暂无选项（等待 /api/v1/meta 与 /api/v1/regions）</p>
    </section>
  </aside>
</template>

<style scoped>
.filter {
  position: sticky;
  top: calc(var(--topbar-height) + var(--space-4));
  padding: var(--space-4);
  max-height: calc(100vh - var(--topbar-height) - var(--space-6));
  overflow-y: auto;
}

.filter__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.filter__title {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
}

.filter__note {
  margin-top: var(--space-1);
  padding-bottom: var(--space-3);
  border-bottom: var(--border-width) solid var(--color-border);
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.filter__error {
  margin-top: var(--space-3);
  padding: var(--space-2);
  border: var(--border-width) solid #ecd3cf;
  border-radius: var(--radius-sm);
  background: var(--color-negative-soft);
  color: var(--color-negative);
  font-size: var(--text-xs);
}

.filter__group {
  padding: var(--space-3) 0;
  border-bottom: var(--border-width) solid var(--color-border);
}

.filter__group:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.filter__group-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-2);
}

.filter__group-title {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
}

.filter__group-count {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.filter__values {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  margin-bottom: var(--space-2);
}

.filter__empty {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}
</style>
