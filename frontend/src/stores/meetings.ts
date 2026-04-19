import { defineStore } from 'pinia'
import { ref } from 'vue'
import { meetingsApi } from '@/services/api'
import type { GeminiAudioModel, Meeting, PipelineType } from '@/types'

export const useMeetingsStore = defineStore('meetings', () => {
  const meetings = ref<Meeting[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      meetings.value = await meetingsApi.list()
    } catch (e: any) {
      error.value = e?.message ?? 'Failed to load meetings'
    } finally {
      loading.value = false
    }
  }

  async function create(payload: { title: string; meeting_date?: string | null }) {
    const created = await meetingsApi.create(payload)
    meetings.value = [created, ...meetings.value]
    return created
  }

  async function remove(id: string) {
    await meetingsApi.remove(id)
    meetings.value = meetings.value.filter((m) => m.id !== id)
  }

  function patchLocal(id: string, patch: Partial<Meeting>) {
    meetings.value = meetings.value.map((m) =>
      m.id === id ? { ...m, ...patch } : m,
    )
  }

  async function startProcess(
    id: string,
    pipeline: PipelineType,
    opts?: { gemini_model?: GeminiAudioModel; compress_audio?: boolean },
  ) {
    await meetingsApi.startProcess(id, pipeline, opts)
    patchLocal(id, { status: 'processing', pipeline_type: pipeline })
  }

  return { meetings, loading, error, fetchAll, create, remove, patchLocal, startProcess }
})
