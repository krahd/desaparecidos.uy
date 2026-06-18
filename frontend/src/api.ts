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
  make_video: boolean;
  target_id?: string;
}): Promise<GenerateResponse> {
  return request('/api/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
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
