import { Check, Compass, Download, Map, Play, RefreshCw, Upload } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import {
  ManifestRow,
  RouteGeometry,
  Traversal,
  acquireTraversal,
  autoTraversal,
  discoverTraversal,
  fileUrl,
  generateTraversal,
  listTraversals,
  reviewTraversalFrames,
} from './api';
import { TraversalMap } from './TraversalMap';

const initialLine: RouteGeometry = {
  type: 'LineString',
  coordinates: [[-56.21, -34.91], [-56.08, -34.83]],
};
const initialRegion: RouteGeometry = {
  type: 'Polygon',
  coordinates: [[[-58.45, -34.95], [-53.1, -34.95], [-53.1, -30.1], [-58.45, -30.1], [-58.45, -34.95]]],
};

export function SeguimosBuscando({
  targets,
  targetManifest,
  outputDir,
  onGenerated,
}: {
  targets: ManifestRow[];
  targetManifest: string;
  outputDir: string;
  onGenerated: (sidecarPath?: string) => Promise<void>;
}) {
  const [items, setItems] = useState<Traversal[]>([]);
  const [active, setActive] = useState<Traversal | null>(null);
  const [mode, setMode] = useState<'manual' | 'import' | 'autonomous'>('manual');
  const [scope, setScope] = useState<'drawn' | 'uruguay'>('uruguay');
  const [geometry, setGeometry] = useState<RouteGeometry>(initialLine);
  const [name, setName] = useState('Uruguay traversal');
  const [duration, setDuration] = useState(60);
  const [maxFrames, setMaxFrames] = useState(120);
  const [regions, setRegions] = useState(4);
  const [ruralShare, setRuralShare] = useState(25);
  const [autoApprove, setAutoApprove] = useState(true);
  const [importContent, setImportContent] = useState('');
  const [importFormat, setImportFormat] = useState<'geojson' | 'gpx'>('geojson');
  const [selectedFrames, setSelectedFrames] = useState<Set<string>>(new Set());
  const [targetMode, setTargetMode] = useState<'single' | 'sequence'>('single');
  const [targetIds, setTargetIds] = useState<string[]>([]);
  const [composition, setComposition] = useState<'overlay' | 'alternate' | 'split'>('overlay');
  const [fps, setFps] = useState(24);
  const [outputWidth, setOutputWidth] = useState(1920);
  const [fragmentSize, setFragmentSize] = useState(24);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('Mapillary discovery requires MAPILLARY_ACCESS_TOKEN in the backend environment.');

  const approvedTargets = useMemo(() => targets.filter((target) => target.approved), [targets]);
  const acquiredFrames = active?.frames.filter((frame) => frame.local_path) ?? [];

  async function refresh(preferredId?: string) {
    const response = await listTraversals();
    setItems(response.items);
    const selected = response.items.find((item) => item.id === (preferredId ?? active?.id)) ?? response.items[0] ?? null;
    setActive(selected);
  }

  useEffect(() => { void refresh(); }, []); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    setGeometry(mode === 'autonomous' ? initialRegion : initialLine);
  }, [mode]);
  useEffect(() => {
    if (targetIds.length === 0 && approvedTargets[0]) setTargetIds([approvedTargets[0].id]);
  }, [approvedTargets, targetIds.length]);

  async function run(label: string, action: () => Promise<void>) {
    setBusy(true);
    setMessage(label);
    try {
      await action();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  const nationalScope = mode === 'autonomous' && scope === 'uruguay';

  function validGeometry(): boolean {
    const coordinates = geometry.coordinates;
    if (mode === 'autonomous') {
      return geometry.type === 'Polygon' && (coordinates as number[][][])[0].length >= 4;
    }
    return geometry.type === 'Polygon'
      ? (coordinates as number[][][])[0].length >= 4
      : (coordinates as number[][]).length >= 2;
  }

  function describeWalks(traversal: Traversal): string {
    if (!traversal.walks?.length) return '';
    const places = traversal.places?.map((place) => place.name).join(', ');
    return ` across ${traversal.walks.length} coherent walks${places ? ` (${places})` : ''}`;
  }

  async function discover() {
    await run('Discovering Mapillary sequences.', async () => {
      if (!nationalScope && mode !== 'import' && !validGeometry()) throw new Error('Add at least two route points or a three-point region.');
      if (mode === 'import' && !importContent.trim()) throw new Error('Choose a GeoJSON or GPX route file.');
      const response = await discoverTraversal({
        name,
        mode,
        scope: mode === 'autonomous' ? scope : 'drawn',
        geometry: mode === 'import' || nationalScope ? undefined : geometry,
        import_content: mode === 'import' ? importContent : undefined,
        import_format: mode === 'import' ? importFormat : undefined,
        duration_seconds: duration,
        max_frames: maxFrames,
        regions: mode === 'autonomous' ? regions : undefined,
        rural_probability: nationalScope ? ruralShare / 100 : undefined,
      });
      setActive(response.traversal);
      setItems((current) => [response.traversal, ...current.filter((item) => item.id !== response.traversal.id)]);
      setMessage(`Discovered ${response.traversal.frames.length} ordered frames${describeWalks(response.traversal)}. Acquire them before review.`);
    });
  }

  async function acquire() {
    if (!active) return;
    await run('Acquiring and checking traversal frames.', async () => {
      const response = await acquireTraversal({ traversal_id: active.id, max_frames: maxFrames, auto_approve: autoApprove });
      setActive(response.traversal);
      await refresh(response.traversal.id);
      const approved = response.traversal.acquisition?.auto_approved ?? 0;
      setMessage(autoApprove
        ? `Acquired ${response.traversal.acquisition?.acquired ?? 0} frames; ${approved} passed the CV gate and were auto-approved. Review remains open.`
        : `Acquired ${response.traversal.acquisition?.acquired ?? 0} frames. Manual approval is still required.`);
    });
  }

  async function autoRun() {
    await run('Searching Uruguay, acquiring frames, and rendering. This can take several minutes.', async () => {
      if (!targetIds.length) throw new Error('Select at least one approved target.');
      const response = await autoTraversal({
        duration_seconds: duration,
        regions,
        max_frames: maxFrames,
        rural_probability: ruralShare / 100,
        targets: targetManifest,
        output_dir: outputDir,
        target_ids: targetIds,
        target_mode: targetMode,
        composition,
        fps,
        fragment_size: fragmentSize,
        output_width: outputWidth,
      });
      await refresh(response.traversal.id);
      await onGenerated(response.outputs[0]?.sidecar_path);
      setMessage(`Autonomous traversal rendered${describeWalks(response.traversal)}. Frames stay open for review.`);
    });
  }

  async function review(status: 'approved' | 'pending' | 'rejected') {
    if (!active || selectedFrames.size === 0) return;
    await run(`Setting ${selectedFrames.size} frames to ${status}.`, async () => {
      const response = await reviewTraversalFrames({
        traversal_id: active.id,
        frame_ids: [...selectedFrames],
        review_status: status,
      });
      setActive(response.traversal);
      setSelectedFrames(new Set());
      await refresh(response.traversal.id);
      setMessage('Frame review updated.');
    });
  }

  function toggleTarget(id: string) {
    setTargetIds((current) => current.includes(id) ? current.filter((value) => value !== id) : [...current, id]);
  }

  function moveTarget(index: number, offset: number) {
    setTargetIds((current) => {
      const destination = index + offset;
      if (destination < 0 || destination >= current.length) return current;
      const next = current.slice();
      [next[index], next[destination]] = [next[destination], next[index]];
      return next;
    });
  }

  async function generate() {
    if (!active) return;
    await run('Rendering approved traversal and contributing fragments.', async () => {
      const response = await generateTraversal({
        traversal_id: active.id,
        targets: targetManifest,
        output_dir: outputDir,
        target_ids: targetIds,
        target_mode: targetMode,
        composition,
        duration_seconds: duration,
        fps,
        seed: 17,
        fragment_size: fragmentSize,
        output_width: outputWidth,
        reuse_limit: 10000,
        max_contribution_per_source: 0,
      });
      await onGenerated(response.outputs[0]?.sidecar_path);
      setMessage('Traversal video generated.');
    });
  }

  return (
    <>
      <section className="stage-panel traversal-authoring">
        <div className="panel-title">
          <span>Seguimos buscando · route authoring</span>
          <button className="text-button" onClick={() => void refresh()} disabled={busy}><RefreshCw size={14} /> Refresh</button>
        </div>
        <div className="traversal-authoring-grid">
          <div>
            <div className="segmented">
              {(['manual', 'import', 'autonomous'] as const).map((value) => (
                <button key={value} className={mode === value ? 'selected' : ''} onClick={() => setMode(value)}>{value}</button>
              ))}
            </div>
            {mode === 'autonomous' && (
              <div className="segmented">
                {(['uruguay', 'drawn'] as const).map((value) => (
                  <button key={value} className={scope === value ? 'selected' : ''} onClick={() => setScope(value)}>
                    {value === 'uruguay' ? 'all Uruguay' : 'drawn region'}
                  </button>
                ))}
              </div>
            )}
            {nationalScope ? (
              <p className="section-note">
                The walk chooses its own places across Uruguay: localities are sampled by population,
                and a share of the walks searches away from inhabited places.
              </p>
            ) : mode !== 'import' ? (
              <>
                <TraversalMap geometry={geometry} mode={mode} onChange={setGeometry} />
                <button className="text-button" onClick={() => setGeometry({ type: 'LineString', coordinates: [] })}>
                  Clear route
                </button>
              </>
            ) : (
              <label className="route-import">
                <Upload size={18} /> GeoJSON or GPX route
                <input
                  type="file"
                  accept=".geojson,.json,.gpx,application/geo+json,application/gpx+xml"
                  onChange={(event) => {
                    const file = event.target.files?.[0];
                    if (!file) return;
                    setImportFormat(file.name.toLowerCase().endsWith('.gpx') ? 'gpx' : 'geojson');
                    void file.text().then(setImportContent);
                  }}
                />
                <span>{importContent ? `${importFormat.toUpperCase()} loaded` : 'No route loaded'}</span>
              </label>
            )}
          </div>
          <div className="traversal-fields">
            <label>Name<input value={name} onChange={(event) => setName(event.target.value)} /></label>
            <label>Duration (seconds)<input type="number" min={1} max={3600} value={duration} onChange={(event) => setDuration(Number(event.target.value))} /></label>
            <label>Maximum frames<input type="number" min={1} max={600} value={maxFrames} onChange={(event) => setMaxFrames(Number(event.target.value))} /></label>
            {mode === 'autonomous' && (
              <label>Regions<input type="number" min={1} max={12} value={regions} onChange={(event) => setRegions(Number(event.target.value))} /></label>
            )}
            {nationalScope && (
              <label>Rural share (%)<input type="number" min={0} max={100} value={ruralShare} onChange={(event) => setRuralShare(Number(event.target.value))} /></label>
            )}
            <button className="primary" onClick={() => void discover()} disabled={busy}><Map size={16} /> Discover sequences</button>
            <p className="section-note">
              {nationalScope
                ? 'Autonomous Uruguay scope samples one coherent capture sequence per chosen place; walks are joined with direct jump cuts.'
                : 'Click the map to add ordered points. Autonomous mode divides the drawn region into cells and selects one coherent capture sequence per region; walks are joined with direct jump cuts.'}
            </p>
          </div>
        </div>
        <div className="traversal-list">
          <label>Saved traversal
            <select value={active?.id ?? ''} onChange={(event) => setActive(items.find((item) => item.id === event.target.value) ?? null)}>
              <option value="">No traversal selected</option>
              {items.map((item) => <option key={item.id} value={item.id}>{item.name} · {item.frames.length} frames</option>)}
            </select>
          </label>
          <button onClick={() => void acquire()} disabled={busy || !active}><Download size={16} /> Acquire and cache</button>
          <label className="inline-check">
            <input type="checkbox" checked={autoApprove} onChange={(event) => setAutoApprove(event.target.checked)} />
            Auto-approve CV-accepted frames
          </label>
          <span>{message}</span>
        </div>
      </section>

      <section className="stage-panel traversal-review">
        <div className="panel-title">
          <span>Traversal frame review</span>
          <div className="panel-actions">
            <button className="text-button" onClick={() => setSelectedFrames(new Set(acquiredFrames.map((frame) => frame.id)))} disabled={!acquiredFrames.length}>Select all acquired</button>
            <button className="text-button" onClick={() => void review('approved')} disabled={busy || !selectedFrames.size}><Check size={14} /> Approve</button>
            <button className="text-button" onClick={() => void review('rejected')} disabled={busy || !selectedFrames.size}>Reject</button>
          </div>
        </div>
        <div className="traversal-frame-grid">
          {!active && <p className="empty-state">Discover or select a traversal.</p>}
          {active?.frames.map((frame) => (
            <label className={`traversal-frame ${frame.review_status}`} key={frame.id}>
              <input type="checkbox" checked={selectedFrames.has(frame.id)} disabled={!frame.local_path} onChange={() => setSelectedFrames((current) => {
                const next = new Set(current); if (next.has(frame.id)) next.delete(frame.id); else next.add(frame.id); return next;
              })} />
              {frame.local_path ? <img src={fileUrl(frame.local_path)} alt="" /> : <span className="frame-placeholder">metadata only</span>}
              <strong>{frame.ordinal + 1} · {frame.review_status}</strong>
              <span>{frame.cv_label}{frame.place_name ? ` · ${frame.place_name}` : frame.region_index != null ? ` · region ${frame.region_index + 1}` : ''}{frame.sequence_jump ? ' · jump cut' : ''}{frame.review_policy === 'auto-cv-accepted' ? ' · auto' : ''}</span>
            </label>
          ))}
        </div>
      </section>

      <section className="stage-panel traversal-generation">
        <div className="panel-title"><span>Traversal generation</span></div>
        <div className="traversal-generation-grid">
          <div>
            <label>Target mode
              <select value={targetMode} onChange={(event) => setTargetMode(event.target.value as 'single' | 'sequence')}>
                <option value="single">Single target</option><option value="sequence">Ordered target sequence</option>
              </select>
            </label>
            {targetMode === 'single' ? (
              <label>Target
                <select value={targetIds[0] ?? ''} onChange={(event) => setTargetIds(event.target.value ? [event.target.value] : [])}>
                  {approvedTargets.map((target) => <option key={target.id} value={target.id}>{target.label}</option>)}
                </select>
              </label>
            ) : (
              <div className="target-order">
                <strong>Artist-selected order</strong>
                <div className="target-picker">
                  {approvedTargets.map((target) => <button className={targetIds.includes(target.id) ? 'selected' : ''} onClick={() => toggleTarget(target.id)} key={target.id}>{target.label}</button>)}
                </div>
                {targetIds.map((id, index) => <div className="ordered-target" key={id}>
                  <span>{index + 1}. {approvedTargets.find((target) => target.id === id)?.label ?? id}</span>
                  <button onClick={() => moveTarget(index, -1)} disabled={index === 0}>↑</button>
                  <button onClick={() => moveTarget(index, 1)} disabled={index === targetIds.length - 1}>↓</button>
                </div>)}
              </div>
            )}
          </div>
          <div>
            <label>Composition
              <select value={composition} onChange={(event) => setComposition(event.target.value as typeof composition)}>
                <option value="overlay">Traversal overlay</option><option value="alternate">Alternating phases</option><option value="split">Split screen</option>
              </select>
            </label>
            <label>Frames per second<input type="number" min={1} max={60} value={fps} onChange={(event) => setFps(Number(event.target.value))} /></label>
            <label>Output width (px)<input type="number" min={120} max={4096} step={10} value={outputWidth} onChange={(event) => setOutputWidth(Number(event.target.value))} /></label>
            <label>Fragment size<input type="number" min={8} max={128} value={fragmentSize} onChange={(event) => setFragmentSize(Number(event.target.value))} /></label>
            <button className="primary" onClick={() => void generate()} disabled={busy || !active || !targetIds.length}><Play size={16} /> Generate traversal video</button>
            <button className="primary" onClick={() => void autoRun()} disabled={busy || !targetIds.length}><Compass size={16} /> Search Uruguay &amp; generate</button>
            <p className="section-note">Search Uruguay &amp; generate runs the whole walk in one step: sample places, discover, acquire, auto-approve CV-accepted frames, and render. Frames remain reviewable afterwards.</p>
          </div>
        </div>
      </section>
    </>
  );
}
