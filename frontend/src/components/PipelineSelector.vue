<script setup lang="ts">
import type { PipelineType } from '@/types'

const props = defineProps<{ modelValue: PipelineType }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: PipelineType): void }>()

const OPTIONS: { value: PipelineType; title: string; desc: string; tag: string }[] = [
  {
    value: 'gemini',
    title: 'Gemini Only',
    desc: '빠르고 저렴. Gemini 3.1 Pro 단독으로 화자 분리 + 트랜스크립트.',
    tag: '권장',
  },
  {
    value: 'gemini_whisper',
    title: 'Gemini + Whisper',
    desc: 'Gemini의 화자 분리에 Whisper의 STT 텍스트로 보정. 더 정확.',
    tag: '고품질',
  },
]

function pick(v: PipelineType) {
  emit('update:modelValue', v)
}
</script>

<template>
  <div class="grid sm:grid-cols-2 gap-3">
    <button
      v-for="o in OPTIONS"
      :key="o.value"
      type="button"
      class="text-left p-4 rounded-xl border transition-all"
      :class="
        props.modelValue === o.value
          ? 'border-brand-500 bg-brand-50 ring-2 ring-brand-200'
          : 'border-slate-200 hover:border-slate-300 bg-white'
      "
      @click="pick(o.value)"
    >
      <div class="flex items-center justify-between">
        <div class="font-semibold text-slate-900">{{ o.title }}</div>
        <span
          class="text-[10px] px-1.5 py-0.5 rounded-full bg-brand-600 text-white font-medium"
          >{{ o.tag }}</span
        >
      </div>
      <p class="text-xs text-slate-600 mt-1.5">{{ o.desc }}</p>
    </button>
  </div>
</template>
