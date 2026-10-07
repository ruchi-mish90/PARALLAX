import argparse
import csv
import hashlib
import re
import shutil
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests
import browser_cookie3


PROJECT = Path(__file__).resolve().parent.parent

MANIFEST = Path(
    r"C:\Users\graj6\Downloads\parallax_results\parallax_results"
    r"\PARALLAX_FINAL_DOWNLOAD_MANIFEST.csv"
)

DATA_ROOT = PROJECT / "PARALLAX_DATA"
LOG_FILE = DATA_ROOT / "download_log.csv"
SUMMARY_FILE = DATA_ROOT / "download_summary.csv"

OHRC_ZIPS = DATA_ROOT / "OHRC" / "raw_zips"
OHRC_EXTRACTED = DATA_ROOT / "OHRC" / "extracted"

TMC_ZIPS = DATA_ROOT / "TMC2" / "raw_zips"
TMC_EXTRACTED = DATA_ROOT / "TMC2" / "extracted"

CHUNK_SIZE = 1024 * 1024
MAX_RETRIES = 4
REQUEST_TIMEOUT = (30, 180)

LOG_FIELDS = [
    "product_id",
    "sensor",
    "filename",
    "status",
    "attempts",
    "file_size_bytes",
    "download_start",
    "download_end",
    "sha256",
    "zip_valid",
    "extraction_status",
    "error",
]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def prepare_directories():
    for p in [
        OHRC_ZIPS,
        OHRC_EXTRACTED,
        TMC_ZIPS,
        TMC_EXTRACTED,
    ]:
        p.mkdir(parents=True, exist_ok=True)


def load_manifest():
    if not MANIFEST.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST}")

    df = pd.read_csv(MANIFEST)

    required = {"pair_id", "ohrc_product_id", "tmc2_product_id"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Manifest missing columns: {sorted(missing)}")

    return df


def build_jobs(df):
    jobs = []

    for product_id in df["ohrc_product_id"].dropna().astype(str).unique():
        jobs.append({
            "product_id": product_id,
            "sensor": "OHRC",
            "filename": f"{product_id}.zip",
        })

    for product_id in df["tmc2_product_id"].dropna().astype(str).unique():
        jobs.append({
            "product_id": product_id,
            "sensor": "TMC2",
            "filename": f"{product_id}.zip",
        })

    return jobs


def product_date(product_id):
    m = re.search(r"_(\d{8})T\d{10,}\_", product_id)

    if not m:
        raise ValueError(f"Cannot extract YYYYMMDD from product ID: {product_id}")

    return m.group(1)


def build_url(job):
    product_id = job["product_id"]
    date = product_date(product_id)

    base = (
        "https://pradan.issdc.gov.in/ch2/protected/downloadData/"
        "POST_OD/isda_archive/ch2_bundle/cho_bundle/nop/"
    )

    if job["sensor"] == "OHRC":
        return (
            f"{base}ohr_collection/data/raw/{date}/"
            f"{product_id}.zip?ohrc"
        )

    if job["sensor"] == "TMC2":
        return (
            f"{base}tmc_collection/data/calibrated/{date}/"
            f"{product_id}.zip?tmc2"
        )

    raise ValueError(f"Unsupported sensor: {job['sensor']}")


def create_authenticated_session():
    session = requests.Session()

    try:
        cookies = browser_cookie3.chrome(
            domain_name="pradan.issdc.gov.in"
        )
    except Exception as e:
        raise RuntimeError(
            "Could not read Chrome cookies. Make sure Chrome is logged into "
            "PRADAN and try again."
        ) from e

    count = 0

    for cookie in cookies:
        session.cookies.set(
            cookie.name,
            cookie.value,
            domain=cookie.domain,
            path=cookie.path,
        )
        count += 1

    if count == 0:
        raise RuntimeError(
            "No PRADAN Chrome cookies found. Log into PRADAN in Chrome first."
        )

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/152 Safari/537.36"
        ),
        "Accept": "*/*",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
    })

    print(f"Loaded {count} PRADAN browser cookies into memory.")

    return session


def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


def validate_zip(zip_path):
    if not zip_path.exists() or zip_path.stat().st_size <= 0:
        return False, "ZIP file is missing or empty"

    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            bad = z.testzip()

            if bad is not None:
                return False, f"Corrupt ZIP member: {bad}"

            names = z.namelist()
            lower_names = [n.lower() for n in names]

            has_xml = any(n.endswith(".xml") for n in lower_names)
            has_data = any(
                "/data/" in f"/{n}" or n.startswith("data/")
                for n in lower_names
            )
            has_geometry = any(
                "/geometry/" in f"/{n}" or n.startswith("geometry/")
                for n in lower_names
            )
            has_browse = any(
                "/browse/" in f"/{n}" or n.startswith("browse/")
                for n in lower_names
            )

            missing = []

            if not has_xml:
                missing.append("XML")

            if not has_data:
                missing.append("data")

            if not has_geometry:
                missing.append("geometry")

            if not has_browse:
                missing.append("browse")

            if missing:
                return False, (
                    "ZIP opened successfully but expected content missing: "
                    + ", ".join(missing)
                )

            return True, "ZIP valid; XML/data/geometry/browse present"

    except zipfile.BadZipFile:
        return False, "Invalid or incomplete ZIP archive"

    except Exception as e:
        return False, f"ZIP validation error: {e}"


