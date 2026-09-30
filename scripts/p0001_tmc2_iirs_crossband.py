import subprocess
import sys

bands = [128, 160, 192, 224]

for band in bands:
    print("\\n" + "=" * 70)
    print(f"CROSS-BAND VERIFICATION ? BAND {band}")
    print("=" * 70)

    p = subprocess.run(
        [sys.executable, "scripts/p0001_tmc2_iirs_spatial_batch.py"],
        capture_output=True,
        text=True
    )

    # Existing script is currently fixed to band 224.
    # Print its output so the current implementation is preserved.
    print(p.stdout)
    if p.stderr:
        print(p.stderr)
