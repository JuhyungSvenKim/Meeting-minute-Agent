<script setup lang="ts"></script>

<template>
  <section class="max-w-3xl mx-auto">
    <h1 class="text-2xl font-bold tracking-tight mb-2">Meeting Minute Agent</h1>
    <p class="text-slate-600 mb-6">
      회의 오디오를 업로드하면 자동으로 화자 분리, 트랜스크립션, 요약, PDF/MD/TXT 내보내기까지 한 번에 처리합니다.
    </p>

    <div class="card p-6 space-y-5">
      <section>
        <h2 class="text-base font-semibold text-slate-800 mb-2">파이프라인</h2>
        <ul class="text-sm text-slate-700 space-y-2 list-disc pl-5">
          <li>
            <strong>Gemini Only</strong> — Gemini 3.1 Pro 단독으로 화자 분리 + 트랜스크립트.
            가장 빠르고 저렴.
          </li>
          <li>
            <strong>Gemini + Whisper</strong> — Gemini의 화자 분리 결과 위에 Whisper의 STT
            텍스트를 시간 윈도우 기준으로 합성.
          </li>
        </ul>
      </section>

      <section>
        <h2 class="text-base font-semibold text-slate-800 mb-2">LLM 요약</h2>
        <p class="text-sm text-slate-700">
          요약은 Gemini, GPT-4o, Claude 중 선택해서 재생성할 수 있습니다.
          제공자별로 결과 톤·스타일이 달라집니다.
        </p>
      </section>

      <section>
        <h2 class="text-base font-semibold text-slate-800 mb-2">데이터 모델</h2>
        <p class="text-sm text-slate-700">
          Supabase Postgres에 meetings / audio_files / transcripts / speaker_segments / summaries
          테이블로 저장되며, 오디오는 <code class="text-xs bg-slate-100 px-1 rounded">meeting-audio</code>
          버킷(최대 500MB)에 보관됩니다.
        </p>
      </section>
    </div>
  </section>
</template>
