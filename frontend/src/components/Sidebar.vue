<script setup lang="ts">
import { useRoute } from 'vue-router'

/** 左侧固定导航：系统名、导航分组、当前页、数据版本 */
const props = defineProps<{ mode: 'mock' | 'real'; dataVersion?: string }>()

const route = useRoute()

const groups = [
  {
    label: '分析视图',
    items: [
      { name: 'regions', path: '/regions', label: '地区总览', icon: 'grid' },
      { name: 'jobs', path: '/jobs', label: '职位画像与差异', icon: 'bars' },
      { name: 'evidence', path: '/evidence', label: '条件比较与证据', icon: 'doc' },
    ],
  },
]
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar__brand">
      <span class="sidebar__mark" aria-hidden="true">
        <svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.4">
          <path d="M2 12.5h12M3.5 10V6M7 10V3.5M10.5 10V7M14 10V5" stroke-linecap="round" />
        </svg>
      </span>
      <div class="sidebar__titles">
        <strong class="sidebar__title">职位画像与城市就业</strong>
        <span class="sidebar__subtitle">可视分析系统</span>
      </div>
    </div>

    <nav class="sidebar__nav" aria-label="主导航">
      <div v-for="group in groups" :key="group.label" class="sidebar__group">
        <span class="sidebar__group-label">{{ group.label }}</span>
        <router-link
          v-for="item in group.items"
          :key="item.name"
          :to="item.path"
          class="sidebar__item"
          active-class="sidebar__item--active"
        >
          <span class="sidebar__icon" aria-hidden="true">
            <svg v-if="item.icon === 'grid'" viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.3">
              <path d="M3 3h4v4H3zM9 3h4v4H9zM3 9h4v4H3zM9 9h4v4H9z" />
            </svg>
            <svg v-else-if="item.icon === 'bars'" viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.3">
              <path d="M3 13V8M8 13V4M13 13V6" stroke-linecap="round" />
            </svg>
            <svg v-else viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.3">
              <path d="M4 2.5h5l3 3v8H4z" />
              <path d="M6.5 8h3M6.5 10.5h3" stroke-linecap="round" />
            </svg>
          </span>
          <span>{{ item.label }}</span>
        </router-link>
      </div>
    </nav>

    <div class="sidebar__foot">
      <div class="sidebar__foot-row">
        <span class="sidebar__foot-label">数据版本</span>
        <span class="sidebar__foot-value mono">{{ props.dataVersion ?? '—' }}</span>
      </div>
      <div class="sidebar__foot-row">
        <span class="sidebar__foot-label">数据来源</span>
        <span class="sidebar__foot-value">{{ props.mode === 'mock' ? '前端模拟' : '后端接口' }}</span>
      </div>
      <p class="sidebar__note">基于 ChinaVis 2024 虚拟招聘数据，地区与职位以代码展示。</p>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  width: var(--sidebar-width);
  height: 100vh;
  position: sticky;
  top: 0;
  background: var(--color-brand-strong);
  color: #dbe2e8;
  border-right: var(--border-width) solid var(--color-brand-strong);
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-4) var(--space-3);
  border-bottom: var(--border-width) solid rgba(255, 255, 255, 0.12);
}

.sidebar__mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border: var(--border-width) solid rgba(255, 255, 255, 0.28);
  border-radius: var(--radius-sm);
  color: #ffffff;
  flex: none;
}

.sidebar__titles {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.sidebar__title {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar__subtitle {
  font-size: var(--text-xs);
  color: rgba(219, 226, 232, 0.72);
}

.sidebar__nav {
  flex: 1;
  padding: var(--space-3) var(--space-2);
  overflow-y: auto;
}

.sidebar__group + .sidebar__group {
  margin-top: var(--space-4);
}

.sidebar__group-label {
  display: block;
  padding: 0 var(--space-2) var(--space-2);
  font-size: var(--text-xs);
  letter-spacing: 0.06em;
  color: rgba(219, 226, 232, 0.6);
}

.sidebar__item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  height: 34px;
  padding: 0 var(--space-2);
  border-radius: var(--radius-sm);
  border-left: 2px solid transparent;
  font-size: var(--text-base);
  color: #dbe2e8;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.sidebar__item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #ffffff;
}

.sidebar__item--active {
  background: var(--color-brand);
  border-left-color: #ffffff;
  color: #ffffff;
  font-weight: var(--weight-medium);
}

.sidebar__icon {
  display: inline-flex;
  align-items: center;
  color: inherit;
  opacity: 0.9;
}

.sidebar__foot {
  padding: var(--space-3) var(--space-4) var(--space-4);
  border-top: var(--border-width) solid rgba(255, 255, 255, 0.12);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar__foot-row {
  display: flex;
  justify-content: space-between;
  gap: var(--space-2);
  font-size: var(--text-xs);
}

.sidebar__foot-label {
  color: rgba(219, 226, 232, 0.62);
}

.sidebar__foot-value {
  color: #ffffff;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar__note {
  margin-top: var(--space-2);
  font-size: var(--text-xs);
  line-height: var(--line-normal);
  color: rgba(219, 226, 232, 0.58);
}
</style>
