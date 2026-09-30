from __future__ import annotations

from typing import Any

from parallex.preprocessing.loader import load_preprocessed_run
from parallex.routing.engine import RoutingEngine


def run_saved_preprocessed_match(
    run_id: str,
    matcher_name: str = "loftr",
) -> dict[str, Any]:
    source, target, manifest = load_preprocessed_run(run_id)

    engine = RoutingEngine()

    result = engine.run_matcher(
        matcher_name,
        source,
        target,
    )

    candidate_matches = int(len(result.matches))
    keypoints_source = int(len(result.keypoints_a))
    keypoints_target = int(len(result.keypoints_b))

    return {
        "run_id": run_id,
        "matcher": matcher_name,
        "source_shape": list(source.shape),
        "target_shape": list(target.shape),
        "candidate_matches": candidate_matches,
        "keypoints_source": keypoints_source,
        "keypoints_target": keypoints_target,
        "manifest": manifest,
        "result": result,
    }
