<script setup lang="ts">
import { computed } from 'vue'
import type { Transcript } from '@/types'
import SpeakerSegmentItem from './SpeakerSegment.vue'
import { speakerColor } from '@/utils/speakerColor'

const props = defineProps<{ transcript: Transcript | null }>()
const emit = defineEmits<{ (e: 'rename', label: string, name: string): void }>()

const speakers = computed(() => {
  const map = new Map<string, { name: string | null }>()
  for (const s of props.transcript?.segments ?? []) {
    if (!map.has(s.speaker_label)) map.set(s.speaker_label, { name: s.speaker_name })
  }
  return Array.from(map.entries()).map(([label, v]) => ({ label, name: v.name }))
})
</script>

<template>
  <div v-if="!transcript" class="text-sm text-slate-500 py-12 text-center">
    아직 트랜스크립트가 없습니다. 처리를 시작하면 자동으로 생성됩니다.
  </div>

  <div v-else>
    <div class="flex flex-wrap items-center gap-2 mb-4 pb-3 border-b border-slate-200">
      <span class="text-xs text-slate-500 mr-1">화자:</span>
      <span
        v-for="s in speakers"
        :key="s.label"
        class="inline-flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-full ring-1"
        :class="[speakerColor(s.label).bg, speakerColor(s.label).text, speakerColor(s.label).ring]"
      >
        <span :class="['w-1.5 h-1.5 rounded-full', speakerColor(s.label).dot]"></span>
        {{ s.name || s.label }}
      </span>
      <span class="ml-auto text-xs text-slate-500">
        provider: {{ transcript.provider }} · lang: {{ transcript.language ?? '?' }}
      </span>
    </div>

    <div class="divide-y divide-slate-100">
      <SpeakerSegmentItem
        v-for="seg in transcript.segments"
        :key="seg.id ?? `${seg.segment_order}-${seg.start_time}`"
        :segment="seg"
        @rename="(label, name) => emit('rename', label, name)"
      />
    </div>
  </div>
</template>
