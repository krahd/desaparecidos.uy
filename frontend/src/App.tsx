import {
  Ban,
  Check,
  CheckCircle2,
  CheckSquare,
  Eye,
  FileCheck2,
  Globe2,
  Image as ImageIcon,
  LayoutGrid,
  Maximize2,
  Play,
  RefreshCw,
  Settings,
  Square,
  Trash2,
  Video,
  X,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import {
  CrawlResponse,
  ManifestRow,
  OutputItem,
  ValidateResponse,
  crawlPages,
  createDemoFixtures,
  deleteOutputs,
  deleteReviewRow,
  deleteReviewRows,
  fileUrl,
  generateStage1,
  listOutputs,
  updateReviewStatus,
  updateReviewStatusBulk,
  validateManifests,
} from './api';

type LogEntry = {
  at: string;
  text: string;
  tone?: 'ok' | 'error';
};

type SectionId = 'manifests' | 'review' | 'generate' | 'outputs';
type ReviewKind = 'targets' | 'places' | 'people';
type CrawlKind = 'places' | 'people';
type ReviewStatus = 'approved' | 'pending' | 'rejected';
type CrawlPreset = {
  id: string;
  label: string;
  kind: CrawlKind;
  manifest: string;
  pages: string[];
  maxImages: number;
  labelPrefix: string;
};

const defaultPaths = {
  targets: 'data/manifests/local-targets.csv',
  sources: 'data/manifests/places.csv',
  people: 'data/manifests/people.csv',
  outputDir: 'outputs/stage1',
};

const crawlerManifestDefaults: Record<CrawlKind, string> = {
  places: 'data/manifests/crawled-places.csv',
  people: 'data/manifests/crawled-people.csv',
};

const crawlPresets: CrawlPreset[] = [
  {
    id: 'montevideo-tourism',
    label: 'Montevideo tourism',
    kind: 'places',
    manifest: crawlerManifestDefaults.places,
    pages: ['https://montevideo.gub.uy/tipo/area-tematica/turismo-y-tiempo-libre'],
    maxImages: 12,
    labelPrefix: 'Montevideo tourism',
  },
  {
    id: 'montevideo-events',
    label: 'Montevideo events',
    kind: 'places',
    manifest: crawlerManifestDefaults.places,
    pages: ['https://eventos.montevideo.gub.uy/'],
    maxImages: 18,
    labelPrefix: 'Montevideo event',
  },
  {
    id: 'mintur-news',
    label: 'MINTUR news',
    kind: 'places',
    manifest: crawlerManifestDefaults.places,
    pages: ['https://www.gub.uy/ministerio-turismo/comunicacion/noticias'],
    maxImages: 12,
    labelPrefix: 'Uruguay tourism',
  },
  {
    id: 'descubri-montevideo',
    label: 'Descubri Montevideo',
    kind: 'places',
    manifest: crawlerManifestDefaults.places,
    pages: ['https://www.descubrimontevideo.uy/'],
    maxImages: 12,
    labelPrefix: 'Descubri Montevideo',
  },
  {
    id: 'montevideo-people-news',
    label: 'Montevideo people',
    kind: 'people',
    manifest: crawlerManifestDefaults.people,
    pages: ['https://montevideo.gub.uy/noticias'],
    maxImages: 12,
    labelPrefix: 'Montevideo people',
  },
  {
    id: 'mec-people-news',
    label: 'MEC people',
    kind: 'people',
    manifest: crawlerManifestDefaults.people,
    pages: ['https://www.gub.uy/ministerio-educacion-cultura/comunicacion/noticias'],
    maxImages: 12,
    labelPrefix: 'MEC people',
  },
  {
    id: 'mintur-people-events',
    label: 'MINTUR people',
    kind: 'people',
    manifest: crawlerManifestDefaults.people,
    pages: ['https://www.gub.uy/ministerio-turismo/comunicacion/noticias'],
    maxImages: 12,
    labelPrefix: 'MINTUR people',
  },
];

function loadStored(key: string, fallback: string): string {
  try {
    return window.localStorage.getItem(`desa.${key}`) ?? fallback;
  } catch {
    return fallback;
  }
}

function saveStored(key: string, value: string): void {
  try {
    window.localStorage.setItem(`desa.${key}`, value);
  } catch {
    /* localStorage unavailable; ignore */
  }
}

function manifestForKind(kind: ReviewKind, paths: { targets: string; sources: string; people: string }): string {
  if (kind === 'targets') return paths.targets;
  if (kind === 'places') return paths.sources;
  return paths.people;
}

export function App() {
  const [targets, setTargets] = useState(() => loadStored('targets', defaultPaths.targets));
  const [sources, setSources] = useState(() => loadStored('sources', defaultPaths.sources));
  const [people, setPeople] = useState(() => loadStored('people', defaultPaths.people));
  const [outputDir, setOutputDir] = useState(() => loadStored('outputDir', defaultPaths.outputDir));
  const [seed, setSeed] = useState(17);
  const [fragmentSize, setFragmentSize] = useState(24);
  const [reuseLimit, setReuseLimit] = useState(8);
  const [outputWidth, setOutputWidth] = useState(720);
  const [maxContribution, setMaxContribution] = useState(0);
  const [targetId, setTargetId] = useState('');
  const [validation, setValidation] = useState<ValidateResponse | null>(null);
  const [outputs, setOutputs] = useState<OutputItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [crawling, setCrawling] = useState(false);
  const [selectedOutput, setSelectedOutput] = useState<OutputItem | null>(null);
  const [selectedOutputIds, setSelectedOutputIds] = useState<Set<string>>(new Set());
  const [viewerOutput, setViewerOutput] = useState<OutputItem | null>(null);
  const [showUtilities, setShowUtilities] = useState(false);
  const [activeSection, setActiveSection] = useState<SectionId>('manifests');
  const [reviewKind, setReviewKind] = useState<ReviewKind>('places');
  const [selectedReviewIds, setSelectedReviewIds] = useState<Set<string>>(new Set());
  const [crawlKind, setCrawlKind] = useState<CrawlKind>('places');
  const [crawlPagesText, setCrawlPagesText] = useState('');
  const [crawlManifest, setCrawlManifest] = useState(() => (
    loadStored('crawlManifest', crawlerManifestDefaults.places)
  ));
  const [crawlMaxImages, setCrawlMaxImages] = useState(12);
  const [crawlDepth, setCrawlDepth] = useState(2);
  const [crawlMaxPages, setCrawlMaxPages] = useState(60);
  const [crawlMaxTotal, setCrawlMaxTotal] = useState(80);
  const [crawlCrossDomain, setCrawlCrossDomain] = useState(false);
  const [crawlUseCv, setCrawlUseCv] = useState(true);
  const [crawlLabelPrefix, setCrawlLabelPrefix] = useState('');
  const [log, setLog] = useState<LogEntry[]>([
    { at: new Date().toLocaleTimeString(), text: 'GUI ready. Backend must be running on localhost.' },
  ]);

  const appendLog = useCallback((text: string, tone?: LogEntry['tone']) => {
    setLog((entries) => [
      { at: new Date().toLocaleTimeString(), text, tone },
      ...entries,
    ].slice(0, 80));
  }, []);

  const allTargets = validation?.targets.rows ?? [];
  const approvedTargets = allTargets.filter((row) => row.approved);
  const approvedSources = validation?.sources.rows.filter((row) => row.approved) ?? [];
  const reviewRows = reviewKind === 'targets'
    ? allTargets
    : reviewKind === 'places'
      ? validation?.sources.rows ?? []
      : validation?.people.rows ?? [];
  const activeTarget = allTargets.find((row) => row.id === targetId)
    ?? approvedTargets[0]
    ?? allTargets[0];
  const selectedOutputCount = selectedOutputIds.size;
  const selectedReviewCount = selectedReviewIds.size;

  const statusLabel = useMemo(() => {
    if (crawling) return 'crawling';
    if (busy) return 'running';
    if (!validation) return 'not validated';
    return validation.ok ? 'validated' : 'needs attention';
  }, [busy, crawling, validation]);

  const runAction = useCallback(async <T,>(
    label: string,
    action: () => Promise<T>,
    success: string,
  ): Promise<T | null> => {
    setBusy(true);
    appendLog(label);
    try {
      const result = await action();
      appendLog(success, 'ok');
      return result;
    } catch (error) {
      appendLog(error instanceof Error ? error.message : String(error), 'error');
      return null;
    } finally {
      setBusy(false);
    }
  }, [appendLog]);

  const selectWorkflow = useCallback((section: SectionId) => {
    setActiveSection(section);
    const target = document.getElementById(`section-${section}`)
      ?? document.getElementById(`controls-${section}`);
    target?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }, []);

  async function handleValidate(requireFiles = false) {
    const response = await runAction(
      'Validating manifests.',
      () => validateManifests({ targets, sources, people, require_files: requireFiles }),
      'Validation finished.',
    );
    if (!response) return;
    setValidation(response);
    const firstApproved = response.targets.rows.find((row) => row.approved)?.id ?? '';
    if (firstApproved && !response.targets.rows.some((row) => row.id === targetId)) {
      setTargetId(firstApproved);
    }
    setActiveSection('manifests');
  }

  async function handleCreateDemoFixtures() {
    const response = await runAction(
      'Creating synthetic demo fixtures.',
      async () => {
        const fixtures = await createDemoFixtures();
        const checked = await validateManifests({
          targets: fixtures.targets,
          sources: fixtures.sources,
          people,
          require_files: true,
        });
        return { fixtures, checked };
      },
      'Demo fixtures created and validated.',
    );
    if (!response) return;
    setTargets(response.fixtures.targets);
    setSources(response.fixtures.sources);
    setValidation(response.checked);
    setTargetId(response.checked.targets.rows.find((row) => row.approved)?.id ?? '');
    setReviewKind('places');
    setActiveSection('review');
    setShowUtilities(false);
  }

  async function refreshOutputs(preferredPath?: string): Promise<OutputItem | null> {
    const response = await runAction(
      'Refreshing outputs.',
      () => listOutputs(outputDir),
      'Outputs refreshed.',
    );
    if (!response) return null;
    setOutputs(response.items);
    const outputIds = new Set(response.items.map((item) => item.id));
    setSelectedOutputIds((current) => new Set([...current].filter((id) => outputIds.has(id))));
    const selected = response.items.find((item) => (
      item.sidecar_path === preferredPath
      || item.still_path === preferredPath
      || item.video_path === preferredPath
      || item.id === preferredPath
    )) ?? response.items[0] ?? null;
    setSelectedOutput(selected);
    return selected;
  }

  async function handleGenerate(makeVideo: boolean) {
    const response = await runAction(
      makeVideo ? 'Checking manifests, then generating still and video.' : 'Checking manifests, then generating still output.',
      async () => {
        const checked = await validateManifests({ targets, sources, people, require_files: true });
        setValidation(checked);
        const firstApprovedTarget = checked.targets.rows.find((row) => row.approved)?.id ?? '';
        const selectedApproved = checked.targets.rows.find((row) => row.approved && row.id === targetId)?.id ?? '';
        const selectedTargetId = selectedApproved || firstApprovedTarget;
        if (checked.targets.approved_count === 0 || checked.sources.approved_count === 0) {
          throw new Error('No approved target/source rows. Approve rows in Review images, or use utilities to create demo fixtures.');
        }
        if (!checked.ok) {
          throw new Error('Manifest validation failed. Review the Validation panel before generating.');
        }
        return generateStage1({
          targets,
          sources,
          output_dir: outputDir,
          seed,
          fragment_size: fragmentSize,
          reuse_limit: reuseLimit,
          output_width: outputWidth,
          max_contribution_per_source: maxContribution,
          search_scan_frames_per_candidate: 2,
          search_scan_max_candidates: 120,
          make_video: makeVideo,
          target_id: selectedTargetId || undefined,
        });
      },
      makeVideo ? 'Video generation finished.' : 'Still generation finished.',
    );
    if (!response) return;
    appendLog(`Generated ${response.outputs.length} output${response.outputs.length === 1 ? '' : 's'}.`, 'ok');
    const selected = await refreshOutputs(response.outputs[0]?.sidecar_path);
    if (selected) {
      setViewerOutput(selected);
    }
    setActiveSection('outputs');
  }

  async function handleCrawl() {
    const pages = crawlPagesText
      .split(/\r?\n/)
      .map((page) => page.trim())
      .filter(Boolean);
    if (pages.length === 0) {
      appendLog('Add at least one page URL before crawling.', 'error');
      return;
    }
    if (crawling) {
      appendLog('A crawl is already running.', 'error');
      return;
    }

    appendLog(
      `Crawl queued: ${pages.length} seed page${pages.length === 1 ? '' : 's'} for ${crawlKind}; `
      + `depth ${crawlDepth}; max ${crawlMaxPages} pages; max ${crawlMaxTotal} images; `
      + `${crawlCrossDomain ? 'cross-domain' : 'same-domain'}; CV ${crawlUseCv ? 'on' : 'off'}.`,
    );
    appendLog(`Crawling ${crawlKind}; review remains available.`);
    setCrawling(true);
    let response: CrawlResponse | null = null;
    try {
      response = await crawlPages({
        pages,
        kind: crawlKind,
        manifest: crawlManifest,
        output_root: 'data/raw/crawl',
        max_images_per_page: crawlMaxImages,
        label_prefix: crawlLabelPrefix,
        max_depth: crawlDepth,
        max_pages: crawlMaxPages,
        max_images: crawlMaxTotal,
        cross_domain: crawlCrossDomain,
        use_cv: crawlUseCv,
      });
      appendLog('Crawler finished.', 'ok');
    } catch (error) {
      appendLog(error instanceof Error ? error.message : String(error), 'error');
    } finally {
      setCrawling(false);
    }
    if (!response) return;

    if (crawlKind === 'places') {
      setSources(response.manifest);
    } else {
      setPeople(response.manifest);
    }
    setReviewKind(crawlKind);
    setActiveSection('review');

    const checked = await validateManifests({
      targets,
      sources: crawlKind === 'places' ? response.manifest : sources,
      people: crawlKind === 'people' ? response.manifest : people,
      require_files: true,
    }).catch(() => null);
    if (checked) setValidation(checked);

    appendLog(
      `Crawler run ${response.run_id}: ${response.pages_crawled} pages, ${response.images_seen} images, `
      + `${response.added} added, ${response.duplicates} duplicates, ${response.cv_rejected} CV-rejected, `
      + `${response.from_cache} from cache.`,
      response.added ? 'ok' : undefined,
    );
    const rejected = response.items.filter(
      (item) => !item.cv_accept && item.cv_label && item.cv_label !== 'cv-off',
    );
    if (rejected.length > 0) {
      const counts = rejected.reduce<Record<string, number>>((acc, item) => {
        acc[item.cv_label] = (acc[item.cv_label] ?? 0) + 1;
        return acc;
      }, {});
      const breakdown = Object.entries(counts)
        .map(([label, count]) => `${label} ${count}`)
        .join(', ');
      appendLog(`CV rejected: ${breakdown}.`);
    }
    response.errors.slice(0, 8).forEach((error) => appendLog(error, 'error'));
  }

  async function handleReviewStatus(row: ManifestRow, status: ReviewStatus) {
    const manifest = manifestForKind(row.kind, { targets, sources, people });
    const response = await runAction(
      `${status === 'approved' ? 'Approving' : status === 'rejected' ? 'Rejecting' : 'Resetting'} ${row.label}.`,
      async () => {
        await updateReviewStatus({
          manifest,
          kind: row.kind,
          row_id: row.id,
          review_status: status,
        });
        return validateManifests({ targets, sources, people, require_files: true });
      },
      'Review status updated.',
    );
    if (!response) return;
    setValidation(response);
    if (row.kind === 'targets' && status === 'approved') {
      setTargetId(row.id);
    }
  }

  async function handleDeleteReview(row: ManifestRow) {
    const manifest = manifestForKind(row.kind, { targets, sources, people });
    const confirmed = window.confirm(
      `Delete "${row.label}" from the ${row.kind} manifest? The cached image file is kept on disk.`,
    );
    if (!confirmed) return;
    const response = await runAction(
      `Deleting ${row.label} from the ${row.kind} manifest.`,
      async () => {
        await deleteReviewRow({ manifest, kind: row.kind, row_id: row.id });
        return validateManifests({ targets, sources, people, require_files: true });
      },
      'Row deleted.',
    );
    if (!response) return;
    setValidation(response);
    if (row.id === targetId) {
      setTargetId(response.targets.rows.find((candidate) => candidate.approved)?.id ?? '');
    }
  }

  function toggleReviewSelection(id: string) {
    setSelectedReviewIds((current) => {
      const next = new Set(current);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  async function handleApproveSelected() {
    const manifest = manifestForKind(reviewKind, { targets, sources, people });
    const ids = Array.from(selectedReviewIds);
    if (ids.length === 0) {
      appendLog('Select one or more rows to approve.', 'error');
      return;
    }
    const response = await runAction(
      `Approving ${ids.length} selected ${reviewKind} row${ids.length === 1 ? '' : 's'}.`,
      async () => {
        await updateReviewStatusBulk({ manifest, kind: reviewKind, review_status: 'approved', row_ids: ids });
        return validateManifests({ targets, sources, people, require_files: true });
      },
      'Review status updated.',
    );
    if (!response) return;
    setValidation(response);
    if (reviewKind === 'targets') {
      const firstApproved = response.targets.rows.find((row) => row.approved)?.id;
      if (firstApproved) setTargetId(firstApproved);
    }
  }

  async function handleDeleteSelected() {
    const manifest = manifestForKind(reviewKind, { targets, sources, people });
    const ids = Array.from(selectedReviewIds);
    if (ids.length === 0) {
      appendLog('Select one or more rows to delete.', 'error');
      return;
    }
    const confirmed = window.confirm(
      `Delete ${ids.length} selected row${ids.length === 1 ? '' : 's'} from the ${reviewKind} manifest? Cached image files are kept on disk.`,
    );
    if (!confirmed) return;
    const response = await runAction(
      `Deleting ${ids.length} selected ${reviewKind} row${ids.length === 1 ? '' : 's'}.`,
      async () => {
        await deleteReviewRows({ manifest, kind: reviewKind, row_ids: ids });
        return validateManifests({ targets, sources, people, require_files: true });
      },
      'Rows deleted.',
    );
    if (!response) return;
    setValidation(response);
    setSelectedReviewIds(new Set());
    if (reviewKind === 'targets' && ids.includes(targetId)) {
      setTargetId(response.targets.rows.find((candidate) => candidate.approved)?.id ?? '');
    }
  }

  function handlePickReview(row: ManifestRow) {
    if (row.kind === 'targets') {
      setTargetId(row.id);
      appendLog(`Target portrait set to ${row.label}${row.approved ? '' : ' (pending)'}.`, 'ok');
      return;
    }
    setViewerOutput({
      id: row.id,
      target_id: row.label,
      still_path: row.file_path ?? row.values.local_path ?? null,
      video_path: null,
      sidecar_path: '',
      sidecar: {},
    });
  }

  function handleTargetSelect(value: string) {
    setTargetId(value);
    const row = allTargets.find((target) => target.id === value);
    appendLog(row ? `Selected target: ${row.label}.` : 'No target selected.', row ? 'ok' : undefined);
  }

  function handleCrawlKindChange(value: CrawlKind) {
    setCrawlKind(value);
    setCrawlManifest(crawlerManifestDefaults[value]);
    setReviewKind(value);
  }

  function handleCrawlPreset(presetId: string) {
    const preset = crawlPresets.find((candidate) => candidate.id === presetId);
    if (!preset) return;
    setCrawlKind(preset.kind);
    setReviewKind(preset.kind);
    setCrawlManifest(preset.manifest);
    setCrawlPagesText(preset.pages.join('\n'));
    setCrawlMaxImages(preset.maxImages);
    setCrawlLabelPrefix(preset.labelPrefix);
    appendLog(`Loaded crawler preset: ${preset.label}.`, 'ok');
  }

  function toggleOutputSelection(id: string) {
    setSelectedOutputIds((current) => {
      const next = new Set(current);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  async function handleDeleteOutputs(all = false) {
    const ids = all ? [] : Array.from(selectedOutputIds);
    const count = all ? outputs.length : ids.length;
    if (count === 0) {
      appendLog(all ? 'No generated outputs to delete.' : 'Select one or more outputs to delete.', 'error');
      return;
    }
    const confirmed = window.confirm(
      all
        ? `Delete all ${count} generated output${count === 1 ? '' : 's'} from ${outputDir}?`
        : `Delete ${count} selected generated output${count === 1 ? '' : 's'} from ${outputDir}?`,
    );
    if (!confirmed) return;

    const response = await runAction(
      all ? 'Deleting all generated outputs.' : `Deleting ${count} selected generated output${count === 1 ? '' : 's'}.`,
      () => deleteOutputs({ output_dir: outputDir, ids, all }),
      'Output deletion finished.',
    );
    if (!response) return;
    response.errors.forEach((error) => appendLog(error, 'error'));
    appendLog(`Deleted ${response.deleted.length} output${response.deleted.length === 1 ? '' : 's'}.`, response.ok ? 'ok' : 'error');
    setSelectedOutputIds(new Set());
    if (viewerOutput && (all || response.deleted.includes(viewerOutput.id))) {
      setViewerOutput(null);
    }
    await refreshOutputs();
  }

  useEffect(() => saveStored('targets', targets), [targets]);
  useEffect(() => saveStored('sources', sources), [sources]);
  useEffect(() => saveStored('people', people), [people]);
  useEffect(() => saveStored('outputDir', outputDir), [outputDir]);
  useEffect(() => saveStored('crawlManifest', crawlManifest), [crawlManifest]);

  // The review grid shows a different row set per kind; drop any stale selection.
  useEffect(() => setSelectedReviewIds(new Set()), [reviewKind]);

  useEffect(() => {
    listOutputs(outputDir)
      .then((response) => {
        setOutputs(response.items);
        setSelectedOutput(response.items[0] ?? null);
      })
      .catch(() => undefined);
    validateManifests({ targets, sources, people, require_files: false })
      .then((response) => {
        setValidation(response);
        const firstApproved = response.targets.rows.find((row) => row.approved)?.id;
        if (firstApproved) setTargetId(firstApproved);
      })
      .catch(() => undefined);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>desaparecidos.uy</h1>
          <p>Stage 1 local workspace: Están en todas partes</p>
        </div>
        <div className="topbar-actions">
          <button className="icon-button" onClick={() => setShowUtilities(true)} title="Utilities">
            <Settings size={16} />
          </button>
          <div className={`run-status ${busy || crawling ? 'busy' : ''} ${validation?.ok ? 'ok' : ''}`}>
            {(busy || crawling) && <RefreshCw size={13} className="spin" />}
            <span>{statusLabel}</span>
          </div>
        </div>
      </header>

      <aside className="workflow">
        <WorkflowItem
          icon={<FileCheck2 />}
          title="Manifests"
          active={activeSection === 'manifests'}
          detail={`${validation?.targets.row_count ?? 0} targets`}
          onSelect={() => selectWorkflow('manifests')}
        />
        <WorkflowItem
          icon={<LayoutGrid />}
          title="Review images"
          active={activeSection === 'review'}
          detail={`${approvedSources.length} approved places`}
          onSelect={() => selectWorkflow('review')}
        />
        <WorkflowItem
          icon={<Play />}
          title="Generate"
          active={activeSection === 'generate'}
          detail={`block ${fragmentSize}px`}
          onSelect={() => selectWorkflow('generate')}
        />
        <WorkflowItem
          icon={<ImageIcon />}
          title="Outputs"
          active={activeSection === 'outputs'}
          detail={`${outputs.length} sidecars`}
          onSelect={() => selectWorkflow('outputs')}
        />
      </aside>

      <main className="workspace">
        <section className="stage-panel target-panel" id="section-generate">
          <div className="panel-title">
            <span>Target portrait</span>
            <select
              value={activeTarget?.id ?? ''}
              onChange={(event) => handleTargetSelect(event.target.value)}
              disabled={allTargets.length === 0}
            >
              {allTargets.length === 0 && <option value="">No targets</option>}
              {allTargets.map((row) => (
                <option key={row.id} value={row.id}>
                  {row.approved ? row.label : `${row.label} (pending)`}
                </option>
              ))}
            </select>
          </div>
          <Preview row={activeTarget} />
          <div className="metadata-strip">
            <span>
              {activeTarget
                ? `${activeTarget.label}${activeTarget.approved ? '' : ' pending'}`
                : 'No target selected'}
            </span>
            <span>{activeTarget?.values.source_page || 'source page pending'}</span>
          </div>
        </section>

        <section className="stage-panel source-panel" id="section-review">
          <div className="panel-title">
            <span>Review images</span>
            <div className="panel-actions">
              <div className="segmented">
                <button
                  className={reviewKind === 'targets' ? 'selected' : ''}
                  onClick={() => setReviewKind('targets')}
                  disabled={busy}
                >
                  Targets
                </button>
                <button
                  className={reviewKind === 'places' ? 'selected' : ''}
                  onClick={() => setReviewKind('places')}
                  disabled={busy}
                >
                  Places
                </button>
                <button
                  className={reviewKind === 'people' ? 'selected' : ''}
                  onClick={() => setReviewKind('people')}
                  disabled={busy}
                >
                  People
                </button>
              </div>
              <button
                className="text-button"
                onClick={() => setSelectedReviewIds(new Set(reviewRows.map((row) => row.id)))}
                disabled={busy || reviewRows.length === 0}
                title={`Select all ${reviewKind}`}
              >
                <CheckSquare size={14} /> Select all
              </button>
              <button
                className="text-button"
                onClick={() => setSelectedReviewIds(new Set())}
                disabled={busy || selectedReviewCount === 0}
                title="Clear selection"
              >
                <Square size={14} /> Select none
              </button>
              <button
                className="text-button"
                onClick={() => void handleApproveSelected()}
                disabled={busy || selectedReviewCount === 0}
                title="Approve selected rows"
              >
                <CheckCircle2 size={14} /> Approve selected
              </button>
              <button
                className="text-button danger"
                onClick={() => void handleDeleteSelected()}
                disabled={busy || selectedReviewCount === 0}
                title="Delete selected rows"
              >
                <Trash2 size={14} /> Delete selected
              </button>
            </div>
          </div>
          <div className="review-grid">
            {reviewRows.length === 0 && <EmptyState text="Validate or crawl manifests to review image rows." />}
            {reviewRows.map((row) => (
              <ReviewCard
                key={`${row.kind}-${row.id}`}
                row={row}
                busy={busy}
                selected={row.kind === 'targets' && row.id === targetId}
                checked={selectedReviewIds.has(row.id)}
                onToggleSelect={toggleReviewSelection}
                onReview={handleReviewStatus}
                onPick={handlePickReview}
                onDelete={handleDeleteReview}
              />
            ))}
          </div>
        </section>

        <section className="stage-panel outputs-panel" id="section-outputs">
          <div className="panel-title">
            <span>Generated outputs</span>
            <div className="panel-actions">
              <button
                className="text-button"
                onClick={() => selectedOutput && setViewerOutput(selectedOutput)}
                disabled={busy || !selectedOutput}
              >
                <Maximize2 size={14} /> View
              </button>
              <button
                className="text-button"
                onClick={() => setSelectedOutputIds(new Set(outputs.map((item) => item.id)))}
                disabled={busy || outputs.length === 0}
              >
                <CheckSquare size={14} /> Select all
              </button>
              <button
                className="text-button"
                onClick={() => setSelectedOutputIds(new Set())}
                disabled={busy || selectedOutputCount === 0}
              >
                <Square size={14} /> Clear
              </button>
              <button
                className="text-button danger"
                onClick={() => void handleDeleteOutputs(false)}
                disabled={busy || selectedOutputCount === 0}
              >
                <Trash2 size={14} /> Delete selected
              </button>
              <button
                className="icon-button danger"
                onClick={() => void handleDeleteOutputs(true)}
                disabled={busy || outputs.length === 0}
                title="Delete all outputs"
              >
                <Trash2 size={16} />
              </button>
              <button className="icon-button" onClick={() => void refreshOutputs()} disabled={busy} title="Refresh outputs">
                <RefreshCw size={16} />
              </button>
            </div>
          </div>
          <div className="output-list">
            {outputs.length === 0 && <EmptyState text="No generated outputs found." />}
            {outputs.map((item) => (
              <article
                className={`output-thumb ${selectedOutput?.id === item.id ? 'selected' : ''} ${selectedOutputIds.has(item.id) ? 'checked' : ''}`}
                key={item.id}
              >
                <label className="output-select" title="Select output">
                  <input
                    type="checkbox"
                    checked={selectedOutputIds.has(item.id)}
                    onChange={() => toggleOutputSelection(item.id)}
                  />
                  {selectedOutputIds.has(item.id) ? <CheckSquare size={16} /> : <Square size={16} />}
                </label>
                <button
                  className="output-open"
                  onClick={() => {
                    setSelectedOutput(item);
                    setViewerOutput(item);
                  }}
                >
                  {item.still_path ? <img src={fileUrl(item.still_path)} alt="" /> : <ImageIcon size={24} />}
                  <span>{item.video_path ? <Video size={12} /> : <ImageIcon size={12} />}{item.target_id || item.id}</span>
                </button>
              </article>
            ))}
          </div>
        </section>

        <section className="stage-panel log-panel">
          <div className="panel-title">
            <span>Progress log</span>
          </div>
          <div className="log-list">
            {log.map((entry, index) => (
              <div className={`log-entry ${entry.tone ?? ''}`} key={`${entry.at}-${index}`}>
                <time>{entry.at}</time>
                <span>{entry.text}</span>
              </div>
            ))}
          </div>
        </section>
      </main>

      <aside className="inspector">
        <section id="controls-manifests">
          <div className="section-heading-row">
            <h2>Manifests</h2>
            <button className="icon-button" onClick={() => setShowUtilities(true)} title="Utilities">
              <Settings size={15} />
            </button>
          </div>
          <label>
            Targets
            <input value={targets} onChange={(event) => setTargets(event.target.value)} />
          </label>
          <label>
            Places
            <input value={sources} onChange={(event) => setSources(event.target.value)} />
          </label>
          <label>
            People
            <input value={people} onChange={(event) => setPeople(event.target.value)} />
          </label>
          <div className="button-row">
            <button onClick={() => void handleValidate(false)} disabled={busy}>
              <FileCheck2 size={16} /> Validate
            </button>
            <button onClick={() => void handleValidate(true)} disabled={busy}>
              <CheckCircle2 size={16} /> Check files
            </button>
          </div>
        </section>

        <section className="crawler-box">
          <h2>Crawler</h2>
          <label>
            Starting page
            <select value="" onChange={(event) => handleCrawlPreset(event.target.value)}>
              <option value="">Choose source</option>
              {crawlPresets.map((preset) => (
                <option key={preset.id} value={preset.id}>
                  {preset.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Kind
            <select value={crawlKind} onChange={(event) => handleCrawlKindChange(event.target.value as CrawlKind)}>
              <option value="places">Places</option>
              <option value="people">People</option>
            </select>
          </label>
          <label>
            Page URLs
            <textarea
              value={crawlPagesText}
              onChange={(event) => setCrawlPagesText(event.target.value)}
              rows={4}
              placeholder="https://..."
            />
          </label>
          <label>
            Manifest
            <input value={crawlManifest} onChange={(event) => setCrawlManifest(event.target.value)} />
          </label>
          <div className="form-grid">
            <label>
              Per page
              <input
                type="number"
                min={1}
                max={50}
                value={crawlMaxImages}
                onChange={(event) => setCrawlMaxImages(Number(event.target.value))}
              />
            </label>
            <label>
              Depth
              <input
                type="number"
                min={0}
                max={4}
                value={crawlDepth}
                onChange={(event) => setCrawlDepth(Number(event.target.value))}
              />
            </label>
            <label>
              Max pages
              <input
                type="number"
                min={1}
                max={500}
                value={crawlMaxPages}
                onChange={(event) => setCrawlMaxPages(Number(event.target.value))}
              />
            </label>
            <label>
              Total images
              <input
                type="number"
                min={1}
                max={1000}
                value={crawlMaxTotal}
                onChange={(event) => setCrawlMaxTotal(Number(event.target.value))}
              />
            </label>
          </div>
          <label>
            Label prefix
            <input value={crawlLabelPrefix} onChange={(event) => setCrawlLabelPrefix(event.target.value)} />
          </label>
          <div className="toggle-row">
            <label className="checkbox">
              <input
                type="checkbox"
                checked={crawlCrossDomain}
                onChange={(event) => setCrawlCrossDomain(event.target.checked)}
              />
              Follow other domains
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={crawlUseCv}
                onChange={(event) => setCrawlUseCv(event.target.checked)}
              />
              CV filter
            </label>
          </div>
          <button onClick={() => void handleCrawl()} disabled={crawling}>
            {crawling ? <RefreshCw size={16} className="spin" /> : <Globe2 size={16} />} Crawl pages
          </button>
        </section>

        <section id="controls-generate">
          <h2>Generation</h2>
          <label>
            Output directory
            <input value={outputDir} onChange={(event) => setOutputDir(event.target.value)} />
          </label>
          <label className="slider-label">
            <span>Block size: {fragmentSize}px</span>
            <input
              type="range"
              min={8}
              max={128}
              step={4}
              value={fragmentSize}
              onChange={(event) => setFragmentSize(Number(event.target.value))}
            />
          </label>
          <label className="slider-label">
            <span>Max tiles per source: {maxContribution === 0 ? 'unlimited' : maxContribution}</span>
            <input
              type="range"
              min={0}
              max={320}
              step={1}
              value={maxContribution}
              onChange={(event) => setMaxContribution(Number(event.target.value))}
            />
          </label>
          <div className="form-grid">
            <label>
              Seed
              <input type="number" value={seed} onChange={(event) => setSeed(Number(event.target.value))} />
            </label>
            <label>
              Reuse limit
              <input type="number" min={1} value={reuseLimit} onChange={(event) => setReuseLimit(Number(event.target.value))} />
            </label>
            <label>
              Width
              <input type="number" min={120} value={outputWidth} onChange={(event) => setOutputWidth(Number(event.target.value))} />
            </label>
          </div>
          <div className="button-row stacked">
            <button className="primary" onClick={() => void handleGenerate(false)} disabled={busy}>
              <Play size={16} /> Generate still
            </button>
            <button onClick={() => void handleGenerate(true)} disabled={busy}>
              <Video size={16} /> Generate video
            </button>
          </div>
        </section>

        <section className="status-box">
          <h2>Validation</h2>
          <ValidationSummary validation={validation} />
        </section>

        <section className="sidecar-box">
          <h2>Sidecar</h2>
          <pre>{selectedOutput ? JSON.stringify(selectedOutput.sidecar, null, 2) : 'No output selected.'}</pre>
        </section>
      </aside>

      {viewerOutput && <OutputViewer item={viewerOutput} onClose={() => setViewerOutput(null)} />}
      {showUtilities && (
        <UtilitiesModal
          busy={busy}
          onCreateDemo={() => void handleCreateDemoFixtures()}
          onClose={() => setShowUtilities(false)}
        />
      )}
    </div>
  );
}

function WorkflowItem({
  icon,
  title,
  detail,
  active,
  onSelect,
}: {
  icon: ReactNode;
  title: string;
  detail: string;
  active?: boolean;
  onSelect: () => void;
}) {
  return (
    <button type="button" className={`workflow-item ${active ? 'active' : ''}`} onClick={onSelect}>
      <div className="workflow-icon">{icon}</div>
      <div>
        <strong>{title}</strong>
        <span>{detail}</span>
      </div>
    </button>
  );
}

function ReviewCard({
  row,
  busy,
  selected,
  checked,
  onToggleSelect,
  onReview,
  onPick,
  onDelete,
}: {
  row: ManifestRow;
  busy: boolean;
  selected?: boolean;
  checked: boolean;
  onToggleSelect: (id: string) => void;
  onReview: (row: ManifestRow, status: ReviewStatus) => void;
  onPick: (row: ManifestRow) => void;
  onDelete: (row: ManifestRow) => void;
}) {
  const status = row.values.review_status || 'pending';
  const pickTitle = row.kind === 'targets' ? 'Use as target portrait' : 'View image';
  return (
    <article className={`review-card ${status} ${selected ? 'selected' : ''} ${checked ? 'checked' : ''}`} key={row.id}>
      <label className="review-select" title="Select row">
        <input
          type="checkbox"
          checked={checked}
          onChange={() => onToggleSelect(row.id)}
        />
        {checked ? <CheckSquare size={15} /> : <Square size={15} />}
      </label>
      <button
        type="button"
        className="review-delete"
        onClick={() => onDelete(row)}
        disabled={busy}
        title="Delete from manifest"
      >
        <Trash2 size={14} />
      </button>
      <button type="button" className="review-pick" onClick={() => onPick(row)} title={pickTitle}>
        <Preview row={row} compact />
      </button>
      <div className="review-card-body">
        <div>
          <strong>{row.label}</strong>
          <span>{row.values.source_page || row.values.source_url}</span>
        </div>
        <StatusPill status={status} />
      </div>
      <div className="review-actions">
        <button onClick={() => onReview(row, 'approved')} disabled={busy || row.approved}>
          <Check size={14} /> Approve
        </button>
        <button onClick={() => onReview(row, 'rejected')} disabled={busy || status === 'rejected'}>
          <Ban size={14} /> Reject
        </button>
        <button onClick={() => onReview(row, 'pending')} disabled={busy || status === 'pending'}>
          <Eye size={14} /> Pending
        </button>
      </div>
    </article>
  );
}

function StatusPill({ status }: { status: string }) {
  return <span className={`status-pill ${status}`}>{status}</span>;
}

function Preview({ row, compact = false }: { row?: ManifestRow; compact?: boolean }) {
  const path = row?.file_path ?? row?.values.local_path;
  if (!path) {
    return <div className={`preview placeholder ${compact ? 'compact' : ''}`} />;
  }
  return (
    <div className={`preview ${compact ? 'compact' : ''}`}>
      <img src={fileUrl(path)} alt="" />
    </div>
  );
}

function OutputViewer({ item, onClose }: { item: OutputItem; onClose: () => void }) {
  const stillUrl = item.still_path ? fileUrl(item.still_path) : null;
  const videoUrl = item.video_path ? fileUrl(item.video_path) : null;
  return (
    <div className="viewer-backdrop" role="dialog" aria-modal="true">
      <div className="viewer">
        <div className="viewer-title">
          <div>
            <strong>{item.target_id || item.id}</strong>
            <span>{item.id}</span>
          </div>
          <button className="icon-button" onClick={onClose} title="Close">
            <X size={18} />
          </button>
        </div>
        <div className="viewer-media">
          {videoUrl ? (
            <video src={videoUrl} poster={stillUrl ?? undefined} controls />
          ) : stillUrl ? (
            <img src={stillUrl} alt="" />
          ) : (
            <EmptyState text="No media file found for this output." />
          )}
        </div>
        <div className="viewer-actions">
          {stillUrl && <a className="link-button" href={stillUrl} target="_blank" rel="noreferrer">Open still</a>}
          {videoUrl && <a className="link-button" href={videoUrl} target="_blank" rel="noreferrer">Open video</a>}
        </div>
      </div>
    </div>
  );
}

function UtilitiesModal({
  busy,
  onCreateDemo,
  onClose,
}: {
  busy: boolean;
  onCreateDemo: () => void;
  onClose: () => void;
}) {
  return (
    <div className="viewer-backdrop" role="dialog" aria-modal="true">
      <div className="viewer utilities-modal">
        <div className="viewer-title">
          <div>
            <strong>Utilities</strong>
            <span>Secondary local tools</span>
          </div>
          <button className="icon-button" onClick={onClose} title="Close">
            <X size={18} />
          </button>
        </div>
        <div className="utilities-body">
          <section>
            <h3>Demo fixtures</h3>
            <p>Synthetic local inputs stored under ignored paths.</p>
            <button onClick={onCreateDemo} disabled={busy}>
              <ImageIcon size={16} /> Create demo fixtures
            </button>
          </section>
        </div>
      </div>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return <div className="empty-state">{text}</div>;
}

function ValidationSummary({ validation }: { validation: ValidateResponse | null }) {
  if (!validation) {
    return <p>No validation run yet.</p>;
  }
  const errors = [...validation.targets.errors, ...validation.sources.errors, ...validation.people.errors];
  const warnings = [...validation.targets.warnings, ...validation.sources.warnings, ...validation.people.warnings];
  return (
    <div className="validation-summary">
      <p>
        {validation.targets.approved_count} approved targets, {validation.sources.approved_count} approved places, {validation.people.approved_count} approved people.
      </p>
      {errors.map((error) => (
        <div className="validation-line error" key={error}>
          {error}
        </div>
      ))}
      {warnings.map((warning) => (
        <div className="validation-line" key={warning}>
          {warning}
        </div>
      ))}
      {errors.length === 0 && <div className="validation-line ok">No blocking validation errors.</div>}
    </div>
  );
}
