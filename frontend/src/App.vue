<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { API_MODE } from '@/api/client'
import { api } from '@/api/endpoints'
import { useFilterStore } from '@/stores/filter'
import FilterPanel from '@/components/FilterPanel.vue'

const store = useFilterStore()
const metaError = ref('')

onMounted(async () => {
  try {
    store.setMeta(await api.meta())
  } catch (caught) {
    metaError.value = caught instanceof Error ? caught.message : String(caught)
  }
})

const tabs = [
  { name: 'regions', path: '/regions', label: '地区总览' },
  { name: 'jobs', path: '/jobs', label: '职位画像与差异' },
  { name: 'evidence', path: '/evidence', label: '条件比较与证据' },
]
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="app-header__main">
        <h1 class="app-header__title">职位画像与城市就业机会可视分析系统</h1>
        <p class="app-header__subtitle">基于 ChinaVis 2024 虚拟招聘数据，地区与职位以代码展示</p>
      </div>
      <div class="app-header__meta">
        <span class="app-header__badge">{{ API_MODE === 'mock' ? '模拟数据' : '真实接口' }}</span>
        <span class="muted">{{ store.meta?.dataVersion ?? '版本未知' }}</span>
      </div>
    </header>

    <div v-if="API_MODE === 'mock'" class="banner banner--mock">
      <strong>模拟数据模式</strong>
      <span>当前所有数值由前端模拟数据生成（非真实统计），仅用于界面与交互开发；人员二冻结接口后改为 real 模式。</span>
    </div>
    <div v-if="metaError" class="banner banner--error">
      <strong>无法读取接口元信息</strong>
      <span>{{ metaError }}</span>
    </div>

    <nav class="tab-nav">
      <router-link v-for="tab in tabs" :key="tab.name" :to="tab.path" class="tab-nav__item" active-class="tab-nav__item--active">
        {{ tab.label }}
      </router-link>
      <div class="tab-nav__spacer"></div>
      <span class="tab-nav__summary" title="当前筛选条件">条件：{{ store.summary }}</span>
      <button class="btn btn--ghost" type="button" :disabled="store.activeCount === 0" @click="store.resetFilters()">清除筛选</button>
    </nav>

    <main class="app-main">
      <FilterPanel />
      <section class="app-content">
        <router-view />
      </section>
    </main>

    <footer class="app-footer">
      <span>数据说明：官方数据为虚拟招聘数据，无真实名称映射、技能与时间字段；地区/职位/学历/经验均为代码，系统不做语义猜测。</span>
      <span>薪资单位：{{ store.salaryUnit }}；样本低于 {{ store.sampleThreshold }} 的对象从主排名剔除（展示阈值，非统计显著性）。</span>
    </footer>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.app-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5) var(--space-3);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.app-header__title { font-size: 19px; }

.app-header__subtitle { margin: 2px 0 0; color: var(--color-text-muted); font-size: 12.5px; }

.app-header__meta { display: flex; align-items: center; gap: var(--space-2); font-size: 12px; }

.app-header__badge {
  background: var(--color-warning-soft);
  color: var(--color-warning);
  border-radius: 999px;
  padding: 2px 10px;
  font-weight: 600;
}

.banner {
  display: flex;
  gap: var(--space-3);
  padding: 8px var(--space-5);
  font-size: 12.5px;
}

.banner--mock { background: var(--color-warning-soft); color: var(--color-warning); }

.banner--error { background: var(--color-danger-soft); color: var(--color-danger); }

.tab-nav {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: 0 var(--space-5);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.tab-nav__item {
  padding: 10px 14px;
  border-bottom: 2px solid transparent;
  color: var(--color-text-muted);
  font-size: 13.5px;
}

.tab-nav__item--active {
  border-bottom-color: var(--color-primary);
  color: var(--color-primary);
  font-weight: 600;
}

.tab-nav__spacer { flex: 1; }

.tab-nav__summary {
  max-width: 42vw;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-text-muted);
  font-size: 12px;
  margin-right: var(--space-2);
}

.app-main {
  flex: 1;
  display: grid;
  grid-template-columns: 248px minmax(0, 1fr);
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  align-items: start;
}

.app-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  min-width: 0;
}

.app-footer {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: var(--space-3) var(--space-5);
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-muted);
  font-size: 11.5px;
}

@media (max-width: 1080px) {
  .app-main { grid-template-columns: 1fr; }
}
</style>
