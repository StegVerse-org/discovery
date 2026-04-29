# StegVerse Discovery

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/github/license/StegVerse-org/discovery)

Release: v1.0.0

Discovery and monitoring layer for the StegVerse ecosystem. Identifies, tracks, and wires in components across the distributed architecture.

## What It Does

- **Component discovery** — Auto-detects StegVerse repos and services
- **State monitoring** — Tracks health and status of ecosystem nodes
- **StegDB integration** — Wires monitoring data into the canonical database
- **Architecture validation** — Verifies repo structure against governance manifests

## Install

```bash
pip install stegverse-discovery
```

## Quick Start

```python
from discovery import discover_repos, wire_to_stegdb

# Discover all StegVerse org repos
repos = discover_repos(org="StegVerse-org")

# Wire monitoring to StegDB
wire_to_stegdb(repos)
```

## Integration

| System | Role |
|--------|------|
| StegDB | Canonical monitoring database |
| demo_ingest_engine | Ingestion state tracking |
| StegVerse-SDK | SDK component discovery |
| Trust Kernel | Governance node identification |

## Links

- Repository: https://github.com/StegVerse-org/discovery
- Issues: https://github.com/StegVerse-org/discovery/issues

---

**StegVerse: Execution is not assumed. Execution is admitted.**
