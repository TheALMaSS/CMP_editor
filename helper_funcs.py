
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF
import math
import sys, os, re, json
from jinja2 import Environment, FileSystemLoader

# ------------------------------------------------------------------------------------------------
# HELPER FUNCTIONS FOR EXPORT AND SAVING
# ------------------------------------------------------------------------------------------------
def generate_json(all_nodes, crop_name, author, date, filename):
    # Metadata stays at the top level
    data = {
        "crop_name": crop_name,
        "author": author,
        "last_modified": date,
        "nodes": []   # this will hold all node objects
    }

    for node in all_nodes:
        node_data = {
            "type": node.__class__.__name__,
            "x": node.scenePos().x(),
            "y": node.scenePos().y(),
            "width": getattr(node, "width", 120),
            "height": getattr(node, "height", 60),
            "id": node.id_text.toPlainText(),
            "name": node.name_text.toPlainText(),
            "dates": getattr(node, "dates_text", "+0d - +0d").toPlainText() if hasattr(node, "dates_text") else "+0d - +0d",
            "outgoing": []
        }

        if node.__class__.__name__ == "OpNode":
            node_data["cpp_func"] = node.cpp_func

        if node.__class__.__name__ == "CondNode":
            node_data["cpp_cond"] = node.cpp_cond
            node_data["cond_type"] = node.cond_type
            node_data["cond_value"] = node.cond_value

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

        # append node_data to the "nodes" array
        data["nodes"].append(node_data)

    # write the JSON to file
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    return data
# ------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------
def generate_almass_json(all_nodes, crop_name, filename):
    start_node = None
    others = []
    for n in all_nodes:
        if n.id_text.toPlainText() == "START":
            start_node = n
        else:
            others.append(n)
    ordered = [start_node] + others if start_node else all_nodes

    data = {"crop_name": crop_name, "nodes": []}
    nodes_data = []

    code_counter = 1
    for node in ordered:
        node_id = node.id_text.toPlainText()
        if node_id == "START":
            earliest = getattr(node, "dates_text", "+0d").toPlainText() if hasattr(node, "dates_text") else "+0d"
            latest = ""
        elif node_id == "END":
            earliest = "+1d"
            latest = ""
        else:
            dates_str = getattr(node, "dates_text", "+0d - +0d").toPlainText() if hasattr(node, "dates_text") else "+0d - +0d"
            earliest, latest = [part.strip() for part in dates_str.split("-", 1)]

        node_data = {
            "type": node.__class__.__name__,
            "code": code_counter,
            "id": node_id,
            "name": node.name_text.toPlainText(),
            "earliest": earliest,
            "latest": latest,
            "outgoing": []
        }

        if node.__class__.__name__ == "CondNode":
            node_data["cond_type"] = node.cond_type
            node_data["cond_value"] = node.cond_value

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
                        break

                arrow_data = {
                    "destination_type": arrow.end_node.__class__.__name__ if arrow.end_node else "",
                    "destination_id": dest_id,
                    "destination_code": dest_code,
                    "destination_earliest": dest_earliest,
                    "branching_condition": arrow.text_item.toPlainText() if arrow.text_item else ""
                }
                node_data["outgoing"].append(arrow_data)

        data["nodes"].append(node_data)

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    return data
# ------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------
def to_all_caps(name):
    s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return s1.upper()

def to_lower_underscore(name):
    s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return s1.lower()
# ------------------------------------------------------------------------------------------------

def get_earliest_date(dates: str) -> str:
    start_date = dates.split(" - ")[0].strip()

    relative_match = re.fullmatch(r"\+(\d{1,2})d", start_date)
    absolute_match = re.fullmatch(r"(\d{2})/(\d{2})", start_date)

    if relative_match:
        offset = int(relative_match.group(1))
        return f"g_date->Date() + {offset}"
    elif absolute_match:
        day, month = absolute_match.groups()
        return f"std::max(g_date->Date() + 1, g_date->OldDays() + g_date->DayInYear({str(int(day))}, {str(int(month))}))"
    else:
        return "g_date->Date() + 1"


