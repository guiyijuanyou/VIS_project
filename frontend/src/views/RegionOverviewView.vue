<script setup lang="ts">
import { computed, watch } from 'vue'
import { api } from '@/api/endpoints'
import type { SimilarRegionsResponse } from '@/api/types'
import { useAsyncQuery } from '@/composables/useAsyncQuery'
import { useFilterStore } from '@/stores/filter'
import OverviewCards from '@/components/OverviewCards.vue'
import RegionScatter from '@/components/RegionScatter.vue'
import RegionCompare from '@/components/RegionCompare.vue'
import SimilarRegions from '@/components/SimilarRegions.vue'
import StateBlock from '@/components/StateBlock.vue'

/** 页签 1：地区总览（C03）—— 指标卡 + 散点 + 结构比较 + 相似地区 */
const store = useFilterStore()

const overviewQuery = useAsyncQuery((signal) => api.overview(store.filters, signal))
const regionsQuery = useAsyncQuery((signal) => api.regions(store.filters, signal))
const similarQuery = useAsyncQuery<SimilarRegionsResponse | null>((signal) => {
  const region = store.compareRegions[0]
  return region ? api.similarRegions(region, signal) : Promise.resolve(null)
})

watch(() => [store.queryKey, store.compareRegions[0] ?? ''] as const, () => {
  void overviewQuery.run()
  void regionsQuery.run()
  void similarQuery.run()
}, { immediate: true })

const regionRows = computed(() => regionsQuery.data.value?.items ?? [])
</script>

<template>
  <section class="card">
    <div class="card__header">
      <h2 class="card__title">总量与有效报价</h2>
      <span class="card__hint">记录数按发布量统计；有效报价样本单独计数，薪资不可用不计为 0。</span>
    </div>
    <StateBlock :status="overviewQuery.status.value" :error="overviewQuery.error.value">
      <OverviewCards v-if="overviewQuery.data.value" :overview="overviewQuery.data.value" />
    </StateBlock>
  </section>

  <section class="card">
    <div class="card__header">
      <h2 class="card__title">地区发布量 × 报价中位数</h2>
      <span class="card__hint">点宽表示记录数；地区是代码，不是坐标，本视图不是地图。</span>
    </div>
    <StateBlock
      :status="regionsQuery.status.value"
      :error="regionsQuery.error.value"
      :empty="regionRows.length === 0"
      empty-text="当前筛选条件下没有地区记录；请放宽条件或重置筛选。"
    >
      <RegionScatter :items="regionRows" :selected="store.compareRegions" @toggle="store.toggleCompareRegion" />
    </StateBlock>
  </section>

  <section class="card">
    <div class="card__header">
      <h2 class="card__title">地区结构比较（2～4 个）</h2>
      <span class="card__hint">行业占比与报价分布分开呈现，不混合成一个“综合得分”。</span>
    </div>
    <StateBlock :status="regionsQuery.status.value" :error="regionsQuery.error.value">
      <RegionCompare :items="regionRows" :selected="store.compareRegions" @remove="store.toggleCompareRegion" />
    </StateBlock>
  </section>

  <section class="card">
    <div class="card__header">
      <h2 class="card__title">相似地区</h2>
      <span class="card__hint">基于全局行业发布结构，不随筛选重算；相似 ≠ 地理接近。</span>
    </div>
    <StateBlock
      :status="similarQuery.status.value"
      :error="similarQuery.error.value"
      :empty="!similarQuery.data.value"
      empty-text="先在散点图中点选一个地区，查看与其行业发布结构最相似的 5 个地区。"
    >
      <SimilarRegions
        v-if="similarQuery.data.value"
        :result="similarQuery.data.value"
        @pick="store.toggleCompareRegion"
      />
    </StateBlock>
  </section>
</template>
