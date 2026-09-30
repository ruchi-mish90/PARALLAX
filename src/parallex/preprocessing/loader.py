from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def load_preprocessed_run(run_id: str) -> tuple[np.ndarray, np.ndarray, dict]:
    root = Path(__file__).resolve().parents[3] / "data" / "preprocessed" / run_id

    if not root.exists():
        raise FileNotFoundError(f"Preprocessed run not found: {root}")

    source_path = root / "source" / "image.npy"
    target_path = root / "target" / "image.npy"
    manifest_path = root / "manifest.json"

    if not source_path.exists():
        raise FileNotFoundError(source_path)

    if not target_path.exists():
        raise FileNotFoundError(target_path)

    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)

    source = np.load(source_path)
    target = np.load(target_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    return source, target, manifest

