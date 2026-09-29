import difflib
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF
import math
import sys, os, re, json

# ------------------------------------------------------------------------------------------------
# HELPER FUNCTIONS FOR EXPORT AND SAVING
# ------------------------------------------------------------------------------------------------
def generate_json(all_nodes, crop_name, author, date, filename, comments=None, veg_patchy=False, rotation=None):
    # Metadata stays at the top level
    data = {
        "crop_name": crop_name,
        "author": author,
        "last_modified": date,
        "veg_patchy": bool(veg_patchy),
        "nodes": [],      # this will hold all node objects
        "comments": []    # this will hold all comment boxes
    }

    # Rotation timing, when the author has supplied it.
    for k, v in (rotation or {}).items():
        data[k] = v

    # Save nodes
    for node in all_nodes:
        node_data = {
            "type": node.__class__.__name__,
            "x": node.scenePos().x(),
            "y": node.scenePos().y(),
            "width": getattr(node, "width", 120),
            "height": getattr(node, "height", 60),
            "id": node.id_text.toPlainText() if hasattr(node, "id_text") else "",
            "name": node.name_text.toPlainText() if hasattr(node, "name_text") else "",
            "dates": getattr(node, "dates_text", "+0d - +1d").toPlainText() if hasattr(node, "dates_text") else "+0d - +0d",
            "outgoing": []
        }

        if node.__class__.__name__ == "CondNode":
            node_data["cpp_cond"] = node.cpp_cond
            node_data["cond_type"] = node.cond_type
            node_data["cond_value"] = node.cond_value
            node_data["cond_op"] = getattr(node, "cond_op", "")

        if node.__class__.__name__ == "OpNode":
            node_data["clears_patchy"] = bool(getattr(node, "clears_patchy", False))
            if getattr(node, "op_value", -1) >= 0:
                node_data["op_value"] = int(node.op_value)

        if node.__class__.__name__ == "CatchCropNode":
            node_data["catch_crop"] = getattr(node, "catch_crop", "conventional")

        for arrow in node.outgoing_arrows:
            if arrow.end_node:
                destination_id = arrow.end_node.id_text.toPlainText() if hasattr(arrow.end_node, "id_text") else "no_id"
            else:
                destination_id = ""

            branching_condition = arrow.text_item.toPlainText() if arrow.text_item else ""

            arrow_data = {
                "destination_type": arrow.end_node.__class__.__name__ if arrow.end_node else "",
                "destination_id": destination_id,
                "branching_condition": branching_condition,
                "bend_points": [[bp.pos().x(), bp.pos().y()] for bp in arrow.bend_points]
            }

            node_data["outgoing"].append(arrow_data)

        data["nodes"].append(node_data)

    # Save comments if provided
    if comments:
        for comment in comments:
            data["comments"].append(comment)

    # Write the JSON to file
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    return data
# ------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------
def generate_almass_json(all_nodes, crop_name, filename, veg_patchy=False, rotation=None):
    start_node = None
    others = []
    for n in all_nodes:
        if n.id_text.toPlainText() == "START":
            start_node = n
        else:
            others.append(n)
    ordered = [start_node] + others if start_node else all_nodes

    data = {"crop_name": crop_name, "veg_patchy": bool(veg_patchy), "nodes": []}
    # Operation windows for the rotation handoff. Absent means the crop takes no part in the
    # rotation's timing, which is how every crop behaved before this existed.
    for k, v in (rotation or {}).items():
        if v is not None:
            data[k] = v
    nodes_data = []

    code_counter = 1
    for node in ordered:
        node_id = node.id_text.toPlainText()
        if node_id == "START":
            earliest = getattr(node, "dates_text", "+0d").toPlainText() if hasattr(node, "dates_text") else "+0d"
            latest = ""
        elif node_id == "END":
            earliest = "+0d"
            latest = "+1d"
        else:
            dates_str = getattr(node, "dates_text", "+0d - +0d").toPlainText() if hasattr(node, "dates_text") else "+0d - +0d"
            earliest, latest = [part.strip() for part in dates_str.split("-", 1)]

        node_data = {
            "type": node.__class__.__name__,
            "code": code_counter,
            "id": crop_name + "_" + node_id,
            "name": node.name_text.toPlainText(),
            "earliest": earliest,
            "latest": latest,
            "outgoing": []
        }

        if node.__class__.__name__ == "CondNode":
            node_data["cond_type"] = node.cond_type
            node_data["cond_value"] = node.cond_value
            # Comparison used by numeric conditions. Empty means "==", which is how every
            # condition behaved before operators existed.
            node_data["cond_op"] = getattr(node, "cond_op", "")

        if node.__class__.__name__ == "OpNode":
            # Harvest, ploughing and topping end a crop's patchiness in the hardcoded crops.
            node_data["clears_patchy"] = bool(getattr(node, "clears_patchy", False))
            # Only written when the author set one; absent means the operation's own default.
            if getattr(node, "op_value", -1) >= 0:
                node_data["op_value"] = int(node.op_value)

        if node.__class__.__name__ == "CatchCropNode":
            # "conventional" / "organic" rather than the C++ enum name, so renaming an enum
            # cannot invalidate authored crop files.
            node_data["catch_crop"] = getattr(node, "catch_crop", "conventional")

        nodes_data.append((node, node_data))
        code_counter += 1

    for node, node_data in nodes_data:
        if node.id_text.toPlainText() != "END":
            for arrow in node.outgoing_arrows:
                dest_id = arrow.end_node.id_text.toPlainText() if arrow.end_node and hasattr(arrow.end_node, "id_text") else ""
                dest_code = None
                dest_earliest = None
                for n, nd in nodes_data:
                    if n.id_text.toPlainText() == dest_id:
                        dest_code = nd["code"]
                        dest_earliest = nd["earliest"]
                        dest_latest = nd["latest"]
                        break

                arrow_data = {
                    "destination_type": arrow.end_node.__class__.__name__ if arrow.end_node else "",
                    "destination_id": crop_name + "_" + dest_id,
                    "destination_code": dest_code,
                    "destination_earliest": dest_earliest,
                    "destination_latest": dest_latest,
                    "branching_condition": arrow.text_item.toPlainText() if arrow.text_item else ""
                }
                node_data["outgoing"].append(arrow_data)

        data["nodes"].append(node_data)

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    return data
# ------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
# ------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------
# HELPER FUNC FOR VALIDATION LOGIC
# ------------------------------------------------------------------------------------------------
def validate_graph(op_nodes, prob_nodes, cond_nodes, crop_name, author, catch_crop_nodes=None,
                   rotation=None, reference=None, known_crops=None):
    warnings = []
    catch_crop_nodes = catch_crop_nodes or []

    # A catch-crop node replaces END: the crop continues into the catch crop rather than
    # finishing, so having both is contradictory and having outgoing arrows is meaningless.
    for ccn in catch_crop_nodes:
        if len(ccn.outgoing_arrows) > 0:
            warnings.append(
                "⚠ <b>WARNING:</b> the catch crop node has outgoing arrows. It ends the flowchart, "
                "so nothing can follow it."
            )
        if getattr(ccn, "catch_crop", "") not in ("conventional", "organic"):
            warnings.append(
                "⚠ <b>WARNING:</b> the catch crop node must be either conventional or organic."
            )
    if catch_crop_nodes and any(n.name_text.toPlainText() == "END" for n in op_nodes):
        warnings.append(
            "⚠ <b>WARNING:</b> this flowchart has both an END node and a catch crop node. "
            "A crop that hands over to a catch crop should use the catch crop node instead of END."
        )

    op_names = [op_node.name_text.toPlainText() for op_node in op_nodes]
    ids = [node.id_text.toPlainText() for node in (op_nodes + prob_nodes + cond_nodes)]
    all_nodes = op_nodes + prob_nodes + cond_nodes

    if crop_name == "":
        warnings.append("⚠ <b>WARNING:</b> no crop's name defined.")

    if author == "":
        warnings.append("⚠ <b>WARNING:</b> no author's name defined.")

    if "START" not in op_names:
        warnings.append("⚠ <b>WARNING:</b> no operation named 'START' exists.")

    # A catch crop node ends the flowchart as END does.
    if "END" not in op_names and not catch_crop_nodes:
        warnings.append("⚠ <b>WARNING:</b> no operation named 'END' exists.")

    if len(ids) != len(set(ids)):
        warnings.append("⚠ <b>WARNING:</b> two or more Nodes share the same ID.")

    for node in all_nodes:
        if (node.name != "START") and (node.name != "END"):
            if len(node.incoming_arrows) <= 0:
                warnings.append("⚠ <b>WARNING:</b> node '" + node.id_text.toPlainText() + "' has no incoming arrows, thus is never executed.")

    for prob_node in prob_nodes:
        total_flow = 0.0
        for arrow in prob_node.outgoing_arrows:
            flow_str = arrow.text_item.toPlainText().strip()
            if not re.fullmatch(r'\d{1,2}%', flow_str):
                warnings.append(
                    "⚠ <b>WARNING:</b> one of your arrows has an invalid probability format. Must be a percentage in the format XX%."
                )
            try:
                total_flow += float(flow_str.replace('%', ''))
            except ValueError:
                pass
        if abs(total_flow - 100.0) > 0.01:
            warnings.append(
                "⚠ <b>WARNING:</b> Node '" + prob_node.id_text.toPlainText() + "' has an outgoing probability flow different than 100%."
            )

    for cond_node in cond_nodes:
        outgoing = cond_node.outgoing_arrows
        if len(outgoing) != 2:
            warnings.append(
                "⚠ <b>WARNING:</b> Node '" + cond_node.id_text.toPlainText() + "' does not have exactly 2 outgoing arrows."
            )
            break
        texts = [arrow.text_item.toPlainText().strip().upper() for arrow in outgoing]
        if "YES" not in texts or "NO" not in texts:
            warnings.append(
                "⚠ <b>WARNING:</b> Node '" + cond_node.id_text.toPlainText() + "' must have one arrow labeled 'YES' and one labeled 'NO'."
            )
    pattern1 = r'\d{2}/\d{2} - \d{2}/\d{2}'
    pattern2 = r'\+\d+d - \d{2}/\d{2}'
    pattern3 = r'\d{2}/\d{2}'

    # A field_history condition asks "has operation <id> already been performed by THIS crop?".
    # ALMaSS clears the field's history at the start of every crop (GenericCrop::ExecuteStartNode),
    # so the id must name a node in this same flowchart -- an id belonging to another crop can
    # never match and the condition silently takes the NO branch forever.
    # The stored cond_value carries no crop prefix; the exporter adds the prefix to node ids only.
    # So compare against the bare ids, and also accept a value the author wrote with this crop's
    # own prefix already attached.
    for cond_node in cond_nodes:
        if getattr(cond_node, "cond_type", "") != "field_history":
            continue
        wanted = (getattr(cond_node, "cond_value", "") or "").strip()
        node_id = cond_node.id_text.toPlainText()
        if not wanted:
            warnings.append(
                "⚠ <b>WARNING:</b> Node '" + node_id + "' is a history condition but names no operation."
            )
            continue
        stripped = wanted
        if crop_name and stripped.startswith(crop_name + "_"):
            stripped = stripped[len(crop_name) + 1:]
        if wanted not in ids and stripped not in ids:
            warnings.append(
                "⚠ <b>WARNING:</b> Node '" + node_id + "' asks about operation '" + wanted
                + "', which is not a node in this flowchart. History conditions can only refer to "
                + "operations of the same crop, so this branch would never be taken."
            )

    for op_node in op_nodes:
        name = op_node.name_text.toPlainText()
        dates = op_node.dates_text.toPlainText().strip()
        if name not in ("START", "END"):
            if not re.fullmatch(pattern1, dates) and not re.fullmatch(pattern2, dates):
                warnings.append(
                    "⚠ <b>WARNING:</b> Node '" + op_node.id_text.toPlainText() + "' has an invalid date format. Must be 'dd/MM - dd/MM' or '+XXd - dd/MM'."
                )
        elif name == "START" and not re.fullmatch(pattern3, dates):
            warnings.append(
                "⚠ <b>WARNING:</b> the Start Node has an invalid date format. Must be 'dd/MM' to indicate the crop cultivation start."
            )

    warnings += _validate_against_almass(op_nodes, prob_nodes, cond_nodes, catch_crop_nodes,
                                         crop_name, rotation, reference, known_crops)
    return warnings
