<script setup lang="ts">
import type { Summary } from '@/types'

defineProps<{ summary: Summary | null }>()
</script>

<template>
  <div v-if="!summary" class="text-sm text-slate-500 py-12 text-center">
    아직 회의록 요약이 없습니다. 위에서 LLM을 선택해 생성해 주세요.
  </div>

  <div v-else class="space-y-6">
    <header>
      <h2 class="text-xl font-semibold text-slate-900">
        {{ summary.content.title || '회의록' }}
      </h2>
      <div class="text-xs text-slate-500 mt-1">
        생성: {{ summary.llm_provider }} · {{ new Date(summary.created_at).toLocaleString() }}
      </div>
    </header>

    <section v-if="summary.content.attendees?.length">
      <h3 class="text-sm font-semibold text-slate-700 mb-2">참석자</h3>
      <div class="flex flex-wrap gap-1.5">
        <span
          v-for="a in summary.content.attendees"
          :key="a"
          class="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-700"
          >{{ a }}</span
        >
      </div>
    </section>

    <section v-if="summary.content.summary">
      <h3 class="text-sm font-semibold text-slate-700 mb-2">개요</h3>
      <p class="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">
        {{ summary.content.summary }}
      </p>
    </section>

    <section v-if="summary.content.key_points?.length">
      <h3 class="text-sm font-semibold text-slate-700 mb-2">주요 논점</h3>
      <ul class="list-disc pl-5 space-y-1 text-sm text-slate-800">
        <li v-for="(k, i) in summary.content.key_points" :key="i">{{ k }}</li>
      </ul>
    </section>

    <section v-if="summary.content.decisions?.length">
      <h3 class="text-sm font-semibold text-slate-700 mb-2">결정 사항</h3>
      <ul class="list-disc pl-5 space-y-1 text-sm text-slate-800">
        <li v-for="(d, i) in summary.content.decisions" :key="i">{{ d }}</li>
      </ul>
    </section>

    <section v-if="summary.content.action_items?.length">
      <h3 class="text-sm font-semibold text-slate-700 mb-2">액션 아이템</h3>
      <ul class="space-y-2">
        <li
          v-for="(a, i) in summary.content.action_items"
          :key="i"
          class="p-3 rounded-lg bg-slate-50 border border-slate-200"
        >
          <div class="text-sm font-medium text-slate-900">{{ a.title }}</div>
          <div class="text-xs text-slate-500 mt-0.5">
            <span v-if="a.owner">담당: {{ a.owner }}</span>
            <span v-if="a.owner && a.due_date"> · </span>
            <span v-if="a.due_date">기한: {{ a.due_date }}</span>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>
