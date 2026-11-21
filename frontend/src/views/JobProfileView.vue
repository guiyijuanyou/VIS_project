<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '@/api/endpoints'
import { useAsyncQuery } from '@/composables/useAsyncQuery'
import { useFilterStore } from '@/stores/filter'
import { formatCount } from '@/utils/format'
import PageHeader from '@/components/PageHeader.vue'
import ChartContainer from '@/components/ChartContainer.vue'
import SearchInput from '@/components/SearchInput.vue'
import Tag from '@/components/Tag.vue'
import JobProfile from '@/components/JobProfile.vue'
import SalaryBox from '@/components/SalaryBox.vue'
import DistanceMatrix from '@/components/DistanceMatrix.vue'
import StateBlock from '@/components/StateBlock.vue'

/** 页签 2：职位画像与差异（C04）—— 搜索职位、画像、箱线图、差异矩阵 */
const store = useFilterStore()
const keyword = ref('')
const options = ref<{ code: string; recordCount: number }[]>([])
const optionError = ref('')

async function loadOptions() {
  try {
    const response = await api.jobOptions(keyword.value, 1, 20)
    options.value = response.items
    optionError.value = ''
    if (!store.focusJob && response.items.length) store.setFocusJob(response.items[0].code)
  } catch (caught) {
    optionError.value = caught instanceof Error ? caught.message : String(caught)
  }
}

onMounted(loadOptions)

const profileQuery = useAsyncQuery((signal) => {
  if (!store.focusJob) return Promise.resolve(null)
  return api.jobProfile(store.filters, store.focusJob, signal)
})

const distanceQuery = useAsyncQuery((signal) => {
  if (store.compareJobs.length < 2) return Promise.resolve(null)
  return api.jobDistance(store.filters, store.compareJobs, signal)
})

watch(() => [store.queryKey, store.focusJob] as const, () => { void profileQuery.run() }, { immediate: true })
watch(() => [store.queryKey, store.compareJobs.join(',')] as const, () => { void distanceQuery.run() }, { immediate: true })

const profile = computed(() => profileQuery.data.value)
const distanceData = computed(() => distanceQuery.data.value)

function selectJob(code: string) {
  const alreadyCompared = store.compareJobs.includes(code)
  // 再次点击当前职位 = 取消比较；否则设为焦点并确保进入比较集合
  if (store.focusJob === code && alreadyCompared) {
    store.toggleCompareJob(code)
    return
  }
  store.setFocusJob(code)
  if (!store.compareJobs.includes(code)) store.toggleCompareJob(code)
}
</script>

<template>
  <PageHeader
    title="职位画像与差异度"
    subtitle="比较职位在行业、学历、经验结构与报价上的差异，并解释差异来源。职位为 job_title 代码，不是招聘记录 ID。"
  >
    <template #actions>
      <Tag :tone="store.compareJobs.length >= 2 ? 'brand' : 'neutral'">比较对象 {{ store.compareJobs.length }} / 4</Tag>
    </template>
  </PageHeader>

  <ChartContainer title="选择职位" hint="默认展示记录量较高的职位，其余可搜索；再次点击当前职位可移出比较。">
    <template #meta>
      <span v-if="optionError" class="picker__error">{{ optionError }}</span>
    </template>
    <div class="picker">
      <SearchInput
        v-model="keyword"
        placeholder="输入职位代码关键字后回车"
        button-label="搜索"
        width="320px"
        @submit="loadOptions"
      />
      <span class="picker__scale">已选：{{ store.compareJobs.join('、') || '未选择' }}</span>
    </div>
    <div class="picker__list">
      <Tag
        v-for="option in options"
        :key="option.code"
        :tone="store.focusJob === option.code ? 'brand' : 'neutral'"
        :title="`${option.code}：${formatCount(option.recordCount)} 条`"
      >
        <button class="picker__option" type="button" @click="selectJob(option.code)">
          {{ option.code }} · {{ formatCount(option.recordCount) }}
        </button>
      </Tag>
      <span v-if="options.length === 0" class="picker__empty">没有匹配的职位代码。</span>
    </div>
  </ChartContainer>

  <ChartContainer title="职位画像" hint="行业、学历、经验三类占比同一分母，并显示样本数。">
    <StateBlock
      :status="profileQuery.status.value"
      :error="profileQuery.error.value"
      :empty="!profile"
      empty-text="请先在上方选择一个职位代码。"
    >
      <JobProfile v-if="profile" :profile="profile" />
    </StateBlock>
  </ChartContainer>

  <ChartContainer title="薪资分布" hint="无有效报价时显示状态，不显示 0。">
    <StateBlock :status="profileQuery.status.value" :error="profileQuery.error.value" :empty="!profile">
      <SalaryBox v-if="profile" :profile="profile" />
    </StateBlock>
  </ChartContainer>

  <ChartContainer title="职位差异度矩阵" hint="至少选择 2 个职位；点击单元格查看各维贡献与公式说明。">
    <StateBlock
      :status="distanceQuery.status.value"
      :error="distanceQuery.error.value"
      :empty="!distanceData"
      empty-text="再选择 1 个以上职位即可比较差异度。"
    >
      <DistanceMatrix v-if="distanceData" :data="distanceData" />
    </StateBlock>
  </ChartContainer>
</template>

<style scoped>
.picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.picker__scale {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.picker__error {
  font-size: var(--text-xs);
  color: var(--color-negative);
}

.picker__list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: var(--border-width) solid var(--color-border);
}

.picker__option {
  border: none;
  background: transparent;
  padding: 0;
  font-size: inherit;
  color: inherit;
  font-variant-numeric: tabular-nums;
}

.picker__empty {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}
</style>
