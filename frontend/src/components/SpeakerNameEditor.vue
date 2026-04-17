<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  label: string
  name: string | null
  colorClasses: { bg: string; text: string; ring: string; dot: string }
}>()

const emit = defineEmits<{ (e: 'save', name: string): void }>()

const editing = ref(false)
const value = ref(props.name ?? '')

watch(
  () => props.name,
  (n) => {
    value.value = n ?? ''
  },
)

function startEdit() {
  editing.value = true
  value.value = props.name ?? ''
}

function commit() {
  const v = value.value.trim()
  if (v && v !== (props.name ?? '')) emit('save', v)
  editing.value = false
}

function cancel() {
  editing.value = false
  value.value = props.name ?? ''
}
</script>

<template>
  <div
    class="inline-flex items-center gap-2 px-2 py-0.5 rounded-full text-xs ring-1"
    :class="[colorClasses.bg, colorClasses.text, colorClasses.ring]"
  >
    <span :class="['w-1.5 h-1.5 rounded-full', colorClasses.dot]"></span>

    <template v-if="!editing">
      <span class="font-medium">{{ name || label }}</span>
      <span v-if="name" class="text-[10px] opacity-70">({{ label }})</span>
      <button
        class="ml-0.5 opacity-60 hover:opacity-100"
        title="화자 이름 편집"
        @click.stop="startEdit"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          class="w-3 h-3"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L7.5 19.152 3 20.25l1.098-4.5L16.862 4.487z"
          />
        </svg>
      </button>
    </template>

    <template v-else>
      <input
        v-model="value"
        class="bg-white/70 rounded px-1.5 py-0.5 text-xs w-28 outline-none ring-1 ring-current"
        :placeholder="label"
        @keyup.enter="commit"
        @keyup.escape="cancel"
        @click.stop
      />
      <button class="text-[10px] font-semibold" @click.stop="commit">저장</button>
      <button class="text-[10px] opacity-70" @click.stop="cancel">취소</button>
    </template>
  </div>
</template>
