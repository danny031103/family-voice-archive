create extension if not exists vector;

create table if not exists recordings (
  id uuid primary key default gen_random_uuid(),
  person text not null,
  title text not null,
  date date not null,
  prompt text,
  themes text[],
  summary text,
  transcript text not null,
  audio_drive_path text,
  obsidian_note_path text,
  embedding vector(1536),
  created_at timestamptz default now()
);

create index if not exists recordings_embedding_idx
  on recordings using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create or replace function match_recordings(
  query_embedding vector(1536),
  match_count int default 5
)
returns table (
  id uuid,
  person text,
  title text,
  date date,
  themes text[],
  summary text,
  transcript text,
  obsidian_note_path text,
  similarity float
)
language sql stable
as $$
  select
    id, person, title, date, themes, summary, transcript, obsidian_note_path,
    1 - (embedding <=> query_embedding) as similarity
  from recordings
  where embedding is not null
  order by embedding <=> query_embedding
  limit match_count;
$$;
