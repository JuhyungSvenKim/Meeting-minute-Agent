import { defineStore } from 'pinia'
import { ref } from 'vue'
import { meetingsApi } from '@/services/api'
import type {
  LLMProvider,
  Meeting,
  ProcessStatus,
  Summary,
  Transcript,
} from '@/types'

export const useMeetingDetailStore = defineStore('meetingDetail', () => {
  const meeting = ref<Meeting | null>(null)
  const transcript = ref<Transcript | null>(null)
  const summary = ref<Summary | null>(null)
  const status = ref<ProcessStatus | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  let pollTimer: number | null = null

  async function loadMeeting(id: string) {
    loading.value = true
    error.value = null
    try {
      meeting.value = await meetingsApi.get(id)
      await Promise.allSettled([loadTranscript(id), loadSummary(id), refreshStatus(id)])
    } catch (e: any) {
      error.value = e?.message ?? 'Failed to load meeting'
    } finally {
      loading.value = false
    }
  }

  async function loadTranscript(id: string) {
    try {
      transcript.value = await meetingsApi.transcript(id)
    } catch {
      transcript.value = null
    }
  }

  async function loadSummary(id: string) {
    try {
      summary.value = await meetingsApi.latestSummary(id)
    } catch {
      summary.value = null
    }
  }

  async function refreshStatus(id: string) {
    try {
      status.value = await meetingsApi.status(id)
    } catch {
      status.value = null
    }
  }

  function startPolling(id: string, intervalMs = 2500) {
    stopPolling()
    pollTimer = window.setInterval(async () => {
      await refreshStatus(id)
      if (
        status.value &&
        (status.value.stage === 'completed' || status.value.stage === 'error')
      ) {
        stopPolling()
        meeting.value = await meetingsApi.get(id)
        await Promise.allSettled([loadTranscript(id), loadSummary(id)])
      }
    }, intervalMs)
  }

  function stopPolling() {
    if (pollTimer) {
      window.clearInterval(pollTimer)
      pollTimer = null
    }
  }

  async function renameSpeaker(id: string, label: string, name: string) {
    await meetingsApi.renameSpeaker(id, label, name)
    if (transcript.value) {
      transcript.value = {
        ...transcript.value,
        segments: transcript.value.segments.map((s) =>
          s.speaker_label === label ? { ...s, speaker_name: name } : s,
        ),
      }
    }
  }

  async function regenerateSummary(id: string, provider: LLMProvider) {
    summary.value = await meetingsApi.summarize(id, provider)
    meeting.value = await meetingsApi.get(id)
  }

  function $reset() {
    meeting.value = null
    transcript.value = null
    summary.value = null
    status.value = null
    error.value = null
    stopPolling()
  }

  return {
    meeting,
    transcript,
    summary,
    status,
    loading,
    error,
    loadMeeting,
    loadTranscript,
    loadSummary,
    refreshStatus,
    startPolling,
    stopPolling,
    renameSpeaker,
    regenerateSummary,
    $reset,
  }
})
