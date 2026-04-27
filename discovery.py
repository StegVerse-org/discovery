"""
discovery.py
StegVerse repo discovery and manifest-driven file placement.
Uses StegDB as canonical authority.
"""

import os, json, hashlib, fnmatch
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class FileDiscovery:
    path: str
    repo: str
    relative_path: str
    size: int
    hash: str
    pattern_match: str
    suggested_target: str
    confidence: float


@dataclass
class PlacementManifest:
    manifest_id: str
    timestamp: str
    source_repo: str
    target_repo: str
    files: List[Dict[str, Any]]
    gate_result: Optional[Dict[str, Any]] = None
    receipt_id: Optional[str] = None


class StegDBStub:
    """Stub for StegDB. Replace with real API when live."""
    def __init__(self, endpoint: Optional[str] = None):
        self.endpoint = endpoint or "https://stegdb.stegverse.org"
        self.local_log: List[Dict[str, Any]] = []

    def log_action(self, action_type: str, receipt_id: str, data: Dict[str, Any]) -> bool:
        entry = {"timestamp": datetime.now().isoformat(), "action_type": action_type,
                 "receipt_id": receipt_id, "data": data}
        self.local_log.append(entry)
        print(f"[StegDB] Logged {action_type} — {receipt_id}")
        return True

    def query_gate(self, manifest: PlacementManifest) -> Dict[str, Any]:
        file_count = len(manifest.files)
        if file_count == 0:
            return {"result": "FAIL_CLOSED", "confidence": 1.0, "reasoning": "Empty manifest"}
        if any(f["relative_path"].startswith(".") for f in manifest.files):
            return {"result": "DENY", "confidence": 0.7, "reasoning": "Hidden files detected"}
        return {"result": "ALLOW", "confidence": 0.95, "reasoning": f"Safe placement of {file_count} files"}

    def get_canonical_state(self, repo: str) -> Dict[str, Any]:
        return {"repo": repo, "files": [], "last_sync": datetime.now().isoformat()}


