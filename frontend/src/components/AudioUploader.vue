<script setup lang="ts">
import { ref } from 'vue'
import { formatBytes } from '@/utils/format'

const props = defineProps<{
  uploading?: boolean
  progress?: number
  accept?: string
}>()

const emit = defineEmits<{ (e: 'select', file: File): void }>()

const dragOver = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const lastFile = ref<File | null>(null)

function trigger() {
  fileInput.value?.click()
}

function onChange(e: Event) {
  const target = e.target as HTMLInputElement
  const f = target.files?.[0]
  if (f) {
    lastFile.value = f
    emit('select', f)
  }
  target.value = ''
}

function onDrop(e: DragEvent) {
  dragOver.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f) {
    lastFile.value = f
    emit('select', f)
  }
}
</script>

<template>
  <div
    class="rounded-xl border-2 border-dashed transition-colors p-8 text-center cursor-pointer"
    :class="
      dragOver
        ? 'border-brand-500 bg-brand-50'
        : 'border-slate-300 bg-slate-50 hover:bg-slate-100'
    "
    @click="trigger"
    @dragenter.prevent="dragOver = true"
    @dragover.prevent="dragOver = true"
    @dragleave.prevent="dragOver = false"
    @drop.prevent="onDrop"
  >
    <input
      ref="fileInput"
      type="file"
      class="hidden"
      :accept="accept ?? 'audio/*,video/*'"
      @change="onChange"
    />

    <div class="flex flex-col items-center gap-2">
      <div
        class="w-12 h-12 rounded-full bg-brand-100 text-brand-600 grid place-items-center"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.8"
          stroke="currentColor"
          class="w-6 h-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M3 16.5V18a3 3 0 003 3h12a3 3 0 003-3v-1.5M16.5 12L12 7.5 7.5 12M12 7.5V18"
          />
        </svg>
      </div>
      <div class="font-medium text-slate-800">오디오 파일을 드래그하거나 클릭해서 업로드</div>
      <div class="text-xs text-slate-500">최대 500MB · audio/* 또는 video/*</div>

      <div v-if="lastFile" class="mt-2 text-xs text-slate-700">
        선택됨: <span class="font-medium">{{ lastFile.name }}</span>
        <span class="text-slate-500"> ({{ formatBytes(lastFile.size) }})</span>
      </div>

      <div v-if="props.uploading" class="w-full mt-3 max-w-xs">
        <div class="h-2 bg-slate-200 rounded-full overflow-hidden">
          <div
            class="h-full bg-brand-600 transition-all"
            :style="{ width: `${props.progress ?? 0}%` }"
          ></div>
        </div>
        <div class="text-xs text-slate-500 mt-1">업로드 중… {{ props.progress ?? 0 }}%</div>
      </div>
    </div>
  </div>
</template>