# ------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------
# CHECKS LEARNT FROM RUNNING THE PLANS IN ALMaSS (2026-09)
# ------------------------------------------------------------------------------------------------
_DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def _bad_dates(text):
    """dd/MM dates in text that do not exist (31/09). ALMaSS does not reject them: it quietly
    moves them to the next day (31/09 becomes 1 October)."""
    bad = []
    for d, m in re.findall(r"\b(\d{2})/(\d{2})\b", text or ""):
        d, m = int(d), int(m)
        if not (1 <= m <= 12 and 1 <= d <= _DAYS_IN_MONTH[m - 1]):
            bad.append(f"{d:02d}/{m:02d}")
    return bad


def _validate_against_almass(op_nodes, prob_nodes, cond_nodes, catch_crop_nodes, crop_name,
                             rotation, reference, known_crops):
    """Problems found only by running the plans in ALMaSS, now checked when validating."""
    warnings = []
    W = "⚠ <b>WARNING:</b> "
    catch_crop_nodes = catch_crop_nodes or []
    label = lambda n: n.id_text.toPlainText()
    name = lambda n: n.name_text.toPlainText()
    is_end = lambda n: n in catch_crop_nodes or name(n) == "END"
    kids = lambda n: [a.end_node for a in n.outgoing_arrows if getattr(a, "end_node", None) is not None]

    # 1. Every outcome must be able to reach END. A field whose crop takes a branch that never
    #    reaches END keeps that crop for ever, and ALMaSS stops the run after 800 days. A branch
    #    that ends while another thread carries on to END is fine (a side thread), so only a
    #    probability or condition outcome with no way at all to END is reported.
    memo = {}
    def possible(n, stack=()):
        if id(n) in memo:
            return memo[id(n)]
        if id(n) in stack:
            return False
        r = is_end(n) or any(possible(c, stack + (id(n),)) for c in kids(n))
        memo[id(n)] = r
        return r
    for n in prob_nodes + cond_nodes:
        if not possible(n):
            continue
        for a in n.outgoing_arrows:
            end = getattr(a, "end_node", None)
            if end is not None and not possible(end):
                lab = a.text_item.toPlainText().strip() if a.text_item else ""
                warnings.append(W + f"the '{lab}' branch of node '{label(n)}' (to '{label(end)}') "
                                "never reaches END. A field that takes it keeps this crop for ever. "
                                "Connect the last step of that branch to where the crop carries on.")
    starts = [n for n in op_nodes if name(n) == "START"]
    if starts and not possible(starts[0]):
        warnings.append(W + "no path from START reaches END.")

    # 2. Dates that do not exist.
    for n in op_nodes:
        for d in _bad_dates(n.dates_text.toPlainText() if hasattr(n, "dates_text") else ""):
            warnings.append(W + f"node '{label(n)}' has the date {d}, which does not exist.")
    for k, v in (rotation or {}).items():
        texts = [v] if isinstance(v, str) else ([r.get("start") or "" for r in v] + [r.get("end") or "" for r in v]
                                                 if isinstance(v, list) else [])
        for t in texts:
            for d in _bad_dates(t):
                warnings.append(W + f"the rotation timing has the date {d}, which does not exist.")

    # 3. A crop followed by a catch crop must hand over to it.
    if crop_name.endswith("_CC") and not catch_crop_nodes:
        warnings.append(W + "this crop's name ends in _CC but it has no catch crop node, so the "
                        "catch crop is never sown.")

    # 4. Rotation timing against the dates ALMaSS has always used for this crop.
    r = rotation or {}
    if not r.get("first_date"):
        warnings.append(W + "no rotation timing is set (Rotation Timing...). ALMaSS needs the "
                        "date this crop takes over the field.")
    ref = (reference or {}).get(crop_name)
    if ref and r:
        diff = [k for k in ("first_date", "last_date", "harvest_end", "flexdates")
                if k in ref and (r.get(k) or None) != (ref.get(k) or None)]
        if diff:
            warnings.append(W + "the rotation timing differs from the dates ALMaSS has used for "
                            f"this crop ({', '.join(diff)}). Unless that is intended, use "
                            "'Load the dates ALMaSS uses' in Rotation Timing. 'Takes over the "
                            "field by' is the date the previous crop must be harvested by, not the "
                            "date of this crop's first operation.")

    # 5. ALMaSS finds a plan by the crop's name.
    if known_crops and crop_name and crop_name not in known_crops:
        close = difflib.get_close_matches(crop_name, known_crops, n=1)
        hint = f" Did you mean '{close[0]}'?" if close else ""
        warnings.append(W + f"ALMaSS has no crop called '{crop_name}', so it will not use this "
                        f"plan: it loads each crop from '<crop name>.json'.{hint}")
    return warnings

