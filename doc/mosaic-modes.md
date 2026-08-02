# Unique spatial mosaic modes

The fragment-based works now expose two final composition modes:

- **Grid** retains a regular square lattice.
- **Free-positioned** preserves each region's match to the target while applying
  deterministic displacement, scale, rotation, opacity, and overlap.

The interface defaults to 36-pixel tiles, spatial region matching, and unique
tiles. Spatial matching compares the internal colour, luminance, and
directional structure of source and target regions. It is therefore intended to
select meaningful image regions rather than treat tiles as enlarged pixels.

With **Use each image region only once** enabled, an extracted source crop
cannot appear twice. Different regions from the same reviewed parent image may
still participate. For *Están en todas partes*, this distinction permits a
bounded collection of high-resolution place photographs to contribute many
different urban details without duplicating any exact crop.

If the reviewed corpus cannot provide enough distinct regions, generation
stops with an explicit instruction to approve or crawl additional images,
increase the tile size, or reduce the output width. The renderer never silently
relaxes uniqueness.

The historical implementation is retained in `pipeline_core.py`,
`api_core.py`, `AppCore.tsx`, and `apiCore.ts`. The public facade modules add
the new controls while preserving the existing pipeline, API endpoints,
interface, video process, output sidecars, and benchmark compatibility.
