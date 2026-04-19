export type PipelineType = 'gemini' | 'gemini_whisper'
export type GeminiAudioModel =
  | 'gemini-3.0-flash'
  | 'gemini-3.0-pro'
  | 'gemini-3.1-flash-lite'
  | 'gemini-3.1-flash'
  | 'gemini-3.1-pro'

export const GEMINI_AUDIO_MODELS: {
  value: GeminiAudioModel
  label: string
  sub: string
  tag?: string
}[] = [
  { value: 'gemini-3.0-flash',      label: 'Gemini 3.0 Flash',      sub: '구세대 · 매우 빠름 · 저렴' },
  { value: 'gemini-3.0-pro',        label: 'Gemini 3.0 Pro',        sub: '구세대 · 품질 우선' },
  { value: 'gemini-3.1-flash-lite', label: 'Gemini 3.1 Flash Lite', sub: '최신 · 초경량 · 최저가' },
  { value: 'gemini-3.1-flash',      label: 'Gemini 3.1 Flash',      sub: '최신 · 균형', tag: '권장' },
  { value: 'gemini-3.1-pro',        label: 'Gemini 3.1 Pro',        sub: '최신 · 최고 품질 · 느림' },
]
export type LLMProvider = 'gemini' | 'openai' | 'anthropic'
export type ExportFormat = 'pdf' | 'md' | 'txt'
export type MeetingStatus =
  | 'created'
  | 'uploaded'
  | 'processing'
  | 'transcribed'
  | 'summarized'
  | 'error'
export type ProcessingStage =
  | 'queued'
  | 'downloading'
  | 'transcribing'
  | 'merging'
  | 'saving'
  | 'completed'
  | 'error'

export interface Meeting {
  id: string
  title: string
  meeting_date: string | null
  duration_seconds: number | null
  status: MeetingStatus
  pipeline_type: PipelineType | null
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface AudioFile {
  id: string
  meeting_id: string
  storage_path: string
  filename: string
  size: number
  mime_type: string
  created_at: string
}

export interface SpeakerSegment {
  id?: string
  transcript_id?: string
  speaker_label: string
  speaker_name: string | null
  start_time: number
  end_time: number
  text: string
  confidence: number | null
  gender_estimate: string | null
  segment_order: number
}

export interface Transcript {
  id: string
  meeting_id: string
  provider: string
  full_text: string | null
  language: string | null
  confidence_score: number | null
  raw_response: unknown
  created_at: string
  segments: SpeakerSegment[]
}

export interface ActionItem {
  title: string
  owner?: string | null
  due_date?: string | null
}

export interface SummaryContent {
  title?: string | null
  attendees: string[]
  summary: string
  key_points: string[]
  decisions: string[]
  action_items: ActionItem[]
}

export interface Summary {
  id: string
  meeting_id: string
  llm_provider: LLMProvider
  content: SummaryContent
  format_type: string
  created_at: string
}

export interface ProcessStatus {
  meeting_id: string
  status: MeetingStatus
  stage: ProcessingStage
  progress: number
  message: string | null
  error_message: string | null
}
