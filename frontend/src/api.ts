export const API_BASE =
  import.meta.env.VITE_API_BASE?.replace(/\/$/, '') ?? 'http://127.0.0.1:8765';

export type ManifestRow = {
  kind: 'targets' | 'places' | 'people';
  line_number: number;
  id: string;
  label: string;
  approved: boolean;
  file_path?: string | null;
  values: Record<string, string>;
};

export type ManifestValidation = {
  path: string;
  kind: 'targets' | 'places' | 'people';
  ok: boolean;
  errors: string[];
  warnings: string[];
  row_count: number;
  approved_count: number;
  rows: ManifestRow[];
};

export type ValidateResponse = {
  ok: boolean;
  targets: ManifestValidation;
  sources: ManifestValidation;
  people: ManifestValidation;
};

export type OutputItem = {
  id: string;
  target_id: string;
  still_path: string | null;
  video_path: string | null;
  sidecar_path: string;
  sidecar: Record<string, unknown>;
};

export type GenerateResponse = {
  ok: boolean;
  outputs: Array<{
    target_id: string;
    still_path: string;
    sidecar_path: string;
    video_path: string | null;
  }>;
};

export type ArtworkKind = 'todos-somos-familiares' | 'estan-en-todas-partes' | 'seguimos-buscando';
export type FragmentArtworkKind = Exclude<ArtworkKind, 'seguimos-buscando'>;
export type VideoSourceLayout = 'grid' | 'match';
export type RouteGeometry = {
  type: 'LineString' | 'MultiLineString' | 'Polygon';
  coordinates: number[][] | number[][][];
};

export type TraversalFrame = {
  id: string;
  ordinal: number;
  provider_id: string;
  sequence_id: string;
  longitude: number;
  latitude: number;
  compass_angle: number;
  captured_at?: number | string | null;
  local_path: string;
  review_status: 'pending' | 'approved' | 'rejected';
  cv_label: string;
  cv_reason: string;
  cv_accept?: boolean;
  sequence_jump: boolean;
  region_index?: number | null;
};

export type Traversal = {
  id: string;
  name: string;
  artwork: 'seguimos-buscando';
  provider: string;
  mode: 'manual' | 'import' | 'autonomous';
  geometry: RouteGeometry;
  duration_seconds: number;
  regions?: number | null;
  walks?: {
    region_index: number | null;
    sequence_id: string;
    first_frame_id: string;
    frame_count: number;
  }[] | null;
  gap_policy: 'direct-jump-cut';
  release_status: 'internal_unreviewed';
  attribution: string;
  created_at: string;
  updated_at: string;
  frames: TraversalFrame[];
  summary?: {
    frame_count: number;
    approved_count: number;
    pending_count: number;
    rejected_count: number;
  };
  acquisition?: { attempted: number; acquired: number; errors: string[]; completed_at: string };
};

export type CrawlResponse = {
  ok: boolean;
  manifest: string;
  kind: 'targets' | 'places' | 'people';
  pages: string[];
  run_id: string;
  trail_path?: string | null;
  errors: string[];
  pages_crawled: number;
  images_seen: number;
  from_cache: number;
  cv_rejected: number;
  duplicates: number;
  added: number;
  items: Array<{
    id: string;
    page_url: string;
    image_url: string;
    local_path: string;
    ok: boolean;
    bytes_written: number;
    from_cache: boolean;
    duplicate: boolean;
    cv_label: string;
    cv_score: number;
    cv_accept: boolean;
    content_sha256: string;
    perceptual_hash: string;
    crawl_run_id: string;
    error?: string | null;
  }>;
};

export type CombinedCrawlResponse = {
  ok: boolean;
  pages: string[];
  pages_crawled: number;
  images_seen: number;
  errors: string[];
  results: {
    places: CrawlResponse;
    people: CrawlResponse;
  };
};

export type PortraitCandidate = {
  id: string;
  source_url: string;
  source_page: string;
  source_id: string;
  source_name: string;
  licence_or_terms: string;
  accessed_at: string;
  raw_path: string;
  processed_path: string;
  sha256: string;
  width: number | string;
  height: number | string;
  status: string;
  confidence: string;
  notes: string;
};

export type PortraitReview = {
  needs_review: boolean;
  reason: string;
  selected_area: number;
  best_alternative_area: number;
  candidate_count: number;
  review_candidate_count: number;
  best_alternative_id: string;
  best_alternative_source: string;
};