def safe_extract(zip_path, destination):
    destination.mkdir(parents=True, exist_ok=True)

    destination_resolved = destination.resolve()

    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.infolist():
            target = (destination / member.filename).resolve()

            if (
                target != destination_resolved
                and destination_resolved not in target.parents
            ):
                raise RuntimeError(
                    f"Unsafe ZIP path detected: {member.filename}"
                )

        z.extractall(destination)


def load_log():
    if not LOG_FILE.exists():
        return {}

    df = pd.read_csv(LOG_FILE, dtype=str)

    return {
        row["product_id"]: row.to_dict()
        for _, row in df.iterrows()
    }


def write_log(records):
    DATA_ROOT.mkdir(parents=True, exist_ok=True)

    with LOG_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        writer.writeheader()

        for record in records.values():
            writer.writerow({
                field: record.get(field, "")
                for field in LOG_FIELDS
            })


def download_file(session, job, zip_path):
    url = build_url(job)

    partial = zip_path.with_suffix(".zip.part")

    attempts = 0
    start_time = utc_now()

    for attempt in range(1, MAX_RETRIES + 1):
        attempts = attempt

        try:
            existing = partial.stat().st_size if partial.exists() else 0

            headers = {}

            if existing > 0:
                headers["Range"] = f"bytes={existing}-"

            print(
                f"[{job['sensor']}] {job['product_id']} "
                f"attempt {attempt}/{MAX_RETRIES}"
            )

            with session.get(
                url,
                headers=headers,
                stream=True,
                allow_redirects=True,
                timeout=REQUEST_TIMEOUT,
            ) as response:

                final_url = response.url.lower()
                content_type = (
                    response.headers.get("Content-Type", "")
                    .lower()
                )

                if "keycloak" in final_url or "login" in final_url:
                    raise RuntimeError(
                        "PRADAN authentication/session expired or login redirect detected."
                    )

                if response.status_code == 401:
                    raise RuntimeError(
                        "PRADAN returned HTTP 401: authentication required."
                    )

                if response.status_code == 403:
                    raise RuntimeError(
                        "PRADAN returned HTTP 403: authenticated access denied."
                    )

                if response.status_code >= 500:
                    raise RuntimeError(
                        f"Transient PRADAN server error: HTTP {response.status_code}"
                    )

                if existing > 0 and response.status_code == 200:
                    print(
                        "Server did not honor Range request; "
                        "restarting partial download."
                    )

                    partial.unlink(missing_ok=True)
                    existing = 0

                elif existing > 0 and response.status_code != 206:
                    raise RuntimeError(
                        f"Unexpected resume response: HTTP {response.status_code}"
                    )

                elif existing == 0 and response.status_code != 200:
                    raise RuntimeError(
                        f"Unexpected PRADAN response: HTTP {response.status_code}"
                    )

                if "text/html" in content_type:
                    raise RuntimeError(
                        "PRADAN returned HTML instead of a ZIP. "
                        "Authentication may have expired."
                    )

                mode = "ab" if existing > 0 else "wb"

                with partial.open(mode) as f:
                    for chunk in response.iter_content(CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)

            if not partial.exists() or partial.stat().st_size == 0:
                raise RuntimeError("Downloaded file is empty.")

            partial.replace(zip_path)

            return {
                "success": True,
                "attempts": attempts,
                "start": start_time,
                "end": utc_now(),
                "error": "",
            }

        except Exception as e:
            print(f"  ERROR: {e}")

            if attempt < MAX_RETRIES:
                delay = 2 ** (attempt - 1)

                print(f"  Retrying in {delay} seconds...")
                time.sleep(delay)

            else:
                return {
                    "success": False,
                    "attempts": attempts,
                    "start": start_time,
                    "end": utc_now(),
                    "error": str(e),
                }


