<script setup lang="ts">
defineProps<{ title: string; description?: string }>()
</script>

<template>
  <div class="text-center py-16 px-6">
    <div class="w-14 h-14 mx-auto rounded-full bg-slate-100 grid place-items-center mb-4">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        class="w-6 h-6 text-slate-400"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-3a2.25 2.25 0 00-2.25 2.25V9m7.5 0H6.75A2.25 2.25 0 004.5 11.25v7.5A2.25 2.25 0 006.75 21h10.5a2.25 2.25 0 002.25-2.25v-7.5A2.25 2.25 0 0017.25 9z"
        />
      </svg>
    </div>
    <h3 class="text-base font-semibold text-slate-800">{{ title }}</h3>
    <p v-if="description" class="text-sm text-slate-500 mt-1.5 max-w-sm mx-auto">
      {{ description }}
    </p>
    <slot />
  </div>
</template>
