import {
  Ban,
  Check,
  CheckCircle2,
  CheckSquare,
  Download,
  Eye,
  FileCheck2,
  Globe2,
  Image as ImageIcon,
  LayoutGrid,
  Maximize2,
  Play,
  RefreshCw,
  Square,
  Trash2,
  Video,
  X,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import {
  ManifestRow,
  OutputItem,
  ValidateResponse,
  crawlPages,
  createDemoFixtures,
  deleteOutputs,
  downloadManifest,
  fileUrl,
  generateStage1,
  listOutputs,
  updateReviewStatus,
  validateManifests,
} from './api';

type LogEntry = {
  at: string;
  text: string;
  tone?: 'ok' | 'error';
};

type SectionId = 'manifests' | 'review' | 'generate' | 'outputs';
type ReviewKind = 'targets' | 'places';
type ReviewStatus = 'approved' | 'pending' | 'rejected';
type CrawlPreset = {
  id: string;
  label: string;
  kind: ReviewKind;
  manifest: string;
  pages: string[];
  maxImages: number;
  labelPrefix: string;
};

const defaultPaths = {
  targets: 'data/manifests/targets.csv',
  sources: 'data/manifests/places.csv',
  outputDir: 'outputs/stage1',
};

const crawlerManifestDefaults: Record<ReviewKind, string> = {
  targets: 'data/manifests/crawled-targets.csv',
  places: 'data/manifests/crawled-places.csv',
};

const crawlPresets: CrawlPreset[] = [
  {
    id: 'cdf-home',
    label: 'CdF Montevideo',
    kind: 'places',
    manifest: crawlerManifestDefaults.places,
    pages: ['https://cdf.montevideo.gub.uy/'],
    maxImages: 12,
    labelPrefix: 'CdF',
  },
  {
    id: 'cdf-exhibitions',
    label: 'CdF exhibitions',
    kind: 'places',
    manifest: crawlerManifestDefaults.places,
    pages: ['https://cdf.montevideo.gub.uy/exposiciones'],
    maxImages: 18,
    labelPrefix: 'CdF exhibition',
  },
  {
    id: 'mume',
    label: 'MUME',
    kind: 'places',
    manifest: crawlerManifestDefaults.places,
    pages: ['https://mume.montevideo.gub.uy/'],
    maxImages: 12,
    labelPrefix: 'MUME',
  },
  {
    id: 'sitios-memoria',
    label: 'Sitios de Memoria',
    kind: 'places',
    manifest: crawlerManifestDefaults.places,
    pages: ['https://sitiosdememoria.uy/'],
    maxImages: 12,
    labelPrefix: 'Sitio memoria',
  },
  {
    id: 'commons-streets',
    label: 'Commons streets',
    kind: 'places',
    manifest: crawlerManifestDefaults.places,
    pages: ['https://commons.wikimedia.org/wiki/Category:Streets_in_Montevideo'],
    maxImages: 24,
    labelPrefix: 'Montevideo street',
  },
  {
    id: 'commons-buildings',
    label: 'Commons buildings',
    kind: 'places',
    manifest: crawlerManifestDefaults.places,
    pages: ['https://commons.wikimedia.org/wiki/Category:Buildings_in_Montevideo'],
    maxImages: 24,
    labelPrefix: 'Montevideo building',
  },
];

export function App() {
  const [targets, setTargets] = useState(defaultPaths.targets);
  const [sources, setSources] = useState(defaultPaths.sources);
  const [outputDir, setOutputDir] = useState(defaultPaths.outputDir);
  const [seed, setSeed] = useState(17);
  const [fragmentSize, setFragmentSize] = useState(24);
  const [reuseLimit, setReuseLimit] = useState(8);
  const [outputWidth, setOutputWidth] = useState(720);
  const [targetId, setTargetId] = useState('');
  const [validation, setValidation] = useState<ValidateResponse | null>(null);
  const [outputs, setOutputs] = useState<OutputItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [selectedOutput, setSelectedOutput] = useState<OutputItem | null>(null);
  const [selectedOutputIds, setSelectedOutputIds] = useState<Set<string>>(new Set());
  const [viewerOutput, setViewerOutput] = useState<OutputItem | null>(null);
  const [activeSection, setActiveSection] = useState<SectionId>('manifests');
  const [reviewKind, setReviewKind] = useState<ReviewKind>('places');
  const [crawlKind, setCrawlKind] = useState<ReviewKind>('places');
  const [crawlPagesText, setCrawlPagesText] = useState('');
  const [crawlManifest, setCrawlManifest] = useState(crawlerManifestDefaults.places);
  const [crawlMaxImages, setCrawlMaxImages] = useState(12);
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

  const approvedTargets = validation?.targets.rows.filter((row) => row.approved) ?? [];
  const approvedSources = validation?.sources.rows.filter((row) => row.approved) ?? [];
  const reviewRows = reviewKind === 'targets'
    ? validation?.targets.rows ?? []
    : validation?.sources.rows ?? [];
  const activeTarget = approvedTargets.find((row) => row.id === targetId) ?? approvedTargets[0];
  const selectedOutputCount = selectedOutputIds.size;

  const statusLabel = useMemo(() => {
    if (busy) return 'running';
    if (!validation) return 'not validated';
    return validation.ok ? 'validated' : 'needs attention';
  }, [busy, validation]);

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
      const message = error instanceof Error ? error.message : String(error);
      appendLog(message, 'error');
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
      () => validateManifests({ targets, sources, require_files: requireFiles }),
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
  }

  async function handleDownload(kind: ReviewKind) {
    const manifest = kind === 'targets' ? targets : sources;
    await runAction(
      `Downloading ${kind} manifest URLs.`,
      () => downloadManifest({ manifest, kind, output_root: 'data/raw' }),
      `${kind} download pass finished.`,
    );
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
        const checked = await validateManifests({
          targets,
          sources,
          require_files: true,
        });
        setValidation(checked);
        const firstApprovedTarget = checked.targets.rows.find((row) => row.approved)?.id ?? '';
        const selectedTargetId = activeTarget?.id || firstApprovedTarget;
        if (firstApprovedTarget && !activeTarget) {
          setTargetId(firstApprovedTarget);
        }
        if (checked.targets.approved_count === 0 || checked.sources.approved_count === 0) {
          throw new Error(
            'No approved target/source rows. Approve rows in Review images, or use Create demo fixtures.',
          );
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
    const response = await runAction(
      `Crawling ${pages.length} page${pages.length === 1 ? '' : 's'} for ${crawlKind}.`,
      () => crawlPages({
        pages,
        kind: crawlKind,
        manifest: crawlManifest,
        output_root: 'data/raw/crawl',
        max_images_per_page: crawlMaxImages,
        label_prefix: crawlLabelPrefix,
      }),
      'Crawler finished.',
    );
    if (!response) return;
    if (crawlKind === 'targets') {
      setTargets(response.manifest);
    } else {
      setSources(response.manifest);
    }
    setReviewKind(crawlKind);
    setActiveSection('review');
    const checked = await validateManifests({
      targets: crawlKind === 'targets' ? response.manifest : targets,
      sources: crawlKind === 'places' ? response.manifest : sources,
      require_files: true,
    });
    setValidation(checked);
    const saved = response.items.filter((item) => item.ok).length;
    appendLog(`Crawler saved ${saved} image${saved === 1 ? '' : 's'} as pending review.`, saved ? 'ok' : 'error');
    response.errors.forEach((error) => appendLog(error, 'error'));
  }

  async function handleReviewStatus(row: ManifestRow, status: ReviewStatus) {
    const manifest = row.kind === 'targets' ? targets : sources;
    const response = await runAction(
      `${status === 'approved' ? 'Approving' : status === 'rejected' ? 'Rejecting' : 'Resetting'} ${row.label}.`,
      async () => {
        await updateReviewStatus({
          manifest,
          kind: row.kind,
          row_id: row.id,
          review_status: status,
        });
        return validateManifests({ targets, sources, require_files: true });
      },
      'Review status updated.',
    );
    if (!response) return;
    setValidation(response);
    if (row.kind === 'targets' && status === 'approved') {
      setTargetId(row.id);
    }
  }

  function handleTargetSelect(value: string) {
    setTargetId(value);
    const row = approvedTargets.find((target) => target.id === value);
    appendLog(row ? `Selected target: ${row.label}.` : 'No approved target selected.', row ? 'ok' : undefined);
  }

  function handleCrawlKindChange(value: ReviewKind) {
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

  useEffect(() => {
    listOutputs(defaultPaths.outputDir)
      .then((response) => {
        setOutputs(response.items);
        setSelectedOutput(response.items[0] ?? null);
      })
      .catch(() => undefined);
  }, []);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>desaparecidos.uy</h1>
          <p>Stage 1 local workspace: Estan en todas partes</p>
        </div>
        <div className={`run-status ${validation?.ok ? 'ok' : ''}`}>
          <span>{statusLabel}</span>
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
          detail={`${approvedSources.length} approved sources`}
          onSelect={() => selectWorkflow('review')}
        />
        <WorkflowItem
          icon={<Play />}
          title="Generate"
          active={activeSection === 'generate'}
          detail={`seed ${seed}`}
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
              disabled={approvedTargets.length === 0}
            >
              {approvedTargets.length === 0 && <option value="">No approved target</option>}
              {approvedTargets.map((row) => (
                <option key={row.id} value={row.id}>
                  {row.label}
                </option>
              ))}
            </select>
          </div>
          <Preview row={activeTarget} />
          <div className="metadata-strip">
            <span>{activeTarget?.label ?? 'No approved target'}</span>
            <span>{activeTarget?.values.source_page || 'source page pending'}</span>
          </div>
        </section>

        <section className="stage-panel source-panel" id="section-review">
          <div className="panel-title">
            <span>Review images</span>
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
            </div>
          </div>
          <div className="review-grid">
            {reviewRows.length === 0 && <EmptyState text="Validate or crawl manifests to review image rows." />}
            {reviewRows.map((row) => (
              <ReviewCard
                key={`${row.kind}-${row.id}`}
                row={row}
                busy={busy}
                onReview={handleReviewStatus}
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
          <h2>Manifests</h2>
          <label>
            Targets
            <input value={targets} onChange={(event) => setTargets(event.target.value)} />
          </label>
          <label>
            Places
            <input value={sources} onChange={(event) => setSources(event.target.value)} />
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

        <section className="demo-box">
          <h2>Demo workspace</h2>
          <p>Synthetic local inputs. Ignored by git.</p>
          <button onClick={() => void handleCreateDemoFixtures()} disabled={busy}>
            <ImageIcon size={16} /> Create demo fixtures
          </button>
        </section>

        <section>
          <h2>Download</h2>
          <div className="button-row">
            <button onClick={() => void handleDownload('targets')} disabled={busy}>
              <Download size={16} /> Targets
            </button>
            <button onClick={() => void handleDownload('places')} disabled={busy}>
              <Download size={16} /> Sources
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
            <select value={crawlKind} onChange={(event) => handleCrawlKindChange(event.target.value as ReviewKind)}>
              <option value="places">Places</option>
              <option value="targets">Targets</option>
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
              Max images
              <input
                type="number"
                min={1}
                max={50}
                value={crawlMaxImages}
                onChange={(event) => setCrawlMaxImages(Number(event.target.value))}
              />
            </label>
            <label>
              Label prefix
              <input value={crawlLabelPrefix} onChange={(event) => setCrawlLabelPrefix(event.target.value)} />
            </label>
          </div>
          <button onClick={() => void handleCrawl()} disabled={busy}>
            <Globe2 size={16} /> Crawl pages
          </button>
        </section>

        <section id="controls-generate">
          <h2>Generation</h2>
          <label>
            Output directory
            <input value={outputDir} onChange={(event) => setOutputDir(event.target.value)} />
          </label>
          <div className="form-grid">
            <label>
              Seed
              <input type="number" value={seed} onChange={(event) => setSeed(Number(event.target.value))} />
            </label>
            <label>
              Fragment
              <input type="number" min={8} max={128} value={fragmentSize} onChange={(event) => setFragmentSize(Number(event.target.value))} />
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
  onReview,
}: {
  row: ManifestRow;
  busy: boolean;
  onReview: (row: ManifestRow, status: ReviewStatus) => void;
}) {
  const status = row.values.review_status || 'pending';
  return (
    <article className={`review-card ${status}`} key={row.id}>
      <Preview row={row} compact />
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

function EmptyState({ text }: { text: string }) {
  return <div className="empty-state">{text}</div>;
}

function ValidationSummary({ validation }: { validation: ValidateResponse | null }) {
  if (!validation) {
    return <p>No validation run yet.</p>;
  }
  const errors = [...validation.targets.errors, ...validation.sources.errors];
  const warnings = [...validation.targets.warnings, ...validation.sources.warnings];
  return (
    <div className="validation-summary">
      <p>
        {validation.targets.approved_count} approved targets, {validation.sources.approved_count} approved sources.
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
