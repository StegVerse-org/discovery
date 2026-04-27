# StegVerse Discovery & Manifest System

## Purpose

Automated repo scanning, manifest generation, and StegDB-governed file placement.

## Flow

```
Scan Repo → Build Manifest → Submit to StegDB Gate → ALLOW → Execute Placement
                                    ↓
                                 DENY/FAIL_CLOSED → Log & Abort
```

## Usage

```python
from discovery import DiscoveryEngine

engine = DiscoveryEngine()
discoveries = engine.scan_repo("./demo-suite-runner", "demo-suite-runner")
manifest = engine.generate_manifest("demo-suite-runner", "demo-sandbox", discoveries)
manifest = engine.submit_for_approval(manifest)
result = engine.execute_placement(manifest, dry_run=False)
```

## Integration

Replace `StegDBStub` with `StegDBClient` from `stegdb/stegdb_wirein.py` when endpoint is live.