class DiscoveryEngine:
    PATTERNS = {
        "invariant": ["*invariant*.py", "gcat_*.py", "bcat_*.py"],
        "sandbox": ["*sandbox*.py", "ephemeral*.py"],
        "experiment": ["*experiment*.py", "*suite*.py"],
        "core": ["receipt_id.py", "governed_action.py", "governed_mutation.py", "llm_adapter.py"],
        "demo": ["demo_suite_runner.py", "demo_*.py"],
        "ci": ["*.yml", "*.yaml", "ci.txt"],
        "config": ["requirements.txt", "*.cfg", "*.ini"]
    }

    TARGET_MAP = {
        "invariant": "demo-sandbox/invariants/",
        "sandbox": "demo-sandbox/sandbox/",
        "experiment": "demo-sandbox/experiments/",
        "core": "demo-suite-runner/scripts/",
        "demo": "demo-suite-runner/scripts/",
        "ci": ".github/workflows/",
        "config": "root/"
    }

    def __init__(self, stegdb: Optional[StegDBStub] = None):
        self.stegdb = stegdb or StegDBStub()
        self.discoveries: List[FileDiscovery] = []

    def scan_repo(self, repo_path: str, repo_name: str) -> List[FileDiscovery]:
        discoveries = []
        repo_root = Path(repo_path)
        for file_path in repo_root.rglob("*"):
            if not file_path.is_file():
                continue
            rel_path = file_path.relative_to(repo_root)
            file_hash = self._hash_file(file_path)
            for category, patterns in self.PATTERNS.items():
                for pattern in patterns:
                    if fnmatch.fnmatch(file_path.name, pattern):
                        discovery = FileDiscovery(
                            path=str(file_path), repo=repo_name, relative_path=str(rel_path),
                            size=file_path.stat().st_size, hash=file_hash,
                            pattern_match=f"{category}:{pattern}",
                            suggested_target=self.TARGET_MAP.get(category, "unknown/"),
                            confidence=0.9 if category in ["core", "invariant"] else 0.7)
                        discoveries.append(discovery)
                        break
        self.discoveries.extend(discoveries)
        return discoveries

    def generate_manifest(self, source_repo: str, target_repo: str, files: List[FileDiscovery]) -> PlacementManifest:
        manifest_id = f"MANIFEST-{hashlib.sha256(f'{source_repo}-{target_repo}-{datetime.now()}'.encode()).hexdigest()[:16]}"
        file_entries = [{"source_path": f.path, "source_repo": f.repo, "relative_path": f.relative_path,
                        "file_hash": f.hash, "size": f.size, "pattern_match": f.pattern_match,
                        "suggested_target": f.suggested_target, "placement_confidence": f.confidence}
                       for f in files]
        return PlacementManifest(manifest_id, datetime.now().isoformat(), source_repo, target_repo, file_entries)

    def submit_for_approval(self, manifest: PlacementManifest) -> PlacementManifest:
        gate_result = self.stegdb.query_gate(manifest)
        manifest.gate_result = gate_result
        manifest.receipt_id = f"REC-MANIFEST-{manifest.manifest_id}"
        self.stegdb.log_action("MANIFEST_SUBMITTED", manifest.receipt_id,
            {"manifest_id": manifest.manifest_id, "source_repo": manifest.source_repo,
             "target_repo": manifest.target_repo, "file_count": len(manifest.files), "gate_result": gate_result})
        return manifest

    def execute_placement(self, manifest: PlacementManifest, dry_run: bool = True) -> Dict[str, Any]:
        if not manifest.gate_result:
            return {"status": "FAIL_CLOSED", "reasoning": "No gate result"}
        if manifest.gate_result["result"] != "ALLOW":
            self.stegdb.log_action("PLACEMENT_DENIED", manifest.receipt_id,
                {"manifest_id": manifest.manifest_id, "reason": manifest.gate_result["reasoning"]})
            return {"status": "DENIED", "reasoning": manifest.gate_result["reasoning"]}
        executed = []
        failed = []
        for file_entry in manifest.files:
            try:
                if not dry_run:
                    pass  # Actual move logic here
                executed.append(file_entry["relative_path"])
            except Exception as e:
                failed.append({"file": file_entry["relative_path"], "error": str(e)})
        self.stegdb.log_action("PLACEMENT_EXECUTED" if not dry_run else "PLACEMENT_SIMULATED",
                                manifest.receipt_id,
            {"manifest_id": manifest.manifest_id, "executed": len(executed), "failed": failed, "dry_run": dry_run})
        return {"status": "EXECUTED" if not dry_run else "SIMULATED", "executed": executed, "failed": failed, "receipt_id": manifest.receipt_id}

    def _hash_file(self, path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]

    def export_manifest(self, manifest: PlacementManifest, filepath: str):
        data = {"manifest_id": manifest.manifest_id, "timestamp": manifest.timestamp,
                "source_repo": manifest.source_repo, "target_repo": manifest.target_repo,
                "receipt_id": manifest.receipt_id, "gate_result": manifest.gate_result, "files": manifest.files}
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Manifest exported: {filepath}")


def main():
    engine = DiscoveryEngine()
    print("Scanning demo-suite-runner...")
    discoveries = engine.scan_repo(".", "demo-suite-runner")
    print(f"Found {len(discoveries)} matching files")
    for d in discoveries[:10]:
        print(f"  {d.relative_path} → {d.suggested_target} (confidence: {d.confidence})")
    sandbox_files = [d for d in discoveries if "invariant" in d.pattern_match or "sandbox" in d.pattern_match]
    if sandbox_files:
        manifest = engine.generate_manifest("demo-suite-runner", "demo-sandbox", sandbox_files)
        print(f"\nGenerated manifest: {manifest.manifest_id}")
        print(f"Files to migrate: {len(manifest.files)}")
        manifest = engine.submit_for_approval(manifest)
        print(f"Gate result: {manifest.gate_result['result']} — {manifest.gate_result['reasoning']}")
        result = engine.execute_placement(manifest, dry_run=True)
        print(f"Execution: {result['status']} — {len(result['executed'])} files")
        engine.export_manifest(manifest, "placement_manifest.json")


if __name__ == "__main__":
    main()
