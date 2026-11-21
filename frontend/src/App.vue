<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { API_MODE } from '@/api/client'
import { api } from '@/api/endpoints'
import { useFilterStore } from '@/stores/filter'
import Sidebar from '@/components/Sidebar.vue'
import Topbar from '@/components/Topbar.vue'
import FilterPanel from '@/components/FilterPanel.vue'

const store = useFilterStore()
const route = useRoute()
const metaError = ref('')

onMounted(async () => {
  try {
    store.setMeta(await api.meta())
  } catch (caught) {
    metaError.value = caught instanceof Error ? caught.message : String(caught)
  }
})

const moduleTitle = computed(() => (route.meta.title as string | undefined) ?? '分析工作区')
</script>

<template>
  <div class="app-shell">
    <Sidebar :mode="API_MODE" :data-version="store.meta?.dataVersion" />

    <div class="app-body">
      <Topbar
        :title="moduleTitle"
        :summary="store.summary"
        :active-count="store.activeCount"
        :data-version="store.meta?.dataVersion"
        @reset="store.resetFilters()"
      />

      <div v-if="API_MODE === 'mock'" class="notice notice--warning">
        <strong>模拟数据模式</strong>
        <span>当前数值由前端模拟数据生成，非真实统计；人员二冻结接口后改为 real 模式。</span>
      </div>
      <div v-if="metaError" class="notice notice--negative">
        <strong>无法读取接口元信息</strong>
        <span>{{ metaError }}</span>
      </div>

      <main class="workspace">
        <div class="workspace__content">
          <router-view />
        </div>
        <FilterPanel class="workspace__rail" />
      </main>

      <footer class="app-footer">
        <span>官方数据为虚拟招聘数据，无真实名称映射、技能与时间字段；地区、职位、学历、经验均为代码，系统不做语义猜测。</span>
        <span>薪资单位：{{ store.salaryUnit }}；样本低于 {{ store.sampleThreshold }} 的对象从主排名剔除（展示阈值，非统计显著性）。</span>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
  min-height: 100vh;
  background: var(--color-bg);
}

.app-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 100vh;
}

.workspace {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) var(--rail-width);
  gap: var(--space-4);
  align-items: start;
  width: 100%;
  max-width: var(--content-max);
  margin: 0 auto;
  padding: var(--space-4) var(--space-6) var(--space-6);
}

.workspace__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  min-width: 0;
}

.workspace__rail {
  min-width: 0;
}

.app-footer {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: var(--space-3) var(--space-6);
  border-top: var(--border-width) solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-muted);
  font-size: var(--text-xs);
}

@media (max-width: 1200px) {
  .workspace {
    grid-template-columns: minmax(0, 1fr);
  }

  .workspace__rail {
    order: -1;
  }
}

@media (max-width: 1024px) {
  .app-shell {
    grid-template-columns: 1fr;
  }
}
</style>
