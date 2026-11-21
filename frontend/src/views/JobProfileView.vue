<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '@/api/endpoints'
import { useAsyncQuery } from '@/composables/useAsyncQuery'
import { useFilterStore } from '@/stores/filter'
import { formatCount } from '@/utils/format'
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
  <section class="card">
    <div class="card__header">
      <h2 class="card__title">选择职位</h2>
      <span class="card__hint">职位是代码（job_title 类别），不是招聘记录 ID；不做技能或适岗推荐。</span>
    </div>
    <div class="job-picker">
      <input v-model="keyword" class="job-picker__input" type="search" placeholder="输入职位代码关键字后回车" @keyup.enter="loadOptions" />
      <button class="btn" type="button" @click="loadOptions">搜索</button>
      <span v-if="optionError" class="muted">{{ optionError }}</span>
    </div>
    <div class="job-picker__list">
      <button
        v-for="option in options"
        :key="option.code"
        type="button"
        class="chip"
        :class="{ 'chip--active': store.focusJob === option.code }"
        :title="`${option.code}：${formatCount(option.recordCount)} 条`"
        @click="selectJob(option.code)"
      >
        {{ option.code }} · {{ formatCount(option.recordCount) }}
      </button>
      <span v-if="options.length === 0" class="muted">没有匹配的职位代码。</span>
    </div>
    <p class="card__hint">
      已选比较对象（{{ store.compareJobs.length }}/4）：{{ store.compareJobs.join('、') || '未选择' }}。默认展示记录量较高的职位，其余可搜索。
    </p>
  </section>

  <section class="card">
    <div class="card__header">
      <h2 class="card__title">职位画像</h2>
      <span class="card__hint">行业、学历、经验三类占比同一分母，并显示样本数。</span>
    </div>
    <StateBlock
      :status="profileQuery.status.value"
      :error="profileQuery.error.value"
      :empty="!profile"
      empty-text="请先在上方选择一个职位代码。"
    >
      <JobProfile v-if="profile" :profile="profile" />
    </StateBlock>
  </section>

  <section class="card">
    <div class="card__header">
      <h2 class="card__title">薪资分布</h2>
      <span class="card__hint">无有效报价时显示状态，不显示 0。</span>
    </div>
    <StateBlock :status="profileQuery.status.value" :error="profileQuery.error.value" :empty="!profile">
      <SalaryBox v-if="profile" :profile="profile" />
    </StateBlock>
  </section>

  <section class="card">
    <div class="card__header">
      <h2 class="card__title">职位差异度矩阵</h2>
      <span class="card__hint">至少选择 2 个职位；点击单元格查看各维贡献。</span>
    </div>
    <StateBlock
      :status="distanceQuery.status.value"
      :error="distanceQuery.error.value"
      :empty="!distanceData"
      empty-text="再选择 1 个以上职位即可比较差异度。"
    >
      <DistanceMatrix v-if="distanceData" :data="distanceData" />
    </StateBlock>
  </section>
</template>

<style scoped>
.job-picker { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-2); }

.job-picker__input {
  flex: 1;
  min-width: 160px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 6px 10px;
  font-family: inherit;
  font-size: 13px;
}

.job-picker__list { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: var(--space-2); }
</style>