export type PersonRecord = {
  id: string;
  slug: string;
  full_name: string;
  given_names: string;
  family_names: string;
  date_of_birth: string;
  place_of_birth: string;
  age_at_disappearance: number | string;
  nationality: string[];
  occupations: string[];
  union_militancy: string[];
  political_militancy: string[];
  date_of_disappearance: string;
  date_of_detention: string;
  date_of_death: string;
  place_of_death: string;
  country_of_detention: string;
  place_of_disappearance: string;
  country_of_disappearance: string;
  places_of_detention: string[];
  remains_status: 'found' | 'not_found' | 'unknown';
  date_of_remains_found: string;
  place_of_remains_found: string;
  date_of_identification: string;
  victim_type: string;
  short_bio: string;
  notes: string;
  source_page: string;
  sources: string[];
  field_sources: Record<string, string>;
  field_source_refs: Record<string, string>;
  portrait_status: string;
  portrait_candidates: PortraitCandidate[];
  selected_portrait_id: string;
  selected_portrait?: PortraitCandidate | null;
  portrait_review: PortraitReview;
  review_status: 'pending' | 'approved' | 'rejected';
  missing_fields: string[];
  created_at: string;
  updated_at: string;
};

export type PersonsResponse = {
  ok: boolean;
  path: string;
  summary: {
    count: number;
    missing_count: number;
    weak_portrait_count: number;
    portrait_review_count: number;
    approved_count: number;
  };
  required_fields: string[];
  people: PersonRecord[];
};

export type SourceRegistry = {
  description: string;
  sources: Array<{
    id: string;
    name: string;
    url: string;
    kind: string;
    licence: string;
    trust?: Record<string, string>;
    notes: string;
  }>;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
      ...init,
    });
  } catch {
    throw new Error(
      `Cannot reach the local FastAPI backend at ${API_BASE}. Start the app with ./start.sh.`,
    );
  }
  if (!response.ok) {
    const body = await response.text();
    const contentType = response.headers.get('content-type') ?? '';
    let detailMessage: string | null = null;
    try {
      const parsed = JSON.parse(body) as { detail?: unknown };
      if (typeof parsed.detail === 'string') {
        detailMessage = parsed.detail;
      }
    } catch {
      detailMessage = null;
    }
    if (detailMessage) {
      throw new Error(detailMessage);
    }
    if (contentType.includes('text/html') || body.trimStart().startsWith('<!DOCTYPE')) {
      throw new Error(
        `The server at ${API_BASE} is not the desaparecidos FastAPI backend. Restart ./start.sh; it will choose a free backend port if 8765 is occupied.`,
      );
    }
    throw new Error(body || response.statusText);
  }
  return response.json() as Promise<T>;
}

export function fileUrl(path: string): string {
  return `${API_BASE}/api/file?path=${encodeURIComponent(path)}`;
}

