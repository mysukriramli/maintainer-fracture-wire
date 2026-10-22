#!/usr/bin/env python3
"""
Maintainer Fracture Wire - Master Orchestration Engine
Predicts open-source library continuity risk, maintainer concentration,
and release cadence decay to emit mitigation directives for AI coding agents.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import List

from core.taxonomy import FractureRecord
from core.fracture_engine import FractureEngine
from connectors.registry_probe import TARGET_PACKAGES, probe_package
from connectors.deps_dev import get_dependent_reach

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DATA_DIR = "data"
ARCHIVE_DIR = os.path.join(DATA_DIR, "archive")
TODAY_FILE = os.path.join(DATA_DIR, "today.json")
QUEUE_FILE = os.path.join(DATA_DIR, "remediation_queue.jsonl")
LLMS_FILE = os.path.join(DATA_DIR, "llms.txt")

def generate_llms_txt(records: List[FractureRecord], now_iso: str) -> str:
    lines = [
        "# Maintainer Fracture Wire",
        f"> Last updated: {now_iso} UTC | Autonomous Package Abandonment & Continuity Radar",
        "> Evaluates open-source package bus factor, release interval decay, and downstream blast radius.",
        "",
        "## Active Maintainer Fracture Directives",
        "| Package | Ecosystem | Fracture Score | Directive | Last Release (Days) | Maintainers | Recommended Alternatives |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for r in records:
        alts = ", ".join(r.alternatives) if r.alternatives else "None specified"
        lines.append(
            f"| **{r.package_name}** | `{r.ecosystem}` | `{r.fracture_probability_score}` | "
            f"`{r.directive.value}` | {r.days_since_last_release:.0f}d | {r.estimated_maintainer_count} | {alts} |"
        )
    return "\n".join(lines) + "\n"

def run():
    logging.info("Starting Maintainer Fracture computation cycle...")
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    date_str = now.strftime("%Y-%m-%d")

    engine = FractureEngine()
    records: List[FractureRecord] = []

    for target in TARGET_PACKAGES:
        eco = target["ecosystem"]
        name = target["name"]
        alts = target.get("alternatives", [])

        meta = probe_package(eco, name)
        if not meta:
            continue

        dependents = get_dependent_reach(eco, name)
        purl = f"pkg:{eco}/{name}@{meta['latest_version']}"

        score, directive, confidence, reasons = engine.evaluate(
            days_since_release=meta["days_since_last_release"],
            maintainer_count=meta["maintainer_count"],
            direct_dependents=dependents,
            is_deprecated=meta.get("is_deprecated", False)
        )

        records.append(FractureRecord(
            package_name=name,
            ecosystem=eco,
            purl=purl,
            latest_version=meta["latest_version"],
            days_since_last_release=meta["days_since_last_release"],
            estimated_maintainer_count=meta["maintainer_count"],
            direct_dependents=dependents,
            fracture_probability_score=score,
            directive=directive,
            confidence=confidence,
            reason_codes=reasons,
            alternatives=alts
        ))

    # Sort descending by fracture risk
    records.sort(key=lambda x: x.fracture_probability_score, reverse=True)

    month_dir = os.path.join(ARCHIVE_DIR, now.strftime("%Y"), now.strftime("%m"))
    os.makedirs(month_dir, exist_ok=True)

    payload = {
        "metadata": {
            "generated_at_utc": now_iso,
            "schema_version": "1.0.0",
            "packages_evaluated": len(records),
            "scoring_rule": "FractureScore = f(ReleaseStaleness, MaintainerConcentration, DownstreamReach)"
        },
        "packages": [r.model_dump() for r in records]
    }

    # 1. Output today.json
    with open(TODAY_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # 2. Output remediation_queue.jsonl
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r.model_dump()) + "\n")

    # 3. Output llms.txt
    llms_content = generate_llms_txt(records, now_iso)
    with open(LLMS_FILE, "w", encoding="utf-8") as f:
        f.write(llms_content)

    # 4. Output historical daily archive
    archive_file = os.path.join(month_dir, f"{date_str}.json")
    with open(archive_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    logging.info(f"Published Maintainer Fracture evaluation for {len(records)} packages to {TODAY_FILE}.")

if __name__ == "__main__":
    run()
