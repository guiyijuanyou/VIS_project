<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/endpoints'
import { emptyFilters, useFilterStore, type FilterDimension } from '@/stores/filter'

/** 侧边筛选：五个代码维度，全站唯一条件源；只做代码精确匹配，不做语义猜测 */
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

const dimensions = computed<{ key: FilterDimension; title: string; codes: string[] }[]>(() => [
  { key: 'regions', title: '地区代码', codes: regionCodes.value },
  { key: 'industries', title: '行业代码', codes: store.industryOptions },
  { key: 'jobs', title: '职位代码', codes: jobCodes.value },
  { key: 'educations', title: '学历代码', codes: store.educationOptions },
  { key: 'experiences', title: '经验代码', codes: store.experienceOptions },
])
</script>

<template>
  <aside class="filter-panel card">
    <div class="card__header">
      <h2 class="card__title">筛选条件</h2>
      <button class="btn btn--ghost" type="button" :disabled="store.activeCount === 0" @click="store.resetFilters()">
        重置
      </button>
    </div>

    <p class="filter-panel__note">同字段多值 OR，不同字段 AND；代码精确匹配且区分大小写。</p>

    <div v-if="optionError" class="filter-panel__error">{{ optionError }}</div>

    <section v-for="dimension in dimensions" :key="dimension.key" class="filter-group">
      <header class="filter-group__header">
        <span>{{ dimension.title }}</span>
        <button
          v-if="store.filters[dimension.key].length"
          class="btn btn--ghost filter-group__clear"
          type="button"
          @click="store.clearDimension(dimension.key)"
        >
          清除
        </button>
      </header>
      <div class="filter-group__chips">
        <button
          v-for="code in dimension.codes"
          :key="code"
          type="button"
          class="chip"
          :class="{ 'chip--active': store.isActive(dimension.key, code) }"
          :title="code"
          @click="store.toggle(dimension.key, code)"
        >
          {{ code }}
        </button>
        <span v-if="dimension.codes.length === 0" class="muted">暂无选项（等待 /api/v1/meta 与 /api/v1/regions）</span>
      </div>
    </section>
  </aside>
</template>

<style scoped>
.filter-panel {
  position: sticky;
  top: var(--space-4);
  max-height: calc(100vh - 140px);
  overflow-y: auto;
}

.filter-panel__note {
  margin: 0 0 var(--space-3);
  font-size: 11.5px;
  color: var(--color-text-muted);
}

.filter-panel__error {
  margin-bottom: var(--space-3);
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  background: var(--color-danger-soft);
  color: var(--color-danger);
  font-size: 11.5px;
}

.filter-group { margin-bottom: var(--space-3); }

.filter-group__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: var(--space-1);
}

.filter-group__clear { font-size: 11px; padding: 0 4px; }

.filter-group__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.chip { font-size: 11.5px; }
</style>
