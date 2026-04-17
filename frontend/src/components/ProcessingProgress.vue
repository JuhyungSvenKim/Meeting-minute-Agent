<script setup lang="ts">
import { computed } from 'vue'
import type { ProcessStatus, ProcessingStage } from '@/types'

const props = defineProps<{ status: ProcessStatus | null }>()

const STAGES: { key: ProcessingStage; label: string }[] = [
  { key: 'downloading', label: '다운로드' },
  { key: 'transcribing', label: '트랜스크립션' },
  { key: 'merging', label: '병합' },
  { key: 'saving', label: '저장' },
  { key: 'completed', label: '완료' },
]

const stageOrder = computed(() => STAGES.findIndex((s) => s.key === props.status?.stage))

function stageState(idx: number): 'done' | 'active' | 'pending' {
  if (props.status?.stage === 'error') return idx === 0 ? 'active' : 'pending'
  const cur = stageOrder.value
  if (cur < 0) return 'pending'
  if (idx < cur) return 'done'
  if (idx === cur) return 'active'
  return 'pending'
}
</script>

<template>
  <div v-if="status" class="card p-5">
    <div class="flex items-center justify-between mb-3">
      <div>
        <div class="text-sm font-semibold text-slate-800">처리 진행</div>
        <div class="text-xs text-slate-500">{{ status.message ?? status.stage }}</div>
      </div>
      <div class="text-sm font-medium text-brand-700">{{ status.progress }}%</div>
    </div>

    <div class="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
      <div
        class="h-full transition-all"
        :class="status.stage === 'error' ? 'bg-rose-500' : 'bg-brand-600'"
        :style="{ width: `${status.progress}%` }"
      ></div>
    </div>

    <ol class="mt-4 grid grid-cols-5 gap-2 text-[11px]">
      <li
        v-for="(s, i) in STAGES"
        :key="s.key"
        class="flex flex-col items-center gap-1"
      >
        <span
          class="w-6 h-6 rounded-full grid place-items-center font-medium"
          :class="{
            'bg-emerald-500 text-white': stageState(i) === 'done',
            'bg-brand-600 text-white animate-pulse': stageState(i) === 'active',
            'bg-slate-200 text-slate-500': stageState(i) === 'pending',
          }"
        >
          {{ i + 1 }}
        </span>
        <span
          class="text-center"
          :class="
            stageState(i) === 'pending'
              ? 'text-slate-400'
              : 'text-slate-700 font-medium'
          "
          >{{ s.label }}</span
        >
      </li>
    </ol>

    <p v-if="status.error_message" class="mt-3 text-xs text-rose-600">
      ⚠ {{ status.error_message }}
    </p>
  </div>
</template>
