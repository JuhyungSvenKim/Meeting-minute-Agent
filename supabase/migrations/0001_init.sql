-- Meeting Minute Agent — initial schema
-- Run this in Supabase SQL Editor (or via supabase CLI).

create extension if not exists "pgcrypto";

-- =========================================================
-- meetings
-- =========================================================
create table if not exists public.meetings (
    id              uuid primary key default gen_random_uuid(),
    title           text not null,
    meeting_date    timestamptz,
    duration_seconds integer,
    status          text not null default 'created'
        check (status in ('created','uploaded','processing','transcribed','summarized','error')),
    pipeline_type   text
        check (pipeline_type is null or pipeline_type in ('gemini','gemini_whisper')),
    error_message   text,
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now()
);

-- =========================================================
-- audio_files
-- =========================================================
create table if not exists public.audio_files (
    id              uuid primary key default gen_random_uuid(),
    meeting_id      uuid not null references public.meetings(id) on delete cascade,
    storage_path    text not null,
    filename        text not null,
    size            bigint not null,
    mime_type       text not null,
    created_at      timestamptz not null default now()
);
create index if not exists audio_files_meeting_id_idx on public.audio_files(meeting_id);

-- =========================================================
-- transcripts
-- =========================================================
create table if not exists public.transcripts (
    id               uuid primary key default gen_random_uuid(),
    meeting_id       uuid not null references public.meetings(id) on delete cascade,
    provider         text not null,
    raw_response     jsonb,
    full_text        text,
    confidence_score numeric(5,4),
    language         text,
    created_at       timestamptz not null default now()
);
create index if not exists transcripts_meeting_id_idx on public.transcripts(meeting_id);

-- =========================================================
-- speaker_segments
-- =========================================================
create table if not exists public.speaker_segments (
    id              uuid primary key default gen_random_uuid(),
    transcript_id   uuid not null references public.transcripts(id) on delete cascade,
    speaker_label   text not null,
    speaker_name    text,
    start_time      numeric(10,3) not null,
    end_time        numeric(10,3) not null,
    text            text not null,
    confidence      numeric(5,4),
    gender_estimate text,
    segment_order   integer not null,
    created_at      timestamptz not null default now()
);
create index if not exists speaker_segments_transcript_id_idx on public.speaker_segments(transcript_id);
create index if not exists speaker_segments_order_idx on public.speaker_segments(transcript_id, segment_order);

-- =========================================================
-- summaries
-- =========================================================
create table if not exists public.summaries (
    id              uuid primary key default gen_random_uuid(),
    meeting_id      uuid not null references public.meetings(id) on delete cascade,
    llm_provider    text not null,
    content         jsonb not null,
    format_type     text not null default 'standard',
    created_at      timestamptz not null default now()
);
create index if not exists summaries_meeting_id_idx on public.summaries(meeting_id);

-- =========================================================
-- updated_at trigger
-- =========================================================
create or replace function public.set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists meetings_set_updated_at on public.meetings;
create trigger meetings_set_updated_at
before update on public.meetings
for each row execute function public.set_updated_at();

-- =========================================================
-- Storage bucket (idempotent)
-- =========================================================
insert into storage.buckets (id, name, public, file_size_limit)
values ('meeting-audio', 'meeting-audio', false, 524288000)
on conflict (id) do update
set file_size_limit = excluded.file_size_limit;
