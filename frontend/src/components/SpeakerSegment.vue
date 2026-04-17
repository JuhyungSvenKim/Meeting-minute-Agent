<script setup lang="ts">
import { computed } from 'vue'
import type { SpeakerSegment } from '@/types'
import SpeakerNameEditor from './SpeakerNameEditor.vue'
import { speakerColor } from '@/utils/speakerColor'
import { formatTimecode } from '@/utils/format'

const props = defineProps<{ segment: SpeakerSegment }>()
const emit = defineEmits<{ (e: 'rename', label: string, name: string): void }>()

const colors = computed(() => speakerColor(props.segment.speaker_label))
</script>

<template>
  <div class="flex gap-3 py-2.5 group">
    <div class="text-[11px] text-slate-400 font-mono w-12 pt-0.5 text-right shrink-0">
      {{ formatTimecode(segment.start_time) }}
    </div>
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2 mb-1">
        <SpeakerNameEditor
          :label="segment.speaker_label"
          :name="segment.speaker_name"
          :color-classes="colors"
          @save="(n) => emit('rename', segment.speaker_label, n)"
        />
        <span v-if="segment.gender_estimate" class="text-[10px] text-slate-400">
          · {{ segment.gender_estimate }}
        </span>
      </div>
      <p class="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">
        {{ segment.text }}
      </p>
    </div>
  </div>
</template>
