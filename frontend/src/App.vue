<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-full flex flex-col">
    <header class="bg-white border-b border-slate-200 sticky top-0 z-30">
      <div class="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
        <RouterLink to="/" class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-brand-600 grid place-items-center text-white font-bold">
            M
          </div>
          <span class="font-semibold tracking-tight">Meeting Minute Agent</span>
        </RouterLink>
        <nav class="flex items-center gap-1 text-sm">
          <RouterLink
            to="/"
            class="px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            active-class="text-brand-700 bg-brand-50"
            >회의 목록</RouterLink
          >
          <RouterLink
            to="/meetings/new"
            class="px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            active-class="text-brand-700 bg-brand-50"
            >새 회의</RouterLink
          >
          <RouterLink
            to="/about"
            class="px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            active-class="text-brand-700 bg-brand-50"
            >소개</RouterLink
          >
        </nav>
      </div>
    </header>

    <main class="flex-1">
      <div class="max-w-6xl mx-auto px-6 py-8">
        <RouterView />
      </div>
    </main>

    <footer class="border-t border-slate-200 bg-white">
      <div class="max-w-6xl mx-auto px-6 py-4 text-xs text-slate-500">
        Powered by Gemini 3.1 Pro · Whisper · GPT-4o · Claude
      </div>
    </footer>
  </div>
</template>
