from __future__ import annotations

import json
import os
import pathlib
import urllib.request

import pandas as pd
import pyarrow.parquet as pq
import requests

OUT = pathlib.Path("research_artifacts/phase1-smoke")
OUT.mkdir(parents=True, exist_ok=True)

HF_URL = "https://huggingface.co/datasets/thetrademarkk/india-index-options-1m/resolve/main/options/NIFTY/2021-05-27.parquet"
SPOT_URL = "https://raw.githubusercontent.com/technovusin/nifty50-historical-data/main/1min/2024/NIFTY50_1min_2024.csv"

headers = {}
if os.environ.get("HF_TOKEN"):
    headers["Authorization"] = f"Bearer {os.environ['HF_TOKEN']}"

opt_path = OUT / "sample_option.parquet"
with requests.get(HF_URL, headers=headers, stream=True, timeout=120) as r:
    r.raise_for_status()
    with opt_path.open("wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

pf = pq.ParquetFile(opt_path)
opt_schema = {"columns": [str(x) for x in pf.schema_arrow.names], "rows": pf.metadata.num_rows}
opt_df = pd.read_parquet(opt_path)
opt_schema["dtypes"] = {k: str(v) for k, v in opt_df.dtypes.items()}
opt_schema["head"] = opt_df.head(5).to_dict(orient="records")
opt_schema["tail"] = opt_df.tail(5).to_dict(orient="records")

spot_path = OUT / "sample_spot.csv"
urllib.request.urlretrieve(SPOT_URL, spot_path)
spot_df = pd.read_csv(spot_path)
spot_info = {
    "columns": [str(x) for x in spot_df.columns],
    "rows": int(len(spot_df)),
    "dtypes": {k: str(v) for k, v in spot_df.dtypes.items()},
    "head": spot_df.head(3).to_dict(orient="records"),
    "tail": spot_df.tail(3).to_dict(orient="records"),
}

report = {"option_sample": opt_schema, "spot_2024": spot_info}
(OUT / "source_smoke_report.json").write_text(json.dumps(report, indent=2, default=str))
print(json.dumps(report, indent=2, default=str))
