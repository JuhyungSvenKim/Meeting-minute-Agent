<script setup lang="ts">
import type { LLMProvider } from '@/types'

const props = defineProps<{ modelValue: LLMProvider }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: LLMProvider): void }>()

const PROVIDERS: { value: LLMProvider; label: string; sub: string }[] = [
  { value: 'gemini', label: 'Gemini', sub: '3.1 Pro' },
  { value: 'openai', label: 'OpenAI', sub: 'GPT-4o' },
  { value: 'anthropic', label: 'Claude', sub: 'Sonnet 4.6' },
]
</script>

<template>
  <div class="inline-flex bg-slate-100 rounded-lg p-1">
    <button
      v-for="p in PROVIDERS"
      :key="p.value"
      type="button"
      class="px-3 py-1.5 text-xs rounded-md transition-colors"
      :class="
        props.modelValue === p.value
          ? 'bg-white text-slate-900 shadow-sm font-semibold'
          : 'text-slate-600 hover:text-slate-900'
      "
      @click="emit('update:modelValue', p.value)"
    >
      <div>{{ p.label }}</div>
      <div class="text-[10px] opacity-70">{{ p.sub }}</div>
    </button>
  </div>
</template>
