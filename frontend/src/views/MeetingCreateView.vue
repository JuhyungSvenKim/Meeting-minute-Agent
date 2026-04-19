<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { meetingsApi } from '@/services/api'
import { useMeetingsStore } from '@/stores/meetings'
import AudioUploader from '@/components/AudioUploader.vue'
import PipelineSelector from '@/components/PipelineSelector.vue'
import GeminiModelSelector from '@/components/GeminiModelSelector.vue'
import type { GeminiAudioModel, PipelineType } from '@/types'
import { formatBytes } from '@/utils/format'

const router = useRouter()
const store = useMeetingsStore()

const title = ref('')
const meetingDate = ref('')
const pipeline = ref<PipelineType>('gemini')
const geminiModel = ref<GeminiAudioModel>('gemini-3.1-flash')
const compressAudio = ref(true)

const file = ref<File | null>(null)
const uploading = ref(false)
const progress = ref(0)
const submitting = ref(false)
const errorMsg = ref<string | null>(null)

const fileSizeMb = computed(() =>
  file.value ? file.value.size / 1024 / 1024 : 0,
)
const isLargeFile = computed(() => fileSizeMb.value >= 25)

async function submit() {
  if (!title.value.trim()) {
    errorMsg.value = '회의 제목을 입력해 주세요.'
    return
  }
  if (!file.value) {
    errorMsg.value = '오디오 파일을 선택해 주세요.'
    return
  }
  if (pipeline.value === 'gemini_whisper' && isLargeFile.value) {
    errorMsg.value =
      `Whisper는 요청당 25 MB까지만 지원합니다. ${formatBytes(file.value.size)} 파일은 ` +
      `"Gemini Only" 파이프라인을 사용하거나, 자동 압축을 켜주세요.`
    return
  }
  errorMsg.value = null
  submitting.value = true
  try {
    const created = await store.create({
      title: title.value.trim(),
      meeting_date: meetingDate.value
        ? new Date(meetingDate.value).toISOString()
        : null,
    })
    uploading.value = true
    progress.value = 0
    await meetingsApi.uploadAudio(created.id, file.value, {
      compress: compressAudio.value,
      onProgress: (p) => (progress.value = p),
    })
    uploading.value = false

    await store.startProcess(created.id, pipeline.value, {
      gemini_model: geminiModel.value,
      compress_audio: compressAudio.value,
    })
    router.push(`/meetings/${created.id}`)
  } catch (e: any) {
    errorMsg.value =
      e?.response?.data?.detail ?? e?.message ?? '회의 생성 중 오류가 발생했습니다.'
  } finally {
    submitting.value = false
    uploading.value = false
  }
}
</script>

<template>
  <section class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold tracking-tight mb-1">새 회의</h1>
    <p class="text-sm text-slate-500 mb-6">
      오디오를 업로드하면 자동으로 화자 분리 트랜스크립트와 회의록 요약이 생성됩니다.
    </p>

    <div class="card p-6 space-y-5">
      <div>
        <label class="label">회의 제목</label>
        <input v-model="title" class="input" placeholder="예) 4월 정기 회의" />
      </div>
      <div>
        <label class="label">회의 일시 (선택)</label>
        <input v-model="meetingDate" type="datetime-local" class="input" />
      </div>

      <div>
        <label class="label">파이프라인</label>
        <PipelineSelector v-model="pipeline" />
      </div>

      <div>
        <label class="label">Gemini 모델 (음성 변환)</label>
        <GeminiModelSelector v-model="geminiModel" />
      </div>

      <div class="flex items-start gap-2 p-3 rounded-lg bg-slate-50 border border-slate-200">
        <input
          id="compress"
          v-model="compressAudio"
          type="checkbox"
          class="mt-0.5 w-4 h-4 rounded"
        />
        <label for="compress" class="text-sm text-slate-700 cursor-pointer">
          <div class="font-medium">큰 파일 자동 압축 (권장)</div>
          <div class="text-xs text-slate-500 mt-0.5">
            서버에 ffmpeg가 있으면 18 MB 이상 오디오를 Opus 32 kbps로 재인코딩해서
            처리 속도와 비용을 크게 줄입니다. ffmpeg이 없으면 원본 그대로 Files API로 업로드합니다.
          </div>
        </label>
      </div>

      <div>
        <label class="label">오디오 파일</label>
        <AudioUploader
          :uploading="uploading"
          :progress="progress"
          @select="(f) => (file = f)"
        />
        <p
          v-if="isLargeFile"
          class="text-xs text-amber-700 mt-2"
        >
          ⚠ {{ formatBytes(file!.size) }} 파일 — Gemini Files API로 업로드되고,
          전체 처리에 몇 분이 걸릴 수 있습니다.
          <span v-if="pipeline === 'gemini_whisper'">
            Whisper는 25 MB 제한이 있으므로 "Gemini Only" 를 권장합니다.
          </span>
        </p>
      </div>

      <p v-if="errorMsg" class="text-sm text-rose-600">{{ errorMsg }}</p>

      <div class="flex items-center justify-end gap-2 pt-2">
        <button class="btn-ghost" @click="router.push('/')">취소</button>
        <button class="btn-primary" :disabled="submitting" @click="submit">
          {{ submitting ? '처리 중…' : '회의 생성 & 처리 시작' }}
        </button>
      </div>
    </div>
  </section>
</template>
