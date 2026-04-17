<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMeetingsStore } from '@/stores/meetings'
import MeetingCard from '@/components/MeetingCard.vue'
import EmptyState from '@/components/EmptyState.vue'

const store = useMeetingsStore()
const router = useRouter()

onMounted(() => store.fetchAll())

const meetings = computed(() => store.meetings)

async function onDelete(id: string) {
  if (!confirm('이 회의를 삭제하시겠습니까? (오디오/트랜스크립트 모두 삭제됩니다)')) return
  await store.remove(id)
}
</script>

<template>
  <section>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">회의 목록</h1>
        <p class="text-sm text-slate-500 mt-1">
          업로드한 오디오로부터 화자 분리 트랜스크립트와 회의록을 자동 생성합니다.
        </p>
      </div>
      <button class="btn-primary" @click="router.push('/meetings/new')">+ 새 회의</button>
    </div>

    <div v-if="store.loading" class="text-sm text-slate-500">로딩 중…</div>
    <div v-else-if="store.error" class="text-sm text-rose-600">{{ store.error }}</div>

    <EmptyState
      v-else-if="meetings.length === 0"
      title="아직 회의가 없습니다"
      description="새 회의를 만들고 오디오를 업로드해 보세요."
    >
      <button class="btn-primary mt-4" @click="router.push('/meetings/new')">
        첫 회의 만들기
      </button>
    </EmptyState>

    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <MeetingCard
        v-for="m in meetings"
        :key="m.id"
        :meeting="m"
        @delete="onDelete"
      />
    </div>
  </section>
</template>
