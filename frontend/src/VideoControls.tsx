export type VideoOptions = {
  split_orientation: 'side-by-side' | 'stacked';
  playback_mode: 'continuous' | 'hold';
  contribution_seconds: number;
  scan_seconds: number;
  final_hold_seconds: number;
  details_hold_seconds: number;
  text_hold_seconds: number;
  fade_seconds: number;
  closing_text: string;
  show_match_marks: boolean;
};

export const defaultVideoOptions: VideoOptions = {
  split_orientation: 'side-by-side', playback_mode: 'continuous', contribution_seconds: 0.75, scan_seconds: 0.16,
  final_hold_seconds: 4, details_hold_seconds: 3, text_hold_seconds: 2,
  fade_seconds: 1, closing_text: '', show_match_marks: true,
};

export type StructuralOptions = {
  require_complete: boolean;
  max_search_batches: number;
  search_budget_seconds: number;
  contribution_interval: number;
  search_similarity: number;
  structure_scale: 'broad' | 'fine';
  tone_mode: 'source' | 'match-region';
  reconstruction_mode: 'fixed' | 'largest-first' | 'refine';
  max_region_size: number;
  structure_threshold: number;
  min_structure: number;
  refinement_margin: number;
};
export const defaultStructuralOptions: StructuralOptions = {
  require_complete: true, max_search_batches: 8, search_budget_seconds: 300,
  contribution_interval: 6, search_similarity: 0.95,
  structure_scale: 'broad', tone_mode: 'source',
  reconstruction_mode: 'refine', max_region_size: 384,
  structure_threshold: 0.82, min_structure: 0.035, refinement_margin: 0.04,
};

export function VideoControls({ value, onChange, traversal = false }: {
  value: VideoOptions; onChange: (value: VideoOptions) => void; traversal?: boolean;
}) {
  const times = [
    ['contribution_seconds', value.playback_mode === 'continuous' ? 'Region transfer (seconds)' : 'Minimum contribution hold (seconds)'],
    ...(traversal || value.playback_mode === 'continuous' ? [['scan_seconds', 'Search frame (seconds)']] : []),
    ['final_hold_seconds', 'Reconstructed image (seconds)'],
    ['details_hold_seconds', 'Person details (seconds)'],
    ['text_hold_seconds', 'Closing text (seconds)'],
    ['fade_seconds', 'Fade duration (seconds)'],
  ];
  return <div className="video-controls">
    <p className="section-note">Search → reconstructed image → person details → text. All output is monochrome. Continuous playback follows the search-frame timing (about six frames per second by default); every region has time to reach its destination.</p>
    <label>Playback<select value={value.playback_mode} onChange={e => onChange({ ...value, playback_mode: e.target.value as VideoOptions['playback_mode'] })}>
      <option value="continuous">Continuous traversal with travelling regions</option>
      <option value="hold">Pause on each contribution</option>
    </select></label>
    <label>Two equal video halves<select value={value.split_orientation} onChange={e => onChange({ ...value, split_orientation: e.target.value as VideoOptions['split_orientation'] })}>
      <option value="side-by-side">Search left · reconstruction right</option>
      <option value="stacked">Search above · reconstruction below</option>
    </select></label>
    <div className="form-grid">{times.map(([key, label]) => <label key={key}>{label}<input type="number" min={0.05} max={60} step={0.05} value={value[key as keyof VideoOptions] as number} onChange={e => onChange({ ...value, [key]: Number(e.target.value) })} /></label>)}</div>
    <label>Closing text<input maxLength={240} value={value.closing_text} placeholder="Memorial title" onChange={e => onChange({ ...value, closing_text: e.target.value })} /></label>
    <label className="checkbox"><input type="checkbox" checked={value.show_match_marks} onChange={e => onChange({ ...value, show_match_marks: e.target.checked })} />Show matched region and destination</label>
  </div>;
}
