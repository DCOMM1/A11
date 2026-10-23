#!/usr/bin/env python3
"""Download complete official FEC ZIP files within a total byte budget.

Never stores partial ZIPs: if a file does not fit in the remaining budget,
it is skipped. This is a bounded source-acquisition batch, not a database load.
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

BUDGET = int(os.getenv("FEC_MAX_BYTES", "2000000000"))
OUT = Path(os.getenv("FEC_OUT_DIR", "fec_batch"))
OUT.mkdir(parents=True, exist_ok=True)
SOURCES = [
    ("cn26.zip", "https://www.fec.gov/files/bulk-downloads/2026/cn26.zip"),
    ("ccl26.zip", "https://www.fec.gov/files/bulk-downloads/2026/ccl26.zip"),
    ("indiv26.zip", "https://www.fec.gov/files/bulk-downloads/2026/indiv26.zip"),
]
manifest = {
    "status": "running",
    "budget_bytes": BUDGET,
    "downloaded_bytes": 0,
    "sources": [],
    "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}
def head_size(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "DCOMM-A11-public-records-ingest/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        length = resp.headers.get("Content-Length")
        return int(length) if length is not None else None

for name, url in SOURCES:
    entry = {"name": name, "url": url, "status": "pending"}
    try:
        size = head_size(url)
        entry["reported_size_bytes"] = size
        remaining = BUDGET - manifest["downloaded_bytes"]
        if size is None:
            entry["status"] = "skipped_unknown_size"
            entry["reason"] = "Server did not provide Content-Length; refusing an unbounded download."
        elif size > remaining:
            entry["status"] = "skipped_budget"
            entry["reason"] = f"Whole file needs {size} bytes; only {remaining} remain."
        else:
            target = OUT / name
            temp = OUT / (name + ".part")
            req = urllib.request.Request(url, headers={"User-Agent": "DCOMM-A11-public-records-ingest/1.0"})
            h = hashlib.sha256()
            got = 0
            try:
                with urllib.request.urlopen(req, timeout=90) as resp, open(temp, "wb") as f:
                    while True:
                        chunk = resp.read(1024 * 1024)
                        if not chunk:
                            break
                        got += len(chunk)
                        if got > size or manifest["downloaded_bytes"] + got > BUDGET:
                            raise RuntimeError("Download exceeded declared size or total byte budget.")
                        f.write(chunk)
                        h.update(chunk)
                if got != size:
                    raise RuntimeError(f"Length mismatch: expected {size}, received {got}.")
                with zipfile.ZipFile(temp) as zf:
                    bad = zf.testzip()
                    if bad:
                        raise RuntimeError(f"ZIP integrity test failed at {bad}.")
                    entry["zip_members"] = len(zf.infolist())
                temp.replace(target)
                manifest["downloaded_bytes"] += got
                entry.update(status="downloaded_verified", downloaded_bytes=got, sha256=h.hexdigest())
            except Exception:
                if temp.exists():
                    temp.unlink()
                raise
    except Exception as exc:
        entry["status"] = "error"
        entry["error"] = str(exc)
    manifest["sources"].append(entry)
    print(json.dumps(entry, sort_keys=True))
manifest["status"] = "completed_with_errors" if any(x["status"] == "error" for x in manifest["sources"]) else "completed"
manifest["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"final_status": manifest["status"], "downloaded_bytes": manifest["downloaded_bytes"], "budget_bytes": BUDGET}))
