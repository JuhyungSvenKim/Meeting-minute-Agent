<script setup lang="ts">
import { computed } from 'vue'
import type { MeetingStatus } from '@/types'

const props = defineProps<{ status: MeetingStatus }>()

const STATUS_MAP: Record<MeetingStatus, { label: string; classes: string; pulse?: boolean }> = {
  created:     { label: '생성됨',     classes: 'bg-slate-100 text-slate-700' },
  uploaded:    { label: '업로드됨',   classes: 'bg-slate-200 text-slate-800' },
  processing:  { label: '처리 중',    classes: 'bg-amber-100 text-amber-800', pulse: true },
  transcribed: { label: '변환 완료',  classes: 'bg-sky-100 text-sky-800' },
  summarized:  { label: '요약 완료',  classes: 'bg-emerald-100 text-emerald-800' },
  error:       { label: '오류',       classes: 'bg-rose-100 text-rose-800' },
}

const cfg = computed(() => STATUS_MAP[props.status] ?? STATUS_MAP.created)
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium"
    :class="[cfg.classes, cfg.pulse ? 'animate-pulseSoft' : '']"
  >
    <span
      v-if="cfg.pulse"
      class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"
    ></span>
    {{ cfg.label }}
  </span>
</template>
