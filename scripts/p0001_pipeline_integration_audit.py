from pathlib import Path
import inspect
import json

ROOT = Path.cwd()

print("=" * 75)
print("PARALLAX P0001 - PIPELINE INTEGRATION AUDIT")
print("=" * 75)

# ------------------------------------------------------------
# 1. REGISTRATION PIPELINE
# ------------------------------------------------------------
print("\n[1] REGISTRATION PIPELINE")

from parallex.pipeline.registration import RegistrationPipeline

print("class:", RegistrationPipeline)
print("constructor:", inspect.signature(RegistrationPipeline))
print("run:", inspect.signature(RegistrationPipeline.run))

src = inspect.getsource(RegistrationPipeline)

checks = {
    "pair characterization": ["character", "difficulty"],
    "observability": ["observab"],
    "routing": ["router", "route", "model"],
    "matcher": ["matcher", "match"],
    "confidence filtering": ["confidence"],
    "geometric verification": ["ransac", "geometric", "verify"],
    "spatial coverage": ["coverage", "spatial"],
    "quality": ["quality"],
    "subpixel refinement": ["refine_points", "subpixel"],
    "metrics": ["registration_metrics", "reprojection_errors"],
}

for name, terms in checks.items():
    hits = [t for t in terms if t.lower() in src.lower()]
    if hits:
        print(f"{name:28s}: YES {hits}")
    else:
        print(f"{name:28s}: NO")

# ------------------------------------------------------------
# 2. QUALITY MODULE
# ------------------------------------------------------------
print("\n[2] QUALITY MODULE")

import parallex.validation.quality as quality

print("file:", quality.__file__)
print("callable public names:")

for name in dir(quality):
    if not name.startswith("_"):
        obj = getattr(quality, name)
        if callable(obj):
            try:
                print(" ", name, inspect.signature(obj))
            except Exception:
                print(" ", name)

# ------------------------------------------------------------
# 3. SUBPIXEL
# ------------------------------------------------------------
print("\n[3] SUBPIXEL")

import parallex.refinement.subpixel as subpixel

print("refine_points:", inspect.signature(subpixel.refine_points))
print("SubpixelResult:", inspect.signature(subpixel.SubpixelResult))

# ------------------------------------------------------------
# 4. METRICS
# ------------------------------------------------------------
print("\n[4] METRICS")

import parallex.validation.metrics as metrics

print(
    "registration_metrics:",
    inspect.signature(metrics.registration_metrics)
)

print(
    "reprojection_errors:",
    inspect.signature(metrics.reprojection_errors)
)

# ------------------------------------------------------------
# 5. VERIFICATION MODULES
# ------------------------------------------------------------
print("\n[5] VERIFICATION MODULES")

modules = [
    "parallex.verification.confidence",
    "parallex.verification.geometric",
    "parallex.verification.ransac",
    "parallex.verification.spatial",
    "parallex.validation.failure",
    "parallex.validation.observability",
    "parallex.validation.quality",
]

for modname in modules:
    try:
        mod = __import__(modname, fromlist=["*"])

        print("\n", modname)

        for name in dir(mod):
            if not name.startswith("_"):
                obj = getattr(mod, name)

                if callable(obj):
                    try:
                        print("  ", name, inspect.signature(obj))
                    except Exception:
                        pass

    except Exception as e:
        print("IMPORT ERROR:", modname, e)

# ------------------------------------------------------------
# 6. REAL P0001 RESULT
# ------------------------------------------------------------
print("\n[6] REAL P0001 RESULT")

result_path = (
    ROOT
    / "results"
    / "final_backend"
    / "P0001"
    / "result.json"
)

if result_path.exists():

    result = json.loads(
        result_path.read_text(encoding="utf-8")
    )

    for key, value in result.items():
        print(f"{key}: {value}")

else:
    print("MISSING:", result_path)

# ------------------------------------------------------------
# 7. SOURCE-LEVEL PIPELINE STAGES
# ------------------------------------------------------------
print("\n[7] REGISTRATION.PY IMPORTANT LINES")

important_terms = [
    "refine_points",
    "registration_metrics",
    "reprojection_errors",
    "quality",
    "coverage",
    "ransac",
    "router",
    "matcher",
    "observab",
    "confidence",
    "return ",
]

for line_number, line in enumerate(src.splitlines(), 1):

    low = line.lower()

    if any(term in low for term in important_terms):
        print(f"{line_number:4d}: {line}")

# ------------------------------------------------------------
# 8. FINAL DIAGNOSIS
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("AUDIT COMPLETE")
print("=" * 75)

print("""
The audit checks:

1. RegistrationPipeline API
2. Actual quality.py API
3. Subpixel implementation
4. Metrics implementation
5. Verification modules
6. Real P0001 result
7. Actual pipeline source integration

Important distinction:

A module existing in the repository does not prove that
RegistrationPipeline.run() actually calls it.

P0001 OHRC/TMC2 should remain a spatial-gate rejection
because that pair has no valid geographic overlap.

The next implementation step should be based on the
source-level integration evidence printed above.
""")

print("=" * 75)
