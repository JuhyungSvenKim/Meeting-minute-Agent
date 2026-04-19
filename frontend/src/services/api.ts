import axios from 'axios'
import type {
  AudioFile,
  ExportFormat,
  GeminiAudioModel,
  LLMProvider,
  Meeting,
  PipelineType,
  ProcessStatus,
  Summary,
  Transcript,
} from '@/types'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const http = axios.create({
  baseURL,
  timeout: 60_000,
})

export const meetingsApi = {
  list: () => http.get<Meeting[]>('/api/meetings').then((r) => r.data),
  get: (id: string) => http.get<Meeting>(`/api/meetings/${id}`).then((r) => r.data),
  create: (payload: { title: string; meeting_date?: string | null }) =>
    http.post<Meeting>('/api/meetings', payload).then((r) => r.data),
  update: (id: string, payload: Partial<Meeting>) =>
    http.patch<Meeting>(`/api/meetings/${id}`, payload).then((r) => r.data),
  remove: (id: string) => http.delete(`/api/meetings/${id}`).then((r) => r.data),

  uploadAudio: (
    id: string,
    file: File,
    opts?: { compress?: boolean; onProgress?: (pct: number) => void },
  ) => {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('compress', String(opts?.compress ?? true))
    return http
      .post<AudioFile>(`/api/meetings/${id}/audio`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 0,
        onUploadProgress: (e) => {
          if (e.total && opts?.onProgress) {
            opts.onProgress(Math.round((e.loaded / e.total) * 100))
          }
        },
      })
      .then((r) => r.data)
  },

  startProcess: (
    id: string,
    pipeline_type: PipelineType,
    opts?: { gemini_model?: GeminiAudioModel; compress_audio?: boolean },
  ) =>
    http
      .post(`/api/meetings/${id}/process`, {
        pipeline_type,
        gemini_model: opts?.gemini_model,
        compress_audio: opts?.compress_audio ?? true,
      })
      .then((r) => r.data),

  status: (id: string) =>
    http.get<ProcessStatus>(`/api/meetings/${id}/process/status`).then((r) => r.data),

  transcript: (id: string) =>
    http.get<Transcript>(`/api/meetings/${id}/transcript`).then((r) => r.data),

  renameSpeaker: (id: string, label: string, speaker_name: string) =>
    http
      .patch(`/api/meetings/${id}/speakers/${encodeURIComponent(label)}`, {
        speaker_name,
      })
      .then((r) => r.data),

  summarize: (id: string, llm_provider: LLMProvider, format_type = 'standard') =>
    http
      .post<Summary>(`/api/meetings/${id}/summarize`, { llm_provider, format_type })
      .then((r) => r.data),

  latestSummary: (id: string) =>
    http.get<Summary>(`/api/meetings/${id}/summary`).then((r) => r.data),

  exportUrl: (id: string, fmt: ExportFormat) =>
    `${baseURL}/api/meetings/${id}/export/${fmt}`,
}
