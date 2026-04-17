<script setup lang="ts">
import { RouterLink } from 'vue-router'
import StatusBadge from './StatusBadge.vue'
import type { Meeting } from '@/types'
import { formatDateTime, formatDuration } from '@/utils/format'

defineProps<{ meeting: Meeting }>()
defineEmits<{ (e: 'delete', id: string): void }>()
</script>

<template>
  <div class="card p-5 flex flex-col gap-3 hover:shadow-md transition-shadow">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <RouterLink
          :to="`/meetings/${meeting.id}`"
          class="font-semibold text-slate-900 hover:text-brand-700 truncate block"
        >
          {{ meeting.title }}
        </RouterLink>
        <div class="text-xs text-slate-500 mt-0.5">
          {{ formatDateTime(meeting.meeting_date || meeting.created_at) }}
          <span v-if="meeting.duration_seconds"> · {{ formatDuration(meeting.duration_seconds) }}</span>
        </div>
      </div>
      <StatusBadge :status="meeting.status" />
    </div>

    <p v-if="meeting.error_message" class="text-xs text-rose-600 line-clamp-2">
      {{ meeting.error_message }}
    </p>

    <div class="flex items-center justify-between mt-1">
      <span class="text-xs text-slate-500">
        파이프라인: <span class="font-medium text-slate-700">{{ meeting.pipeline_type ?? '-' }}</span>
      </span>
      <div class="flex items-center gap-1">
        <RouterLink :to="`/meetings/${meeting.id}`" class="btn-ghost text-xs px-2 py-1">상세</RouterLink>
        <button
          class="btn-ghost text-xs px-2 py-1 text-rose-600 hover:bg-rose-50"
          @click="$emit('delete', meeting.id)"
        >
          삭제
        </button>
      </div>
    </div>
  </div>
</template>
