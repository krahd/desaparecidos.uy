from __future__ import annotations

import json
import math
import random
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .images import Fragment, crop_from_row, descriptor_for, extract_fragments, load_rgb
from .manifests import ManifestRow, approved_rows, row_file_path
from .paths import display_path


@dataclass(frozen=True)
class Stage1Settings:
    seed: int = 17
    fragment_size: int = 24
    reuse_limit: int = 8
    output_width: int = 720
    max_fragments_per_source: int = 240
    make_video: bool = False


@dataclass(frozen=True)
class Stage1Output:
    target_id: str
    still_path: str
    sidecar_path: str
    video_path: str | None = None


def _target_canvas(target: Image.Image, output_width: int, fragment_size: int) -> Image.Image:
    ratio = target.height / target.width
    width = max(fragment_size, int(round(output_width / fragment_size)) * fragment_size)
    height = max(fragment_size, int(round((width * ratio) / fragment_size)) * fragment_size)
    return target.resize((width, height), Image.Resampling.LANCZOS)


def _best_fragment(
    descriptor: np.ndarray,
    fragments: list[Fragment],
    fragment_usage: dict[str, int],
    reuse_limit: int,
) -> Fragment:
    available = [
        fragment
        for fragment in fragments
        if fragment_usage.get(fragment.fragment_id, 0) < reuse_limit
    ]
    if not available:
        raise ValueError("fragment reuse limit exhausted")
    distances = [
        float(np.linalg.norm(descriptor - fragment.descriptor))
        for fragment in available
    ]
    return available[int(np.argmin(distances))]


def assemble_target(
    target_row: ManifestRow,
    target_manifest: str | Path,
    fragments: list[Fragment],
    settings: Stage1Settings,
) -> tuple[Image.Image, dict[str, int], dict[str, int]]:
    target = crop_from_row(load_rgb(row_file_path(target_row, target_manifest)), target_row)
    target = _target_canvas(target, settings.output_width, settings.fragment_size)
    rng = random.Random(settings.seed + sum(ord(char) for char in target_row.id))
    shuffled = list(fragments)
    rng.shuffle(shuffled)

    output = Image.new("RGB", target.size, (245, 245, 242))
    source_usage: dict[str, int] = {}
    fragment_usage: dict[str, int] = {}
    tile = settings.fragment_size
    tile_count = math.ceil(target.width / tile) * math.ceil(target.height / tile)
    source_count = len({fragment.source_id for fragment in fragments})
    fragment_capacity = len(fragments) * settings.reuse_limit
    if fragment_capacity < tile_count:
        required = math.ceil(tile_count / max(1, len(fragments)))
        raise ValueError(
            "reuse_limit is too low: "
            f"need at least {required} per extracted fragment for {tile_count} output tiles "
            f"and {len(fragments)} fragments from {source_count} approved sources; "
            f"got {settings.reuse_limit}"
        )

    for y in range(0, target.height, tile):
        for x in range(0, target.width, tile):
            target_patch = target.crop((x, y, x + tile, y + tile))
            descriptor = descriptor_for(target_patch)
            fragment = _best_fragment(descriptor, shuffled, fragment_usage, settings.reuse_limit)
            source_usage[fragment.source_id] = source_usage.get(fragment.source_id, 0) + 1
            fragment_usage[fragment.fragment_id] = fragment_usage.get(fragment.fragment_id, 0) + 1
            output.paste(fragment.image, (x, y))

    return output, source_usage, fragment_usage


def render_video(
    still: Image.Image,
    target_row: ManifestRow,
    output_path: Path,
    *,
    seed: int,
    fps: int = 12,
    seconds: int = 8,
) -> str:
    if _render_video_ffmpeg(still, target_row, output_path, seed=seed, fps=fps, seconds=seconds):
        return "h264"
    raise RuntimeError(
        "Browser-playable MP4 rendering requires ffmpeg with libx264. "
        "Install ffmpeg, then restart the launcher and generate the video again."
    )


