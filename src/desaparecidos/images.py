from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from .manifests import ManifestRow, row_file_path


@dataclass(frozen=True)
class Fragment:
    source_id: str
    fragment_id: str
    image: Image.Image
    descriptor: np.ndarray
    x: int
    y: int


def load_rgb(path: str | Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def crop_from_row(image: Image.Image, row: ManifestRow) -> Image.Image:
    values = row.values
    keys = ["crop_x", "crop_y", "crop_width", "crop_height"]
    if not all(values.get(key) for key in keys):
        return image
    x = int(float(values["crop_x"]))
    y = int(float(values["crop_y"]))
    width = int(float(values["crop_width"]))
    height = int(float(values["crop_height"]))
    if width <= 0 or height <= 0:
        return image
    return image.crop((x, y, x + width, y + height))


def descriptor_for(image: Image.Image) -> np.ndarray:
    arr = np.asarray(image.resize((32, 32), Image.Resampling.BILINEAR), dtype=np.float32)
    mean_rgb = arr.mean(axis=(0, 1)) / 255.0
    lum = (0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]) / 255.0
    contrast = np.array([lum.std()], dtype=np.float32)
    gx = np.abs(np.diff(lum, axis=1)).mean()
    gy = np.abs(np.diff(lum, axis=0)).mean()
    edge = np.array([gx, gy], dtype=np.float32)
    return np.concatenate([mean_rgb.astype(np.float32), contrast, edge])


def extract_fragments(
    rows: list[ManifestRow],
    manifest_path: str | Path,
    *,
    fragment_size: int,
    stride: int | None = None,
    max_fragments_per_source: int = 240,
) -> list[Fragment]:
    if fragment_size < 8:
        raise ValueError("fragment_size must be at least 8")
    if max_fragments_per_source < 1:
        raise ValueError("max_fragments_per_source must be at least 1")
    stride = stride or fragment_size
    fragments: list[Fragment] = []

    for row in rows:
        image = load_rgb(row_file_path(row, manifest_path))
        width, height = image.size
        source_fragments: list[Fragment] = []
        for y in range(0, max(1, height - fragment_size + 1), stride):
            for x in range(0, max(1, width - fragment_size + 1), stride):
                patch = image.crop((x, y, x + fragment_size, y + fragment_size))
                if patch.size != (fragment_size, fragment_size):
                    patch = patch.resize((fragment_size, fragment_size))
                source_fragments.append(
                    Fragment(
                        source_id=row.id,
                        fragment_id=f"{row.id}:{x}:{y}",
                        image=patch,
                        descriptor=descriptor_for(patch),
                        x=x,
                        y=y,
                    )
                )
        if not source_fragments:
            resized = image.resize((fragment_size, fragment_size), Image.Resampling.LANCZOS)
            source_fragments.append(
                Fragment(row.id, f"{row.id}:0:0", resized, descriptor_for(resized), 0, 0)
            )
        fragments.extend(_sample_fragments(source_fragments, max_fragments_per_source))

    if not fragments:
        raise ValueError("no fragments could be extracted from approved sources")
    return fragments


def _sample_fragments(source_fragments: list[Fragment], limit: int) -> list[Fragment]:
    if len(source_fragments) <= limit:
        return source_fragments
    if limit == 1:
        return [source_fragments[len(source_fragments) // 2]]
    indexes = np.linspace(0, len(source_fragments) - 1, num=limit, dtype=int)
    return [source_fragments[int(index)] for index in indexes]
