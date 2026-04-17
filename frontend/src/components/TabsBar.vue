<script setup lang="ts" generic="T extends string">
const props = defineProps<{
  modelValue: T
  tabs: { value: T; label: string }[]
}>()
const emit = defineEmits<{ (e: 'update:modelValue', v: T): void }>()
</script>

<template>
  <div class="border-b border-slate-200">
    <nav class="-mb-px flex gap-2">
      <button
        v-for="t in tabs"
        :key="t.value"
        type="button"
        class="px-4 py-2.5 text-sm font-medium border-b-2 transition-colors"
        :class="
          props.modelValue === t.value
            ? 'border-brand-600 text-brand-700'
            : 'border-transparent text-slate-500 hover:text-slate-800'
        "
        @click="emit('update:modelValue', t.value)"
      >
        {{ t.label }}
      </button>
    </nav>
  </div>
</template>
