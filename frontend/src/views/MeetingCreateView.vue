<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { meetingsApi } from '@/services/api'
import { useMeetingsStore } from '@/stores/meetings'
import AudioUploader from '@/components/AudioUploader.vue'
import PipelineSelector from '@/components/PipelineSelector.vue'
import type { PipelineType } from '@/types'

const router = useRouter()
const store = useMeetingsStore()

const title = ref('')
const meetingDate = ref('')
const pipeline = ref<PipelineType>('gemini')

const file = ref<File | null>(null)
const uploading = ref(false)
const progress = ref(0)
const submitting = ref(false)
const errorMsg = ref<string | null>(null)

async function submit() {
  if (!title.value.trim()) {
    errorMsg.value = '회의 제목을 입력해 주세요.'
    return
  }
  if (!file.value) {
    errorMsg.value = '오디오 파일을 선택해 주세요.'
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
    await meetingsApi.uploadAudio(created.id, file.value, (p) => (progress.value = p))
    uploading.value = false

    await store.startProcess(created.id, pipeline.value)
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
        <label class="label">오디오 파일</label>
        <AudioUploader
          :uploading="uploading"
          :progress="progress"
          @select="(f) => (file = f)"
        />
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
