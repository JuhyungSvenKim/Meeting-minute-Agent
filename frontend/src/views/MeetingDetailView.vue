<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMeetingDetailStore } from '@/stores/meetingDetail'
import StatusBadge from '@/components/StatusBadge.vue'
import ProcessingProgress from '@/components/ProcessingProgress.vue'
import TranscriptView from '@/components/TranscriptView.vue'
import SummaryView from '@/components/SummaryView.vue'
import LLMProviderSelector from '@/components/LLMProviderSelector.vue'
import ExportMenu from '@/components/ExportMenu.vue'
import TabsBar from '@/components/TabsBar.vue'
import { formatDateTime } from '@/utils/format'
import type { LLMProvider } from '@/types'

const route = useRoute()
const router = useRouter()
const store = useMeetingDetailStore()

const id = computed(() => String(route.params.id))
type Tab = 'transcript' | 'summary'
const tab = ref<Tab>('transcript')
const llm = ref<LLMProvider>('gemini')
const summarizing = ref(false)

onMounted(async () => {
  await store.loadMeeting(id.value)
  if (store.meeting?.status === 'processing') store.startPolling(id.value)
  if (store.summary) tab.value = 'summary'
})

watch(
  () => store.meeting?.status,
  (s) => {
    if (s === 'processing') store.startPolling(id.value)
    if (s === 'summarized' || s === 'transcribed' || s === 'error') store.stopPolling()
  },
)

onBeforeUnmount(() => store.$reset())

async function rename(label: string, name: string) {
  await store.renameSpeaker(id.value, label, name)
}

async function regenerate() {
  summarizing.value = true
  try {
    await store.regenerateSummary(id.value, llm.value)
    tab.value = 'summary'
  } finally {
    summarizing.value = false
  }
}
</script>

<template>
  <section v-if="store.meeting">
    <div class="flex flex-wrap items-start justify-between gap-3 mb-6">
      <div class="min-w-0">
        <button class="text-xs text-slate-500 hover:text-slate-800 mb-2" @click="router.push('/')">
          ← 회의 목록
        </button>
        <h1 class="text-2xl font-bold tracking-tight truncate">{{ store.meeting.title }}</h1>
        <div class="text-xs text-slate-500 mt-1 flex flex-wrap items-center gap-2">
          <StatusBadge :status="store.meeting.status" />
          <span>· {{ formatDateTime(store.meeting.meeting_date || store.meeting.created_at) }}</span>
          <span v-if="store.meeting.pipeline_type">· 파이프라인: {{ store.meeting.pipeline_type }}</span>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <ExportMenu :meeting-id="id" :disabled="!store.summary" />
      </div>
    </div>

    <ProcessingProgress
      v-if="store.meeting.status === 'processing' || store.status?.stage === 'error'"
      :status="store.status"
      class="mb-5"
    />

    <div class="card p-6">
      <TabsBar
        v-model="tab"
        :tabs="[
          { value: 'transcript', label: '트랜스크립트' },
          { value: 'summary', label: '회의록 요약' },
        ]"
      />

      <div v-if="tab === 'transcript'" class="pt-5">
        <TranscriptView :transcript="store.transcript" @rename="rename" />
      </div>

      <div v-else class="pt-5 space-y-5">
        <div class="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-200">
          <div>
            <div class="text-sm font-semibold text-slate-800">LLM 제공자</div>
            <div class="text-xs text-slate-500">제공자를 선택하고 "다시 생성"으로 요약을 새로 만들 수 있습니다.</div>
          </div>
          <div class="flex items-center gap-2">
            <LLMProviderSelector v-model="llm" />
            <button class="btn-primary" :disabled="summarizing || !store.transcript" @click="regenerate">
              {{ summarizing ? '생성 중…' : store.summary ? '다시 생성' : '요약 생성' }}
            </button>
          </div>
        </div>

        <SummaryView :summary="store.summary" />
      </div>
    </div>
  </section>

  <section v-else-if="store.loading" class="text-sm text-slate-500">로딩 중…</section>
  <section v-else class="text-sm text-rose-600">회의를 찾을 수 없습니다.</section>
</template>
