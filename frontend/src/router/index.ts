import { createRouter, createWebHashHistory } from 'vue-router'
import RegionOverviewView from '@/views/RegionOverviewView.vue'
import JobProfileView from '@/views/JobProfileView.vue'
import EvidenceView from '@/views/EvidenceView.vue'

// 三个页签共用同一套筛选状态（见 stores/filter.ts）。
// 用 hash 历史，静态托管（file:// 或任意子路径）也能直接打开。
const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/regions' },
    { path: '/regions', name: 'regions', component: RegionOverviewView, meta: { title: '地区总览' } },
    { path: '/jobs', name: 'jobs', component: JobProfileView, meta: { title: '职位画像与差异' } },
    { path: '/evidence', name: 'evidence', component: EvidenceView, meta: { title: '条件比较与证据' } },
  ],
})

export default router
