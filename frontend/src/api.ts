export const API_BASE =
  import.meta.env.VITE_API_BASE?.replace(/\/$/, '') ?? 'http://127.0.0.1:8765';

export type ManifestRow = {
  kind: 'targets' | 'places';
  line_number: number;
  id: string;
  label: string;
  approved: boolean;
  file_path?: string | null;
  values: Record<string, string>;
};

export type ManifestValidation = {
  path: string;
  kind: 'targets' | 'places';
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
};

export type OutputItem = {
  id: string;
  target_id: string;
  still_path: string | null;
  video_path: string | null;
  sidecar_path: string;
  sidecar: Record<string, unknown>;
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
      `Cannot reach the local FastAPI backend at ${API_BASE}. Start the app with Start desaparecidos.command.`,
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
        `The server at ${API_BASE} is not the desaparecidos FastAPI backend. Restart Start desaparecidos.command; it will choose a free backend port if 8765 is occupied.`,
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
  require_files: boolean;
}): Promise<ValidateResponse> {
  return request('/api/validate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function downloadManifest(payload: {
  manifest: string;
  kind: 'targets' | 'places';
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

export function generateStage1(payload: {
  targets: string;
  sources: string;
  output_dir: string;
  seed: number;
  fragment_size: number;
  reuse_limit: number;
  output_width: number;
  make_video: boolean;
  target_id?: string;
}): Promise<Record<string, unknown>> {
  return request('/api/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listOutputs(outputDir: string): Promise<{ items: OutputItem[] }> {
  return request(`/api/outputs?output_dir=${encodeURIComponent(outputDir)}`);
}
