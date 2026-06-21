# StegVerse Discovery

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)

Release: v1.0.0

Discovery and repository-indexing layer for the StegVerse ecosystem.

This repository identifies, tracks, and wires declared components across the distributed architecture. It is a discovery/indexing layer, not an authority-bearing governance kernel.

---

## What it does

- component discovery for StegVerse repositories and services;
- state and availability monitoring for ecosystem nodes;
- manifest-aware repository indexing;
- StegDB / monitoring integration support;
- architecture validation support through GSL-compatible manifests.

---

## Install

```bash
pip install stegverse-discovery
```

---

## Quick start

```python
from discovery import discover_repos, wire_to_stegdb

repos = discover_repos(org="StegVerse-org")
wire_to_stegdb(repos)
```

---

## Integration

| System | Role |
|---|---|
| `StegVerse-org/stegverse-gsl` | Manifest and structure validation. |
| `StegVerse-org/demo_ingest_engine` | Ingestion state tracking. |
| `StegVerse-org/StegVerse-SDK` | SDK component discovery. |
| StegDB | Monitoring database / state sink. |
| Trust Kernel | Private governance node; discovery may reference it but does not expose its authority logic. |

---

## Boundary rule

Discovery identifies declared components and reports observed state. It does not create execution authority, admission authority, endorsement, compatibility recognition, provenance recognition, collaboration, or validation.

---

## Links

- Repository: https://github.com/StegVerse-org/discovery
- Issues: https://github.com/StegVerse-org/discovery/issues