def get_days_left(dates: str) -> str:
    end_date = dates.split(" - ")[-1].strip()

    absolute_match = re.fullmatch(r"(\d{2})/(\d{2})", end_date)
    if absolute_match:
        day, month = absolute_match.groups()
        return f"g_date->DayInYear({str(int(day))}, {str(int(month))}) - g_date->DayInYear()"
    else:
        # fallback to relative date if format is unknown
        relative_match = re.fullmatch(r"\+(\d{1,2})d", end_date)
        if relative_match:
            offset = int(relative_match.group(1))
            return f"g_date->Date() + {offset}"
        return "g_date->Date()"

def get_starting_date(start_node):
    #g_date->DayInYear(26, 8)
    absolute_match = re.fullmatch(r"(\d{2})/(\d{2})", start_node.get("dates"))
    if absolute_match:
        day, month = absolute_match.groups()
        return f"g_date->DayInYear({str(int(day))}, {str(int(month))})"


# ------------------------------------------------------------------------------------------------
def generate_header_file(crop_name, data):

    crop_name_all_caps = to_all_caps(crop_name)
    crop_name_lowercase = to_lower_underscore(crop_name)
    nodes = [node for node in data[1:] if node.get("type") == "OpNode"]
    start_node = next(n for n in data[1:] if n["id"] == "START")
    starting_date = get_starting_date(start_node)

    env = Environment(
        loader=FileSystemLoader(resource_path("templates"))
    )

    template = env.get_template('header_file.jinja')

    output = template.render(
        crop_name=crop_name,
        crop_name_all_caps=crop_name_all_caps,
        crop_name_lowercase=crop_name_lowercase,
        starting_date = starting_date,
        nodes=nodes
    )

    with open(f"{crop_name}.h", "w") as f:
        f.write(output)
