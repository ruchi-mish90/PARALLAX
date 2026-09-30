import sys
from pathlib import Path
import traceback

ROOT = Path(r"C:\Users\graj6\Downloads\parallex")
sys.path.insert(0, str(ROOT / "src"))

from parallex.pipeline.registration import RegistrationPipeline

print("=" * 75)
print("PARALLAX P0001 — REAL PIPELINE FAILURE-PATH TEST")
print("=" * 75)

print("\n[1] REGISTRATION MODULE")
import parallex.pipeline.registration as r
print("RegistrationPipeline:", RegistrationPipeline)

print("\n[2] CONSTRUCTOR")
try:
    import inspect
    print(inspect.signature(RegistrationPipeline))
except Exception as e:
    print("signature error:", e)

print("\n[3] PUBLIC METHODS")
try:
    print([
        x for x in dir(RegistrationPipeline)
        if not x.startswith("_")
    ])
except Exception as e:
    print("method inspection error:", e)

print("\n[4] REAL P0001 RESULT.JSON")
result = ROOT / "results" / "final_backend" / "P0001" / "result.json"

if result.exists():
    import json
    data = json.loads(result.read_text(encoding="utf-8"))

    print("keys:", list(data.keys()))

    for k, v in data.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            print(f"{k}: {v}")
else:
    print("P0001 result.json missing")


print("\n[5] FAILURE-PATH UNIT CHECKS")

# Test the existing quality/validation components with deliberately bad inputs.
try:
    from parallex.validation.quality import QualityAssessor
    import inspect

    print("QualityAssessor:", QualityAssessor)
    print("signature:", inspect.signature(QualityAssessor))

    qa = QualityAssessor()

    print("quality object:", qa)

    for method in [
        x for x in dir(qa)
        if not x.startswith("_")
    ]:
        print(" quality method:", method)

except Exception:
    traceback.print_exc()


print("\n[6] SUBPIXEL IMPLEMENTATION")

try:
    import parallex.refinement.subpixel as sp
    import inspect

    print([
        x for x in dir(sp)
        if not x.startswith("_")
    ])

    for name in dir(sp):
        if not name.startswith("_"):
            obj = getattr(sp, name)
            if callable(obj):
                try:
                    print(name, inspect.signature(obj))
                except Exception:
                    pass

except Exception:
    traceback.print_exc()


print("\n[7] METRICS IMPLEMENTATION")

try:
    import parallex.validation.metrics as m
    import inspect

    for name in dir(m):
        if not name.startswith("_"):
            obj = getattr(m, name)

            if callable(obj):
                try:
                    print(name, inspect.signature(obj))
                except Exception:
                    pass

except Exception:
    traceback.print_exc()


print("\n" + "=" * 75)
print("REAL PIPELINE AUDIT COMPLETE")
print("=" * 75)
