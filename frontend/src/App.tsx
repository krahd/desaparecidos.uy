import {
  CheckCircle2,
  Download,
  FileCheck2,
  Image as ImageIcon,
  LayoutGrid,
  Play,
  RefreshCw,
  Video,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import {
  ManifestRow,
  OutputItem,
  ValidateResponse,
  createDemoFixtures,
  downloadManifest,
  fileUrl,
  generateStage1,
  listOutputs,
  validateManifests,
} from './api';

type LogEntry = {
  at: string;
  text: string;
  tone?: 'ok' | 'error';
};

const defaultPaths = {
  targets: 'data/manifests/targets.csv',
  sources: 'data/manifests/places.csv',
  outputDir: 'outputs/stage1',
};

export function App() {
  const [targets, setTargets] = useState(defaultPaths.targets);
  const [sources, setSources] = useState(defaultPaths.sources);
  const [outputDir, setOutputDir] = useState(defaultPaths.outputDir);
  const [seed, setSeed] = useState(17);
  const [fragmentSize, setFragmentSize] = useState(24);
  const [reuseLimit, setReuseLimit] = useState(64);
  const [outputWidth, setOutputWidth] = useState(720);
  const [targetId, setTargetId] = useState('');
  const [validation, setValidation] = useState<ValidateResponse | null>(null);
  const [outputs, setOutputs] = useState<OutputItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [selectedOutput, setSelectedOutput] = useState<OutputItem | null>(null);
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
  const activeTarget = approvedTargets.find((row) => row.id === targetId) ?? approvedTargets[0];

  const statusLabel = useMemo(() => {
    if (busy) return 'running';
    if (!validation) return 'not validated';
    return validation.ok ? 'validated' : 'needs attention';
  }, [busy, validation]);

  async function runAction<T>(label: string, action: () => Promise<T>, success: string) {
    setBusy(true);
    appendLog(label);
    try {
      const result = await action();
      appendLog(success, 'ok');
      return result;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      appendLog(message, 'error');
      throw error;
    } finally {
      setBusy(false);
    }
  }

  async function handleValidate(requireFiles = false) {
    const response = await runAction(
      'Validating manifests.',
      () => validateManifests({ targets, sources, require_files: requireFiles }),
      'Validation finished.',
    );
    setValidation(response);
    const firstApproved = response.targets.rows.find((row) => row.approved)?.id ?? '';
    if (firstApproved && !response.targets.rows.some((row) => row.id === targetId)) {
      setTargetId(firstApproved);
    }
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
    setTargets(response.fixtures.targets);
    setSources(response.fixtures.sources);
    setValidation(response.checked);
    setTargetId(response.checked.targets.rows.find((row) => row.approved)?.id ?? '');
  }

  async function handleDownload(kind: 'targets' | 'places') {
    const manifest = kind === 'targets' ? targets : sources;
    await runAction(
      `Downloading ${kind} manifest URLs.`,
      () => downloadManifest({ manifest, kind, output_root: 'data/raw' }),
      `${kind} download pass finished.`,
    );
  }

  async function refreshOutputs() {
    const response = await runAction(
      'Refreshing outputs.',
      () => listOutputs(outputDir),
      'Outputs refreshed.',
    );
    setOutputs(response.items);
    setSelectedOutput(response.items[0] ?? null);
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
        const selectedTargetId = targetId || firstApprovedTarget;
        if (firstApprovedTarget && !targetId) {
          setTargetId(firstApprovedTarget);
        }
        if (checked.targets.approved_count === 0 || checked.sources.approved_count === 0) {
          throw new Error(
            'No approved target/source rows. Add approved rows to the manifests or use Create demo fixtures.',
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
    appendLog(JSON.stringify(response), 'ok');
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
        <WorkflowItem icon={<FileCheck2 />} title="Manifests" active detail={`${validation?.targets.row_count ?? 0} targets`} />
        <WorkflowItem icon={<LayoutGrid />} title="Review images" detail={`${approvedSources.length} approved sources`} />
        <WorkflowItem icon={<Play />} title="Generate" detail={`seed ${seed}`} />
        <WorkflowItem icon={<ImageIcon />} title="Outputs" detail={`${outputs.length} sidecars`} />
      </aside>

      <main className="workspace">
        <section className="stage-panel target-panel">
          <div className="panel-title">
            <span>Target portrait</span>
            <select value={targetId} onChange={(event) => setTargetId(event.target.value)}>
              <option value="">first approved target</option>
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

        <section className="stage-panel source-panel">
          <div className="panel-title">
            <span>Approved place fragments</span>
            <button className="icon-button" onClick={() => void refreshOutputs()} disabled={busy} title="Refresh outputs">
              <RefreshCw size={16} />
            </button>
          </div>
          <div className="source-grid">
            {approvedSources.length === 0 && <EmptyState text="Validate manifests to load approved place rows." />}
            {approvedSources.slice(0, 12).map((row) => (
              <div className="source-tile" key={row.id}>
                <Preview row={row} compact />
                <span>{row.label}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="stage-panel outputs-panel">
          <div className="panel-title">
            <span>Generated outputs</span>
            <button className="text-button" onClick={() => void refreshOutputs()} disabled={busy}>
              Refresh
            </button>
          </div>
          <div className="output-list">
            {outputs.length === 0 && <EmptyState text="No generated outputs found." />}
            {outputs.map((item) => (
              <button
                className={`output-thumb ${selectedOutput?.id === item.id ? 'selected' : ''}`}
                key={item.id}
                onClick={() => setSelectedOutput(item)}
              >
                {item.still_path ? <img src={fileUrl(item.still_path)} alt="" /> : <ImageIcon size={24} />}
                <span>{item.target_id || item.id}</span>
              </button>
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
        <section>
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

        <section>
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
    </div>
  );
}

function WorkflowItem({
  icon,
  title,
  detail,
  active,
}: {
  icon: ReactNode;
  title: string;
  detail: string;
  active?: boolean;
}) {
  return (
    <div className={`workflow-item ${active ? 'active' : ''}`}>
      <div className="workflow-icon">{icon}</div>
      <div>
        <strong>{title}</strong>
        <span>{detail}</span>
      </div>
    </div>
  );
}

function Preview({ row, compact = false }: { row?: ManifestRow; compact?: boolean }) {
  if (!row?.values.local_path) {
    return <div className={`preview placeholder ${compact ? 'compact' : ''}`} />;
  }
  return (
    <div className={`preview ${compact ? 'compact' : ''}`}>
      <img src={fileUrl(row.values.local_path)} alt="" />
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