def _video_frames(
    still: Image.Image,
    target_row: ManifestRow,
    *,
    seed: int,
    fps: int,
    seconds: int,
) -> Iterable[Image.Image]:
    width, height = still.size
    total = fps * seconds
    still_arr = np.asarray(still, dtype=np.uint8)
    font = ImageFont.load_default()
    for index in range(total):
        progress = index / max(1, total - 1)
        visible = min(1.0, progress * 1.35)
        mask = np.random.default_rng(seed + index).random((height, width, 1)) < visible
        base = np.full_like(still_arr, 235, dtype=np.uint8)
        frame = np.where(mask, still_arr, base)
        pil_frame = Image.fromarray(frame, "RGB")
        if progress > 0.72:
            draw = ImageDraw.Draw(pil_frame)
            label = target_row.values.get("name", target_row.id)
            box_height = 34
            draw.rectangle((0, height - box_height, width, height), fill=(18, 18, 17))
            draw.text((18, height - 24), label, fill=(245, 245, 240), font=font)
        yield pil_frame


def _render_video_ffmpeg(
    still: Image.Image,
    target_row: ManifestRow,
    output_path: Path,
    *,
    seed: int,
    fps: int,
    seconds: int,
) -> bool:
    ffmpeg = _find_ffmpeg()
    if not ffmpeg:
        return False

    width, height = still.size
    command = [
        ffmpeg,
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{width}x{height}",
        "-r",
        str(fps),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    assert process.stdin is not None
    try:
        for frame in _video_frames(still, target_row, seed=seed, fps=fps, seconds=seconds):
            process.stdin.write(frame.tobytes())
        process.stdin.close()
        stderr = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
        return_code = process.wait()
    except Exception:
        process.kill()
        output_path.unlink(missing_ok=True)
        raise

    if return_code != 0:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(f"ffmpeg could not render H.264 MP4: {stderr.strip() or 'unknown error'}")
    return True


def _find_ffmpeg() -> str | None:
    found = shutil.which("ffmpeg")
    if found:
        return found
    for candidate in ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        path = Path(candidate)
        if path.exists() and path.is_file():
            return str(path)
    return None


def run_stage1(
    target_manifest: str | Path,
    source_manifest: str | Path,
    output_dir: str | Path,
    settings: Stage1Settings,
    *,
    target_id: str | None = None,
) -> list[Stage1Output]:
    target_rows = approved_rows(target_manifest, "targets", require_files=True)
    source_rows = approved_rows(source_manifest, "places", require_files=True)
    if target_id:
        target_rows = [row for row in target_rows if row.id == target_id]
        if not target_rows:
            raise ValueError(f"target id is not approved or does not exist: {target_id}")

    fragments = extract_fragments(
        source_rows,
        source_manifest,
        fragment_size=settings.fragment_size,
        max_fragments_per_source=settings.max_fragments_per_source,
    )
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    outputs: list[Stage1Output] = []
    for target_row in target_rows:
        still, source_usage, fragment_usage = assemble_target(target_row, target_manifest, fragments, settings)
        safe_id = "".join(char if char.isalnum() or char in "-_" else "_" for char in target_row.id)
        stem = f"{safe_id}_seed{settings.seed}_f{settings.fragment_size}"
        still_path = output_root / f"{stem}.png"
        sidecar_path = output_root / f"{stem}.json"
        video_path = output_root / f"{stem}.mp4" if settings.make_video else None
        video_codec = None

        still.save(still_path)
        if video_path is not None:
            video_codec = render_video(still, target_row, video_path, seed=settings.seed)

        sidecar = {
            "target": target_row.values,
            "target_id": target_row.id,
            "source_ids": sorted(source_usage),
            "source_usage": source_usage,
            "fragment_count": len(fragments),
            "fragment_usage_count": len(fragment_usage),
            "max_fragment_reuse_observed": max(fragment_usage.values(), default=0),
            "settings": asdict(settings),
            "still_path": display_path(still_path),
            "video_path": display_path(video_path) if video_path else None,
            "video_codec": video_codec,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "method": "Stage 1 place-fragment reconstruction prototype",
        }
        sidecar_path.write_text(
            json.dumps(sidecar, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        outputs.append(
            Stage1Output(
                target_id=target_row.id,
                still_path=str(still_path),
                sidecar_path=str(sidecar_path),
                video_path=str(video_path) if video_path else None,
            )
        )
    return outputs