export function validateManifests(payload: {
  targets: string;
  sources: string;
  people: string;
  require_files: boolean;
}): Promise<ValidateResponse> {
  return request('/api/validate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function downloadManifest(payload: {
  manifest: string;
  kind: 'targets' | 'places' | 'people';
  output_root: string;
}): Promise<Record<string, unknown>> {
  return request('/api/download', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function createDemoFixtures(): Promise<{
  ok: boolean;
  targets: string;
  sources: string;
  images: string[];
}> {
  return request('/api/demo-fixtures', {
    method: 'POST',
    body: JSON.stringify({}),
  });
}

export function listPersons(store: string): Promise<PersonsResponse> {
  return request(`/api/persons?store=${encodeURIComponent(store)}`);
}

export function savePerson(payload: {
  store: string;
  person: PersonRecord;
}): Promise<{ ok: boolean; person: PersonRecord }> {
  return request('/api/persons/save', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function deletePersonRecord(payload: {
  store: string;
  person_id: string;
}): Promise<{ ok: boolean; summary: PersonsResponse['summary'] }> {
  return request('/api/persons/delete', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listPersonSources(): Promise<{ ok: boolean; registry: SourceRegistry }> {
  return request('/api/persons/sources');
}

export function addPersonPortrait(payload: {
  store: string;
  person_id: string;
  image_url: string;
  source_page: string;
  source_id: string;
  source_name: string;
  licence_or_terms: string;
  notes: string;
  raw_root: string;
  overwrite: boolean;
}): Promise<{ ok: boolean; person: PersonRecord }> {
  return request('/api/persons/portrait/add', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function selectPersonPortrait(payload: {
  store: string;
  person_id: string;
  candidate_id: string;
}): Promise<{ ok: boolean; person: PersonRecord }> {
  return request('/api/persons/portrait/select', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function processPersonPortrait(payload: {
  store: string;
  person_id: string;
  candidate_id: string;
  selected_root: string;
  aspect: number;
  use_face: boolean;
  max_side: number;
  overwrite: boolean;
}): Promise<{ ok: boolean; person: PersonRecord }> {
  return request('/api/persons/portrait/process', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function exportTargetsFromPersons(payload: {
  store: string;
  manifest: string;
  approved: boolean;
}): Promise<{
  ok: boolean;
  manifest: string;
  rows_written: number;
  people_seen: number;
  skipped: number;
}> {
  return request('/api/persons/export-targets', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function crawlPages(payload: {
  pages: string[];
  kind: 'places' | 'people';
  manifest: string;
  output_root: string;
  max_images_per_page: number;
  label_prefix: string;
  max_depth: number;
  max_pages: number;
  max_images: number;
  cross_domain: boolean;
  use_cv: boolean;
}): Promise<CrawlResponse> {
  return request('/api/crawl', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function crawlPagesCombined(payload: {
  pages: string[];
  places_manifest: string;
  people_manifest: string;
  output_root: string;
  max_images_per_page: number;
  label_prefix: string;
  max_depth: number;
  max_pages: number;
  max_images: number;
  cross_domain: boolean;
  use_cv: boolean;
}): Promise<CombinedCrawlResponse> {
  return request('/api/crawl/combined', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateReviewStatus(payload: {
  manifest: string;
  kind: 'targets' | 'places' | 'people';
  row_id: string;
  review_status: 'approved' | 'pending' | 'rejected';
}): Promise<{ ok: boolean; manifest: ManifestValidation }> {
  return request('/api/review', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateReviewStatusBulk(payload: {
  manifest: string;
  kind: 'targets' | 'places' | 'people';
  review_status: 'approved' | 'pending' | 'rejected';
  row_ids?: string[];
  all?: boolean;
}): Promise<{ ok: boolean; manifest: ManifestValidation }> {
  return request('/api/review-bulk', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function deleteReviewRow(payload: {
  manifest: string;
  kind: 'targets' | 'places' | 'people';
  row_id: string;
}): Promise<{ ok: boolean; manifest: ManifestValidation }> {
  return request('/api/review/delete', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function deleteReviewRows(payload: {
  manifest: string;
  kind: 'targets' | 'places' | 'people';
  row_ids: string[];
}): Promise<{ ok: boolean; manifest: ManifestValidation }> {
  return request('/api/review/delete', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function generateStage1(payload: {
  targets: string;
  sources: string;
  output_dir: string;
  seed: number;
  fragment_size: number;
  reuse_limit: number;
  output_width: number;
  max_contribution_per_source: number;
  search_scan_frames_per_candidate: number;
  search_scan_max_candidates: number;
  video_source_layout: VideoSourceLayout;
  make_video: boolean;
  target_id?: string;
  artwork: ArtworkKind;
}): Promise<GenerateResponse> {
  return request('/api/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listTraversals(root = 'data/raw/traversals'): Promise<{ ok: boolean; items: Traversal[] }> {
  return request(`/api/traversals?root=${encodeURIComponent(root)}`);
}

export function discoverTraversal(payload: {
  name: string;
  mode: 'manual' | 'import' | 'autonomous';
  geometry?: RouteGeometry;
  import_content?: string;
  import_format?: 'geojson' | 'gpx';
  duration_seconds: number;
  max_frames: number;
  regions?: number;
  root?: string;
}): Promise<{ ok: boolean; traversal: Traversal }> {
  return request('/api/traversals/discover', { method: 'POST', body: JSON.stringify(payload) });
}

export function acquireTraversal(payload: {
  traversal_id: string;
  max_frames: number;
  root?: string;
}): Promise<{ ok: boolean; traversal: Traversal }> {
  return request('/api/traversals/acquire', { method: 'POST', body: JSON.stringify(payload) });
}

export function reviewTraversalFrames(payload: {
  traversal_id: string;
  frame_ids: string[];
  review_status: 'pending' | 'approved' | 'rejected';
  root?: string;
}): Promise<{ ok: boolean; traversal: Traversal }> {
  const { traversal_id, ...body } = payload;
  return request(`/api/traversals/${encodeURIComponent(traversal_id)}/frames/review`, {
    method: 'POST', body: JSON.stringify(body),
  });
}

export function generateTraversal(payload: {
  traversal_id: string;
  targets: string;
  output_dir: string;
  traversal_root?: string;
  target_ids: string[];
  target_mode: 'single' | 'sequence';
  composition: 'overlay' | 'alternate' | 'split';
  duration_seconds: number;
  fps: number;
  seed: number;
  fragment_size: number;
  output_width: number;
  reuse_limit: number;
  max_contribution_per_source: number;
}): Promise<GenerateResponse> {
  return request('/api/generate/traversal', { method: 'POST', body: JSON.stringify(payload) });
}

export function listOutputs(outputDir: string): Promise<{ items: OutputItem[] }> {
  return request(`/api/outputs?output_dir=${encodeURIComponent(outputDir)}`);
}

export function deleteOutputs(payload: {
  output_dir: string;
  ids: string[];
  all: boolean;
}): Promise<{ ok: boolean; deleted: string[]; errors: string[] }> {
  return request('/api/outputs/delete', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
