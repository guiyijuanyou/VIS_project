<script setup lang="ts">
import { computed, ref } from 'vue'
import type { EChartsOption } from 'echarts'
import type { JobProfileResponse } from '@/api/types'
import { useECharts } from '@/composables/useECharts'
import { axisStyle } from '@/charts/theme'
import { formatCount, formatNumber } from '@/utils/format'

/** C04：薪资箱线图 + 各经验代码下的中位数对照（样本不足处为 null，不画成 0） */
const props = defineProps<{ profile: JobProfileResponse }>()

const boxContainer = ref<HTMLElement | null>(null)
const expContainer = ref<HTMLElement | null>(null)

const boxOption = computed<EChartsOption>(() => {
  const salary = props.profile.salary
  if (!salary) return {}
  return {
    tooltip: {
      trigger: 'item',
      formatter: () =>
        [
          `职位：${props.profile.job}`,
          `P05 / P25 / P50 / P75 / P95：${salary.p05} / ${salary.p25} / ${salary.p50} / ${salary.p75} / ${salary.p95}`,
          `有效样本：${formatCount(salary.sampleCount)}（单位：${salary.unit}）`,
        ].join('<br/>'),
    },
    xAxis: { ...axisStyle(), type: 'category', data: [props.profile.job] },
    yAxis: { ...axisStyle(), type: 'value', name: '报价中点', nameGap: 18 },
    series: [
      {
        type: 'boxplot',
        data: [[salary.p05, salary.p25, salary.p50, salary.p75, salary.p95]],
        boxWidth: [28, 70],
        itemStyle: { borderColor: '#3b6dd8', color: '#eaf0fd' },
      },
    ],
  }
})

const expOption = computed<EChartsOption>(() => {
  const rows = props.profile.salaryByExperience.filter((row) => row.median !== null)
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = Array.isArray(params) ? params[0] : params
        const row = props.profile.salaryByExperience.find((entry) => entry.code === item?.name)
        if (!row) return ''
        return [`经验代码：${row.code}`, `中位数：${formatNumber(row.median)}（${props.profile.salary?.unit ?? ''}）`, `有效样本：${formatCount(row.sampleCount)}`].join('<br/>')
      },
    },
    xAxis: { ...axisStyle(), type: 'category', data: rows.map((row) => row.code) },
    yAxis: { ...axisStyle(), type: 'value', name: '中位数', nameGap: 18 },
    series: [
      {
        type: 'bar',
        data: rows.map((row) => ({ value: row.median, itemStyle: { color: row.sampleCount < 30 ? '#b3a01e' : '#3b6dd8' } })),
        barMaxWidth: 26,
        label: { show: rows.length <= 8, position: 'top', fontSize: 10, formatter: (params: any) => formatCount(props.profile.salaryByExperience[params.dataIndex]?.sampleCount) },
      },
    ],
  }
})

const insufficient = computed(() => props.profile.salaryByExperience.filter((row) => row.median !== null && row.sampleCount < 30).length)

useECharts(boxContainer, () => (props.profile.salary ? boxOption.value : null))
useECharts(expContainer, () => (props.profile.salaryByExperience.length ? expOption.value : null))
</script>

<template>
  <div class="salary-box">
    <div class="salary-box__grid">
      <div>
        <h4 class="salary-box__title">报价中点分布（P05～P95 箱线）</h4>
        <div v-if="profile.salary" ref="boxContainer" class="salary-box__canvas"></div>
        <p v-else class="empty-hint">该职位在当前条件下没有有效报价，薪资相关视图不展示，也不会用 0 代替。</p>
        <p v-if="profile.salary" class="card__hint">
          箱体为 P25～P75，横线为中位数，须为 P05～P95；有效样本 {{ formatCount(profile.salary.sampleCount) }}（单位：{{ profile.salary.unit }}）。
        </p>
      </div>
      <div>
        <h4 class="salary-box__title">按经验代码的报价中位数</h4>
        <div v-if="profile.salaryByExperience.length" ref="expContainer" class="salary-box__canvas"></div>
        <p v-else class="empty-hint">没有可用的经验维度报价样本。</p>
        <p class="card__hint">
          柱顶数字为有效样本数；样本低于 30 的柱子标为提示色并从主排名排除（展示阈值，非统计显著性）。当前不足样本的代码：{{ insufficient }} 个。
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.salary-box__grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }

.salary-box__title { font-size: 13px; margin-bottom: var(--space-2); color: var(--color-text-muted); }

.salary-box__canvas { width: 100%; height: 240px; }

@media (max-width: 900px) {
  .salary-box__grid { grid-template-columns: 1fr; }
}
</style>
