from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
plan = (ROOT / "PHASE7_PLAN.md").read_text(encoding="utf-8")
restart = (ROOT / "RESTART_PROTOCOL.md").read_text(encoding="utf-8")
dictionary = (ROOT / "research_artifacts/phase7/FEATURE_DICTIONARY.md").read_text(encoding="utf-8")

required = [
    "2026-05-19", "2026-05-20", "26 eligible weekly observations",
    "option-implied skew", "India VIX", "FII/FPI", "DII",
    "market breadth", "USDINR", "crude", "gold",
    "regime/volatility", "news", "corporate-action",
    "bootstrap 95% CI", "Profit factor > 1.20",
    "Maximum drawdown is not worse", "No post-hoc threshold"
]
text = "\n".join([plan, restart, dictionary])
missing = [x for x in required if x.lower() not in text.lower()]
if missing:
    raise SystemExit("Missing preregistration requirements: " + ", ".join(missing))

if not re.search(r"source_timestamp.*availability_timestamp.*feature_cutoff_timestamp", dictionary, re.S):
    raise SystemExit("Feature dictionary is missing timestamp lineage fields.")

print("Phase 7 protocol check: PASS")
print("No fresh-period performance evaluation is performed by this check.")
