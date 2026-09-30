from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import numpy as np


PREPROCESSED_ROOT = Path(__file__).resolve().parents[3] / "data" / "preprocessed"


def create_run(source_sensor: str, target_sensor: str) -> tuple[str, Path]:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid4().hex[:8]
    run_dir = PREPROCESSED_ROOT / run_id
    (run_dir / "source").mkdir(parents=True, exist_ok=True)
    (run_dir / "target").mkdir(parents=True, exist_ok=True)
    return run_id, run_dir


def save_preprocessed(
    run_dir: Path,
    *,
    source_image: np.ndarray,
    target_image: np.ndarray,
    source_metadata: dict,
    target_metadata: dict,
    manifest: dict,
) -> dict:
    source_path = run_dir / "source" / "image.npy"
    target_path = run_dir / "target" / "image.npy"
    source_meta_path = run_dir / "source" / "metadata.json"
    target_meta_path = run_dir / "target" / "metadata.json"
    manifest_path = run_dir / "manifest.json"

    np.save(source_path, np.asarray(source_image, dtype=np.float32))
    np.save(target_path, np.asarray(target_image, dtype=np.float32))

    source_meta_path.write_text(
        json.dumps(source_metadata, indent=2, default=str),
        encoding="utf-8",
    )
    target_meta_path.write_text(
        json.dumps(target_metadata, indent=2, default=str),
        encoding="utf-8",
    )

    manifest = {
        **manifest,
        "run_id": run_dir.name,
        "source_file": str(source_path),
        "target_file": str(target_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    manifest_path.write_text(
        json.dumps(manifest, indent=2, default=str),
        encoding="utf-8",
    )

    return {
        "run_id": run_dir.name,
        "source_path": str(source_path),
        "target_path": str(target_path),
        "source_metadata": str(source_meta_path),
        "target_metadata": str(target_meta_path),
        "manifest": str(manifest_path),
    }
