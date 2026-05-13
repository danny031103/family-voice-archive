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
