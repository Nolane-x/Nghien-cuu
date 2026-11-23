#!/usr/bin/env python3
"""Execute the checksum-pinned Wilbers Figure 2 stats_fig2.py unchanged.

Only the original Windows workbook paths and anova_lm import are wrapped.
The author's four OLS/Type-II ANOVA tables are captured as printed; a separate
cluster-robust interaction test groups residuals by recording filename.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import math
import runpy
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

FILES = {
    "na": {
        "id": 318668, "path": "Figure2/Na_data_fig2.xlsx", "bytes": 548562,
        "sha1": "cd702d7f1ca65b0b88a2565f289740546902e36b",
        "sha256": "2fac600523d596a4dccbe167d3283b2e506dfdb9c7b1caef2a490c2c5dff184a",
    },
    "k": {
        "id": 318669, "path": "Figure2/K_data_fig2.xlsx", "bytes": 302011,
        "sha1": "287720f8db3b20b167edd9e639dd67b0a1194def",
        "sha256": "f00714c534c9658b8c07d2a473d39b2fd5a99c392e6e2ab50fb52fbb3b6ca74d",
    },
    "stats_script": {
        "id": 318531, "path": "Figure2/stats_fig2.py", "bytes": 2282,
        "sha1": "45ffcd0be45743c7937d3e0a323ac52832aa845e",
        "sha256": "e220f0e8603976b99d67120e2aa91c8828d6e47bc3dc08b7b20cf4e3ce49fa5a",
    },
}
BASE = "https://dataverse.nl/api"


def fetch_verified(spec: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    with urllib.request.urlopen(f"{BASE}/files/{spec['id']}", timeout=60) as response:
        metadata = json.loads(response.read())["data"]["dataFile"]
    if metadata["checksum"]["value"] != spec["sha1"] or int(metadata["filesize"]) != spec["bytes"]:
        raise RuntimeError(f"Dataverse metadata changed for {spec['path']}")
    attempts = []
    for url in (
        f"{BASE}/access/datafile/{spec['path']}/{spec['id']}",
        f"{BASE}/access/datafile/{spec['id']}",
    ):
        request = urllib.request.Request(url, headers={
            "User-Agent": "AMSN-Wilbers-Figure2-stats-reproduction/1.0",
            "Cache-Control": "no-cache", "Pragma": "no-cache", "Accept": "*/*",
        })
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                payload = response.read()
                content_type = response.headers.get("Content-Type")
                final_url = response.url.split("?", 1)[0]
            sha1, sha256 = hashlib.sha1(payload).hexdigest(), hashlib.sha256(payload).hexdigest()
            attempts.append({"url": url, "final_url": final_url, "bytes": len(payload),
                             "content_type": content_type, "sha1": sha1, "sha256": sha256})
            if len(payload) == spec["bytes"] and sha1 == spec["sha1"] and sha256 == spec["sha256"]:
                return payload, {"official_sha1": metadata["checksum"]["value"],
                                 "official_bytes": int(metadata["filesize"]), "attempts": attempts}
        except Exception as exc:
            attempts.append({"url": url, "error": repr(exc)})
    raise RuntimeError("Dataverse file failed both SHA-1 and SHA-256 checks: " + json.dumps(attempts))


def js(value: Any) -> Any:
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if value is None or isinstance(value, (str, int, bool)):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return str(value)


def table_rows(frame: Any) -> list[dict[str, Any]]:
    result = []
    for term, row in frame.iterrows():
        item = {"term": str(term)}
        item.update({str(col): js(value) for col, value in row.items()})
        result.append(item)
    return result


def interaction_p(capture: dict[str, Any]) -> float | None:
    for row in capture["anova_table"]:
        if ":" in row["term"] and "APnr" in row["term"]:
            value = row.get("PR(>F)")
            return float(value) if value is not None else None
    return None


def compare_article_p(p: float | None, reference: dict[str, Any]) -> dict[str, Any]:
    if p is None:
        return {"available": False, "reference": reference}
    if reference["kind"] == "less_than":
        return {"available": True, "reference": reference, "matches": p < reference["threshold"]}
    return {"available": True, "reference": reference,
            "within_tolerance": abs(p - reference["value"]) <= reference["tolerance"],
            "absolute_difference": abs(p - reference["value"])}


def cluster_interaction_test(result: Any) -> dict[str, Any]:
    import numpy as np
    frame = result.model.data.frame
    design = result.model.data.design_info
    terms = [t for t in design.term_name_slices if ":" in t and "APnr" in t and "C(" in t]
    if len(terms) != 1:
        raise RuntimeError(f"Could not identify one AP-by-species interaction: {terms}")
    term = terms[0]
    sl = design.term_name_slices[term]
    cols = list(range(sl.start, sl.stop))
    restriction = np.zeros((len(cols), len(result.params)))
    for r, c in enumerate(cols):
        restriction[r, c] = 1.0
    groups = frame["Filename"].astype(str).to_numpy()
    robust = result.get_robustcov_results(cov_type="cluster", groups=groups,
                                          use_correction=True, df_correction=True)
    test_result = robust.f_test(restriction)
    return {
        "method": "cluster-robust covariance by recording filename (sensitivity only)",
        "cluster_variable": "Filename",
        "cluster_count": int(frame["Filename"].nunique()),
        "observation_count": int(result.nobs),
        "interaction_term": term,
        "parameters": [result.model.exog_names[c] for c in cols],
        "f_statistic": js(test_result.fvalue),
        "df_num": js(getattr(test_result, "df_num", None)),
        "df_denom": js(getattr(test_result, "df_denom", None)),
        "p_value": js(test_result.pvalue),
        "not_authors_original_test": True,
    }


def reproduce(script_path: Path, data_dir: Path) -> tuple[list[dict[str, Any]], str]:
    import pandas as pd
    import statsmodels
    import statsmodels.stats.anova as anova_module

    old_read_excel, old_anova = pd.read_excel, anova_module.anova_lm
    captured: list[dict[str, Any]] = []

    def mapped_read_excel(source: Any, *args: Any, **kwargs: Any) -> Any:
        if isinstance(source, (str, Path)):
            normalized = str(source).replace("\\", "/")
            if normalized.startswith("Data/"):
                source = data_dir / Path(normalized).name
        return old_read_excel(source, *args, **kwargs)

    def capture_anova(model: Any, *args: Any, **kwargs: Any) -> Any:
        table = old_anova(model, *args, **kwargs)
        data = model.model.data.frame
        captured.append({
            "formula": getattr(model.model, "formula", None),
            "anova_type": kwargs.get("typ", 1),
            "anova_table": table_rows(table),
            "observations": int(model.nobs),
            "recordings": int(data["Filename"].nunique()),
            "r_squared": js(model.rsquared),
            "residual_df": js(model.df_resid),
            "cluster_robust_interaction": cluster_interaction_test(model),
        })
        return table

    pd.read_excel = mapped_read_excel
    anova_module.anova_lm = capture_anova
    stdout = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout):
            runpy.run_path(str(script_path), run_name="__main__")
    finally:
        pd.read_excel, anova_module.anova_lm = old_read_excel, old_anova
    return captured, stdout.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("wilbers-figure2-stats-reproduction.json"))
    args = parser.parse_args()
    payloads, integrity = {}, {}
    for name, spec in FILES.items():
        payloads[name], integrity[name] = fetch_verified(spec)

    import pandas, scipy, statsmodels
    with tempfile.TemporaryDirectory(prefix="amsn-wilbers-fig2-stats-") as tmp:
        root = Path(tmp)
        data_dir = root / "Data"
        data_dir.mkdir()
        (data_dir / "Na_data_fig2.xlsx").write_bytes(payloads["na"])
        (data_dir / "K_data_fig2.xlsx").write_bytes(payloads["k"])
        stats_path = root / "stats_fig2.py"
        stats_path.write_bytes(payloads["stats_script"])
        captures, stdout = reproduce(stats_path, data_dir)

    if len(captures) != 4:
        raise RuntimeError(f"Expected four Type-II ANOVA results, got {len(captures)}")
    expected = [
        ("Na AP1-200", "relative_amp ~ APnr*C(Species) - C(Species)", 39200,
         {"kind": "less_than", "threshold": 1e-323, "printed": "p < 10^-323"}),
        ("Na AP1-5", "relative_amp ~ APnr*C(Species) - C(Species)", 980,
         {"kind": "less_than", "threshold": 1e-53, "printed": "p < 10^-53"}),
        ("K AP1-200", "amp ~ APnr*C(species)", 5000,
         {"kind": "less_than", "threshold": 1e-45, "printed": "p < 10^-45"}),
        ("K AP1-5", "amp ~ APnr*C(species)", 125,
         {"kind": "approximately", "value": 0.07, "tolerance": 0.015, "printed": "p = 0.07"}),
    ]
    comparisons = []
    for capture, (label, formula, observations, article) in zip(captures, expected):
        if capture["formula"] != formula:
            raise RuntimeError(f"Formula mismatch for {label}: {capture['formula']}")
        if capture["observations"] != observations:
            raise RuntimeError(f"Observation count mismatch for {label}: {capture['observations']} != {observations}")
        p = interaction_p(capture)
        comparisons.append({"label": label, "original_ols_interaction_p": p,
                             "article_reference": compare_article_p(p, article),
                             "cluster_robust_interaction": capture["cluster_robust_interaction"]})

    output = {
        "schema_version": 1,
        "status": "original_stats_fig2_py_executed_four_type_ii_anova_tables_captured",
        "runtime_eligible": False,
        "source_files": {
            name: {"id": FILES[name]["id"], "path": FILES[name]["path"],
                   "bytes": len(payloads[name]), "sha1": hashlib.sha1(payloads[name]).hexdigest(),
                   "sha256": hashlib.sha256(payloads[name]).hexdigest(), "download": integrity[name]}
            for name in FILES
        },
        "environment": {"python": __import__("platform").python_version(), "pandas": pandas.__version__,
                        "scipy": scipy.__version__, "statsmodels": statsmodels.__version__},
        "original_script": {"executed_unchanged": True, "stdout": stdout, "tables": captures},
        "comparisons": comparisons,
        "caveats": [
            "The four OLS/Type-II ANOVA tables reproduce the original source analysis.",
            "Repeated AP observations from the same recording are not modelled as repeated measures in the original OLS.",
            "Cluster-robust-by-Filename interaction tests are separate sensitivity results, not author-reported p-values.",
            "Na stacks all four APwave groups without adding an APwave term to the original formula.",
            "K uses only normalized human-input waveform condition _h_n_.",
            "This is a statistical reproduction, not replay of raw AP-clamp current traces.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "environment": output["environment"],
                      "comparisons": comparisons, "output": str(args.output)},
                     indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