# ------------------------------------------------------------------------------------------------
# HELPER FUNCTIONS FOR GRAPHICS
# ------------------------------------------------------------------------------------------------
def shape_line_intersection(node, p1: QPointF, p2: QPointF) -> QPointF:
    rect = node.sceneBoundingRect()
    
    if node.__class__.__name__ == "ProbNode":
        cx, cy = rect.center().x(), rect.center().y()
        rx, ry = rect.width()/2, rect.height()/2
        dx, dy = p2.x() - p1.x(), p2.y() - p1.y()
        px, py = p1.x() - cx, p1.y() - cy
        
        a = (dx/rx)**2 + (dy/ry)**2
        b = 2*(px*dx/rx**2 + py*dy/ry**2)
        c = (px/rx)**2 + (py/ry)**2 - 1
        disc = b**2 - 4*a*c
        if disc < 0:
            return p2
        t1 = (-b + math.sqrt(disc)) / (2*a)
        t2 = (-b - math.sqrt(disc)) / (2*a)
        t = max(t1, t2) if 0 <= max(t1, t2) <= 1 else min(t1, t2)
        return QPointF(p1.x() + t*dx, p1.y() + t*dy)
    
    elif node.__class__.__name__ == "CondNode":
        polygon = node.mapToScene(node.polygon_shape)
        edges = [(polygon[i], polygon[(i+1)%len(polygon)]) for i in range(len(polygon))]
    
    else:  # fallback to rectangle
        edges = [
            (QPointF(rect.left(), rect.top()), QPointF(rect.right(), rect.top())),
            (QPointF(rect.right(), rect.top()), QPointF(rect.right(), rect.bottom())),
            (QPointF(rect.right(), rect.bottom()), QPointF(rect.left(), rect.bottom())),
            (QPointF(rect.left(), rect.bottom()), QPointF(rect.left(), rect.top())),
        ]

    for edge_start, edge_end in edges:
        denom = (edge_end.x() - edge_start.x()) * (p2.y() - p1.y()) - (edge_end.y() - edge_start.y()) * (p2.x() - p1.x())
        if denom == 0:
            continue
        ua = ((p2.x() - p1.x()) * (edge_start.y() - p1.y()) - (p2.y() - p1.y()) * (edge_start.x() - p1.x())) / denom
        ub = ((edge_end.x() - edge_start.x()) * (edge_start.y() - p1.y()) - (edge_end.y() - edge_start.y()) * (edge_start.x() - p1.x())) / denom
        if 0 <= ua <= 1 and 0 <= ub <= 1:
            x = edge_start.x() + ua * (edge_end.x() - edge_start.x())
            y = edge_start.y() + ua * (edge_end.y() - edge_start.y())
            return QPointF(x, y)

    return p2
# ------------------------------------------------------------------------------------------------
