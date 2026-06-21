# Process-video source transitions

1. In the videos, the animation of the portion of the source image going to the resulting image should start with the source image at full opacity, then quickly fade to transparent (everything but the selected bits) and then the bits go to their place.
2. We should explore two modes: one where the source portions are set in a grid, as now, and another where they use non-grid positions defined only by the matching with the target image sections.

## Implemented

- Each contributing approved place source now appears at full opacity, then its non-contributing pixels fade to the black video background before the selected fragments move to their target positions.
- For contemporary people sources, the reveal is restricted to the reviewed face region used for fragment extraction; the surrounding photograph is never displayed.
- `grid` mode moves selected fragments from their source coordinates into the existing regular staging grid, then into the target.
- `match` mode moves selected fragments into a deterministic non-grid scatter defined only by their matched target sections, then into those target positions.
- The mode is selectable in the GUI and through API/CLI `video_source_layout` / `--video-source-layout`, and is recorded in output sidecars.
- Rejected and non-contributing candidate images remain excluded from generated videos.