# ------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------
def generate_cpp_file(crop_name, data):
    env = Environment(
        loader=FileSystemLoader(resource_path("templates")),
        trim_blocks=True,
        lstrip_blocks=True
    )

    tmpl_main = env.get_template("cpp_file.jinja")

    # Classify nodes
    start_node = next(n for n in data[1:] if n["id"] == "START")
    end_node   = next(n for n in data[1:] if n["id"] == "END")
    middle_nodes = [n for n in data[1:] if n["id"] not in ("START", "END")]

    # Vars for every node
    crop_name_lowercase = to_lower_underscore(crop_name)

    # Render START
    t_start = env.get_template("case_start.jinja")
    next_id = start_node["outgoing"][0]["destination_id"]
    next_node = next((n for n in data[1:] if n["id"] == next_id), None)
    next_date = get_earliest_date(next_node["dates"])

    start_block = t_start.render(
                crop_name = crop_name,
                crop_name_lowercase = crop_name_lowercase,
                next_date = next_date,
                next_id = next_id
            )

    # Render END
    t_end = env.get_template("case_end.jinja")
    end_block = t_end.render(
                crop_name_lowercase = crop_name_lowercase
            )

    # Render middle nodes
    rendered_middle = []
    for node in middle_nodes:

        # ---------------------------------------------------------
        if node["type"] == "OpNode":
            t = env.get_template("case_op_node.jinja")
            next_id = node["outgoing"][0]["destination_id"]
            next_node = next((n for n in data[1:] if n["id"] == next_id), None)
            next_date = get_earliest_date(next_node["dates"])
            scheduling_date = get_days_left(node["dates"])
            cpp_func = node["cpp_func"]
            latest_date = get_days_left(node["dates"])

            block = t.render(
                crop_name = crop_name,
                crop_name_lowercase = crop_name_lowercase,
                scheduling_date = scheduling_date,
                cpp_func = cpp_func,
                id = node["id"],
                next_date = next_date,
                next_id = next_id,
                latest_date = latest_date
            )

        # ---------------------------------------------------------
        elif node["type"] == "CondNode":
            yes_node_id = next(
                (arrow["destination_id"] for arrow in node["outgoing"] if arrow.get("branching_condition") == "YES"),
                None
            )
            no_node_id = next(
                (arrow["destination_id"] for arrow in node["outgoing"] if arrow.get("branching_condition") == "NO"),
                None
            )
            yes_node = next((n for n in data[1:] if n["id"] == yes_node_id), None)
            no_node = next((n for n in data[1:] if n["id"] == no_node_id), None)

            yes_node_sched_date = get_earliest_date(yes_node["dates"])
            no_node_sched_date = get_earliest_date(no_node["dates"])

            block = t.render(
                crop_name = crop_name,
                crop_name_lowercase = crop_name_lowercase,
                id = node["id"],
                cpp_cond = node["cpp_cond"],
                yes_node_id = yes_node_id,
                yes_node_sched_date = yes_node_sched_date,
                no_node_id = no_node_id,
                no_node_sched_date = no_node_sched_date
            )

        # ---------------------------------------------------------
        elif node["type"] == "ProbNode":
            t = env.get_template("case_prob_node.jinja")

            next_ids = [o["destination_id"] for o in node["outgoing"]]
            probabilities = [float(o["branching_condition"].strip('%')) / 100.0 for o in node["outgoing"]]
            earliest_dates = []
            for dest_id in next_ids:
                dest_node = next(n for n in data[1:] if n["id"] == dest_id)
                earliest_dates.append(get_earliest_date(dest_node["dates"]))

            block = t.render(
                crop_name_lowercase=crop_name.lower(),
                id=node["id"],
                next_ids=next_ids,
                earliest_dates=earliest_dates,
                probabilities=probabilities
            )
        # ---------------------------------------------------------
        else:
            continue

        rendered_middle.append(block)

    middle_block = "\n".join(rendered_middle)

    cpp_code = tmpl_main.render(
        crop_name=crop_name,
        start_block=start_block,
        middle_block=middle_block,
        end_block=end_block
    )

    with open(crop_name + ".cpp", "w") as f:
        f.write(cpp_code)

    # If the type of the node is "OpNode" and the node id is not "START" or "END" -> choose case_op_node.jinja
    # If the type is "OpNode" and the node id is "START" -> choose case_start.jinja
    # If the type is "OpNode" and the node id is "END" -> choose case_end.jinja
    # If the type of the node is "CondNode" -> choose case_cond_node.jinja
    # If the type of the node is "ProbNode" -> choose case_prob_node.jinja
    #
    # OpNode structure:
    # STEP 1: try to do operation. If fail, re-schedule for tomorrow, then break
    # STEP 2: schedule the only 1 next node (max 1, min 1)
    #
    # CondNode structure:
    # STEP 1: empty
    # STEP 2: schedule the only 2 next nodes (max 2, min 2) but gate them with the condition
    #
    # ProbNode structure:
    # STEP 1: empty
    # STEP 2: schedule all the possible nodes iteratively (no upper limit, min 1) but gate them with the probability
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
def validate_graph(op_nodes, prob_nodes, cond_nodes, crop_name, author):
    warnings = []

    op_names = [op_node.name_text.toPlainText() for op_node in op_nodes]
    ids = [node.id_text.toPlainText() for node in (op_nodes + prob_nodes + cond_nodes)]

    if crop_name == "":
        warnings.append("⚠ <b>WARNING:</b> no crop's name defined.")

    if author == "":
        warnings.append("⚠ <b>WARNING:</b> no author's name defined.")

    if "START" not in op_names:
        warnings.append("⚠ <b>WARNING:</b> no operation named 'START' exists.")

    if "END" not in op_names:
        warnings.append("⚠ <b>WARNING:</b> no operation named 'END' exists.")

    if len(ids) != len(set(ids)):
        warnings.append("⚠ <b>WARNING:</b> two or more Nodes share the same ID.")

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

    for op_node in op_nodes:
        outgoing = op_node.outgoing_arrows
        if len(outgoing) != 1 and op_node.name_text.toPlainText() != "END":
            warnings.append(
                "⚠ <b>WARNING:</b> Node '" + op_node.id_text.toPlainText() + "' must have exactly 1 outgoing arrow."
            )

    pattern1 = r'\d{2}/\d{2} - \d{2}/\d{2}'
    pattern2 = r'\+\d+d - \d{2}/\d{2}'
    pattern3 = r'\d{2}/\d{2}'

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

    return warnings
# ------------------------------------------------------------------------------------------------

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
