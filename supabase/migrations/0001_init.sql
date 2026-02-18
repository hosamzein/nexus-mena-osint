-- Nexus MENA OSINT baseline schema

create table if not exists cases (
  id text primary key,
  title text not null,
  query text not null,
  status text not null default 'draft',
  risk_score numeric not null default 0,
  severity text not null default 'R1',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists case_platforms (
  case_id text not null references cases(id) on delete cascade,
  platform text not null,
  primary key (case_id, platform)
);

create table if not exists content_items (
  id text primary key,
  case_id text not null references cases(id) on delete cascade,
  platform text not null,
  author text not null,
  text_content text not null,
  source_url text,
  observed_at timestamptz not null,
  language text,
  engagement int not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists entities (
  id bigserial primary key,
  canonical_name text not null,
  entity_type text not null default 'keyword',
  confidence numeric not null default 0.5,
  created_at timestamptz not null default now()
);

create table if not exists item_entities (
  item_id text not null references content_items(id) on delete cascade,
  entity_id bigint not null references entities(id) on delete cascade,
  primary key (item_id, entity_id)
);

create table if not exists relations (
  id bigserial primary key,
  case_id text not null references cases(id) on delete cascade,
  source_ref text not null,
  target_ref text not null,
  relation_type text not null,
  weight numeric not null default 1,
  confidence numeric not null default 0.5,
  created_at timestamptz not null default now()
);

create table if not exists risk_scores (
  id bigserial primary key,
  case_id text not null references cases(id) on delete cascade,
  harm numeric not null default 0,
  velocity numeric not null default 0,
  reach numeric not null default 0,
  coordination numeric not null default 0,
  credibility_gap numeric not null default 0,
  cross_platform numeric not null default 0,
  total_score numeric not null default 0,
  severity text not null default 'R1',
  created_at timestamptz not null default now()
);

create table if not exists evidence (
  id bigserial primary key,
  case_id text not null references cases(id) on delete cascade,
  item_id text references content_items(id) on delete set null,
  evidence_hash text not null,
  source_name text not null,
  source_url text,
  observed_at timestamptz not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table cases enable row level security;
alter table content_items enable row level security;
alter table entities enable row level security;
alter table relations enable row level security;
alter table risk_scores enable row level security;
alter table evidence enable row level security;
