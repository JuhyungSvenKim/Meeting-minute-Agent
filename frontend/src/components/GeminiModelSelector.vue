<script setup lang="ts">
import type { GeminiAudioModel } from '@/types'
import { GEMINI_AUDIO_MODELS } from '@/types'

const props = defineProps<{ modelValue: GeminiAudioModel }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: GeminiAudioModel): void }>()
</script>

<template>
  <div class="grid sm:grid-cols-2 lg:grid-cols-5 gap-2">
    <button
      v-for="m in GEMINI_AUDIO_MODELS"
      :key="m.value"
      type="button"
      class="text-left p-3 rounded-lg border transition-all relative"
      :class="
        props.modelValue === m.value
          ? 'border-brand-500 bg-brand-50 ring-2 ring-brand-200'
          : 'border-slate-200 hover:border-slate-300 bg-white'
      "
      @click="emit('update:modelValue', m.value)"
    >
      <span
        v-if="m.tag"
        class="absolute -top-1.5 -right-1.5 text-[9px] px-1.5 py-0.5 rounded-full bg-brand-600 text-white font-medium"
        >{{ m.tag }}</span
      >
      <div class="text-xs font-semibold text-slate-900 leading-tight">
        {{ m.label }}
      </div>
      <p class="text-[11px] text-slate-500 mt-1 leading-snug">{{ m.sub }}</p>
    </button>
  </div>
</template>
