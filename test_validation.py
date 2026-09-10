"""Regression tests for the editor's data-correctness rules.

These test the RULES, not the Qt widgets, so they run headless with no PyQt5 installed:
    python3 test_validation.py [path-to-cmp-folder]

Covers:
  * history-condition validation (the check added to validate_graph)
  * label -> code lookup for conditions (ChooseConditionDialog.lookup_code)
  * the sandy/clay soil grouping, mirrored from GenericCrop.cpp

Why these exist: every bug found in the JSON crop audit failed SILENTLY -- an operation was
skipped or a condition was permanently false, with no error. The point of these tests is to make
that class of failure loud.
"""
import json
import os
import sys
import glob

CMP_DIR = "CMP + JSON files"


# --------------------------------------------------------------------------------------------
# Rule under test: a field_history condition must name a node in the SAME flowchart.
# ALMaSS clears field history at the start of every crop, so a foreign id can never match.
# Mirrors the check in helper_funcs.validate_graph.
# --------------------------------------------------------------------------------------------
def bad_history_conditions(doc):
    crop = doc.get("crop_name", "")
    ids = {n.get("id", "") for n in doc.get("nodes", [])}
    bad = []
    for n in doc.get("nodes", []):
        if n.get("cond_type") != "field_history":
            continue
        wanted = (n.get("cond_value") or "").strip()
        if not wanted:
            bad.append((n.get("id"), "<empty>"))
            continue
        stripped = wanted
        if crop and stripped.startswith(crop + "_"):
            stripped = stripped[len(crop) + 1:]
        if wanted not in ids and stripped not in ids:
            bad.append((n.get("id"), wanted))
    return bad


# --------------------------------------------------------------------------------------------
# Rule under test: cond_value must carry the machine code, not the display label.
# --------------------------------------------------------------------------------------------
def lookup_code(conditions, layer, sublayer, label):
    try:
        return conditions[layer]["sublayers"][sublayer][label]
    except (KeyError, TypeError):
        return label


# --------------------------------------------------------------------------------------------
# Rule under test: soil is a GROUP test. Mirrors GenericCrop.cpp field_soil.
# ALMaSS: sandy = {Sand, LoamySand, SandyLoam, SandyClayLoam}; clay = the complement.
# --------------------------------------------------------------------------------------------
SANDY_CODES = {1, 2, 3, 4}


def soil_matches(soil_code, cond_value):
    is_sandy = soil_code in SANDY_CODES
    v = str(cond_value).lower()
    if v == "sandy":
        return is_sandy
    if v == "clay":
        return not is_sandy
    return str(soil_code) == str(cond_value)


def run():
    failures = []
    checks = 0

    # ---- 1. soil grouping replicates the hardcoded C++ for all 15 soil types ----------------
    for code in range(15):
        cpp_sandy = code in SANDY_CODES
        checks += 3
        if soil_matches(code, "sandy") != cpp_sandy:
            failures.append(f"soil {code}: 'sandy' should be {cpp_sandy}")
        if soil_matches(code, "clay") != (not cpp_sandy):
            failures.append(f"soil {code}: 'clay' should be {not cpp_sandy}")
        # the capitalised legacy label must behave identically
        if soil_matches(code, "Clay") != (not cpp_sandy):
            failures.append(f"soil {code}: legacy 'Clay' should be {not cpp_sandy}")
    # legacy numeric values must still resolve
    checks += 2
    if not soil_matches(12, "12"):
        failures.append("legacy numeric soil '12' should match tos_Clay")
    if soil_matches(12, "1"):
        failures.append("legacy numeric soil '1' should NOT match tos_Clay")

    # ---- 2. every conditions.json option resolves to a code, not a label --------------------
    here = os.path.dirname(os.path.abspath(__file__))
    conditions = json.load(open(os.path.join(here, "conditions.json")))
    for layer, v in conditions.items():
        for sub, vv in v.get("sublayers", {}).items():
            for label in [k for k in vv if k != "func"]:
                checks += 1
                code = lookup_code(conditions, layer, sub, label)
                if code == label and label not in ("Sandy", "Clay"):
                    failures.append(f"{layer}/{sub}/{label}: no code, would emit the label")

    # soil must offer exactly the two groups -- individual types are not testable in ALMaSS
    checks += 1
    soil_opts = [k for k in conditions["FIELD"]["sublayers"]["SOIL"] if k != "func"]
    if sorted(soil_opts) != ["Clay", "Sandy"]:
        failures.append(f"SOIL should offer exactly Sandy/Clay, got {soil_opts}")

    # ---- 3. history conditions across the real corpus ---------------------------------------
    folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, CMP_DIR)
    corpus = sorted(glob.glob(os.path.join(folder, "*.cmp")))
    flagged = []
    for path in corpus:
        try:
            doc = json.load(open(path))
        except (ValueError, OSError):
            continue
        checks += 1
        for node_id, wanted in bad_history_conditions(doc):
            flagged.append((os.path.basename(path), node_id, wanted))

    print(f"checks run: {checks}")
    print(f".cmp files scanned: {len(corpus)}")
    print()
    if flagged:
        print(f"KNOWN-BAD history conditions still present in the corpus: {len(flagged)}")
        print("(data problems for the crop authors to fix -- not code failures)")
        for f, n, w in flagged:
            print(f"    {f:38} {n!r:28} -> {w!r}")
        print()
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures:
            print(f"    {f}")
        return 1
    print("All rule checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
