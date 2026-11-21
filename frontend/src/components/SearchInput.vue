<script setup lang="ts">
/** 搜索输入：受控 v-model + 回车/按钮提交 */
const props = withDefaults(defineProps<{ modelValue: string; placeholder?: string; buttonLabel?: string; width?: string }>(), {
  placeholder: '搜索…',
  buttonLabel: '搜索',
  width: '280px',
})
const emit = defineEmits<{ (e: 'update:modelValue', value: string): void; (e: 'submit'): void }>()
</script>

<template>
  <div class="search" :style="{ width: props.width }">
    <input
      class="search__input field"
      type="search"
      :value="props.modelValue"
      :placeholder="props.placeholder"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      @keyup.enter="emit('submit')"
    />
    <button class="btn" type="button" @click="emit('submit')">{{ props.buttonLabel }}</button>
  </div>
</template>

<style scoped>
.search {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
}

.search__input {
  flex: 1;
  min-width: 0;
}
</style>