def process_job(session, job, records):
    product_id = job["product_id"]

    if job["sensor"] == "OHRC":
        zip_dir = OHRC_ZIPS
        extract_dir = OHRC_EXTRACTED
    else:
        zip_dir = TMC_ZIPS
        extract_dir = TMC_EXTRACTED

    zip_path = zip_dir / job["filename"]
    product_extract = extract_dir / product_id

    record = records.get(product_id, {})

    record.update({
        "product_id": product_id,
        "sensor": job["sensor"],
        "filename": job["filename"],
        "status": "PENDING",
        "attempts": record.get("attempts", 0),
        "file_size_bytes": "",
        "download_start": "",
        "download_end": "",
        "sha256": "",
        "zip_valid": "",
        "extraction_status": "",
        "error": "",
    })

    # Existing verified/extracted product: skip network download.
    if zip_path.exists():
        valid, message = validate_zip(zip_path)

        if valid and product_extract.exists():
            record.update({
                "status": "EXTRACTED",
                "file_size_bytes": zip_path.stat().st_size,
                "sha256": sha256_file(zip_path),
                "zip_valid": "YES",
                "extraction_status": "EXISTING_VALID",
                "error": "",
            })

            records[product_id] = record
            print(f"[SKIP] {product_id} already valid and extracted.")
            return

        if not valid:
            quarantine = zip_path.with_suffix(".corrupt.zip")

            print(
                f"[RETRY] Existing ZIP invalid: {message}"
            )

            zip_path.replace(quarantine)

    record["status"] = "DOWNLOADING"
    records[product_id] = record
    write_log(records)

    result = download_file(session, job, zip_path)

    record["attempts"] = result["attempts"]
    record["download_start"] = result["start"]
    record["download_end"] = result["end"]

    if not result["success"]:
        record.update({
            "status": "FAILED",
            "error": result["error"],
            "zip_valid": "NO",
            "extraction_status": "NOT_ATTEMPTED",
        })

        records[product_id] = record
        write_log(records)
        return

    record["status"] = "DOWNLOADED"
    record["file_size_bytes"] = zip_path.stat().st_size
    write_log(records)

    valid, message = validate_zip(zip_path)

    if not valid:
        record.update({
            "status": "FAILED",
            "zip_valid": "NO",
            "error": message,
            "extraction_status": "NOT_ATTEMPTED",
        })

        records[product_id] = record
        write_log(records)

        quarantine = zip_path.with_suffix(".corrupt.zip")
        zip_path.replace(quarantine)

        return

    record["status"] = "VERIFIED"
    record["zip_valid"] = "YES"
    record["sha256"] = sha256_file(zip_path)

    records[product_id] = record
    write_log(records)

    try:
        if product_extract.exists():
            shutil.rmtree(product_extract)

        safe_extract(zip_path, product_extract)

        record.update({
            "status": "EXTRACTED",
            "extraction_status": "SUCCESS",
            "error": "",
        })

        print(f"[OK] {product_id}")

    except Exception as e:
        record.update({
            "status": "FAILED",
            "extraction_status": "FAILED",
            "error": f"Extraction error: {e}",
        })

        print(f"[ERROR] Extraction failed: {e}")

    records[product_id] = record
    write_log(records)


def write_summary(records, total_required):
    statuses = [
        r.get("status", "")
        for r in records.values()
    ]

    downloaded = sum(
        s in {"DOWNLOADED", "VERIFIED", "EXTRACTED"}
        for s in statuses
    )

    verified = sum(
        s in {"VERIFIED", "EXTRACTED"}
        for s in statuses
    )

    extracted = sum(
        s == "EXTRACTED"
        for s in statuses
    )

    failed_ids = [
        r["product_id"]
        for r in records.values()
        if r.get("status") == "FAILED"
    ]

    summary = {
        "total_required": total_required,
        "total_downloaded": downloaded,
        "total_verified": verified,
        "total_extracted": extracted,
        "total_failed": len(failed_ids),
        "missing_products": ";".join(failed_ids),
    }

    with SUMMARY_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(summary.keys())
        )
        writer.writeheader()
        writer.writerow(summary)

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="PARALLAX PRADAN reproducible downloader"
    )

    parser.add_argument(
        "--test",
        type=int,
        default=0,
        help="Test mode. --test 2 means exactly 1 OHRC + 1 TMC-2.",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Reserved for future conservative parallel download mode.",
    )

    args = parser.parse_args()

    if args.workers < 1 or args.workers > 4:
        raise SystemExit("--workers must be between 1 and 4.")

    prepare_directories()

    df = load_manifest()
    jobs = build_jobs(df)

    ohrc_jobs = [j for j in jobs if j["sensor"] == "OHRC"]
    tmc_jobs = [j for j in jobs if j["sensor"] == "TMC2"]

    if args.test:
        if args.test != 2:
            raise SystemExit(
                "--test currently requires value 2: "
                "one OHRC + one TMC-2."
            )

        jobs = [ohrc_jobs[0], tmc_jobs[0]]

        print("\n=== PARALLAX TEST MODE ===")
        print("Testing exactly:")
        print(f"OHRC : {jobs[0]['product_id']}")
        print(f"TMC2 : {jobs[1]['product_id']}")
    else:
        print("\n=== PARALLAX FULL DOWNLOAD ===")
        print(f"Pairs in manifest : {len(df)}")
        print(f"Unique OHRC      : {len(ohrc_jobs)}")
        print(f"Unique TMC-2     : {len(tmc_jobs)}")
        print(f"Total products   : {len(jobs)}")

    print("\nPreparing authenticated PRADAN session...")

    session = create_authenticated_session()

    records = load_log()

    for job in jobs:
        process_job(session, job, records)

    summary = write_summary(records, len(jobs))

    print("\n=== DOWNLOAD SUMMARY ===")

    for key, value in summary.items():
        print(f"{key}: {value}")

    failed = int(summary["total_failed"])

    if failed:
        print("\nSome products failed. Review:")
        print(LOG_FILE)
        print(SUMMARY_FILE)
        return 1

    print("\nAll requested products completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
