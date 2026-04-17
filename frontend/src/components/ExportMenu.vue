<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { meetingsApi } from '@/services/api'
import type { ExportFormat } from '@/types'

const props = defineProps<{ meetingId: string; disabled?: boolean }>()

const open = ref(false)
const root = ref<HTMLDivElement | null>(null)

const FORMATS: { value: ExportFormat; label: string; desc: string }[] = [
  { value: 'pdf', label: 'PDF',      desc: '회의록 PDF' },
  { value: 'md',  label: 'Markdown', desc: '.md 마크다운' },
  { value: 'txt', label: 'Text',     desc: '.txt 일반 텍스트' },
]

function toggle() {
  if (!props.disabled) open.value = !open.value
}

function go(fmt: ExportFormat) {
  window.open(meetingsApi.exportUrl(props.meetingId, fmt), '_blank')
  open.value = false
}

function handleClick(e: MouseEvent) {
  if (root.value && !root.value.contains(e.target as Node)) open.value = false
}

onMounted(() => document.addEventListener('mousedown', handleClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', handleClick))
</script>

<template>
  <div ref="root" class="relative inline-block">
    <button class="btn-secondary" :disabled="disabled" @click="toggle">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="2"
        stroke="currentColor"
        class="w-4 h-4"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5 7.5 12M12 16.5V3"
        />
      </svg>
      Export
    </button>

    <div
      v-if="open"
      class="absolute right-0 mt-2 w-56 bg-white border border-slate-200 rounded-xl shadow-lg z-20 overflow-hidden"
    >
      <button
        v-for="f in FORMATS"
        :key="f.value"
        class="w-full text-left px-4 py-2.5 hover:bg-slate-50 flex items-center justify-between"
        @click="go(f.value)"
      >
        <div>
          <div class="text-sm font-medium text-slate-900">{{ f.label }}</div>
          <div class="text-xs text-slate-500">{{ f.desc }}</div>
        </div>
        <span class="text-xs text-brand-600">↓</span>
      </button>
    </div>
  </div>
</template>
