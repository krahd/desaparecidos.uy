export type VideoOptions = {
  split_orientation: 'side-by-side' | 'stacked';
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
  split_orientation: 'side-by-side', contribution_seconds: 2.5, scan_seconds: 0.18,
  final_hold_seconds: 4, details_hold_seconds: 3, text_hold_seconds: 2,
  fade_seconds: 1, closing_text: '', show_match_marks: true,
};

export type StructuralOptions = {
  reconstruction_mode: 'fixed' | 'largest-first' | 'refine';
  max_region_size: number;
  structure_threshold: number;
  min_structure: number;
  refinement_margin: number;
};
export const defaultStructuralOptions: StructuralOptions = {
  reconstruction_mode: 'refine', max_region_size: 384,
  structure_threshold: 0.72, min_structure: 0.035, refinement_margin: 0.04,
};

export function VideoControls({ value, onChange, traversal = false }: {
  value: VideoOptions; onChange: (value: VideoOptions) => void; traversal?: boolean;
}) {
  const times = [
    ['contribution_seconds', 'Minimum contribution hold (seconds)'],
    ...(traversal ? [['scan_seconds', 'Unmatched frame (seconds)']] : []),
    ['final_hold_seconds', 'Reconstructed image (seconds)'],
    ['details_hold_seconds', 'Person details (seconds)'],
    ['text_hold_seconds', 'Closing text (seconds)'],
    ['fade_seconds', 'Fade duration (seconds)'],
  ];
  return <div className="video-controls">
    <p className="section-note">Search → reconstructed image → person details → text. All output is monochrome. Duration extends when necessary to show every contribution.</p>
    <label>Two equal video halves<select value={value.split_orientation} onChange={e => onChange({ ...value, split_orientation: e.target.value as VideoOptions['split_orientation'] })}>
      <option value="side-by-side">Search left · reconstruction right</option>
      <option value="stacked">Search above · reconstruction below</option>
    </select></label>
    <div className="form-grid">{times.map(([key, label]) => <label key={key}>{label}<input type="number" min={0.05} max={60} step={0.05} value={value[key as keyof VideoOptions] as number} onChange={e => onChange({ ...value, [key]: Number(e.target.value) })} /></label>)}</div>
    <label>Closing text<input maxLength={240} value={value.closing_text} placeholder="Memorial title" onChange={e => onChange({ ...value, closing_text: e.target.value })} /></label>
    <label className="checkbox"><input type="checkbox" checked={value.show_match_marks} onChange={e => onChange({ ...value, show_match_marks: e.target.checked })} />Show matched region and destination</label>
  </div>;
}
