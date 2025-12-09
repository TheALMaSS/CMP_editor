
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF
import math
import sys, os, re, json
from jinja2 import Environment, FileSystemLoader

# ------------------------------------------------------------------------------------------------
# HELPER FUNCTIONS FOR EXPORT AND SAVING
# ------------------------------------------------------------------------------------------------
def generate_json(all_nodes, filename):
    data = []
    for node in all_nodes:
        node_data = {
            "type": node.__class__.__name__,
            "x": node.scenePos().x(),
            "y": node.scenePos().y(),
            "width": getattr(node, "width", 120),
            "height": getattr(node, "height", 60),
            "id": node.id_text.toPlainText(),
            "name": node.name_text.toPlainText(),
            "dates": getattr(node, "dates_text", "dd/MM - dd/MM").toPlainText() if hasattr(node, "dates_text") else "+0d - +0d",
            "outgoing": []
        }

        if node.__class__.__name__ == "OpNode":
            node_data.update({
                "cpp_func": node.cpp_func
            })

        for arrow in node.outgoing_arrows:
            if arrow.end_node:
                if hasattr(arrow.end_node, "id_text"):
                    destination_id = arrow.end_node.id_text.toPlainText()
                else:
                    destination_id = "no_id"

            branching_condition = arrow.text_item.toPlainText() if arrow.text_item else ""

            arrow_data = {
                "destination_type": arrow.end_node.__class__.__name__ if arrow.end_node else "",
                "destination_id": destination_id,
                "branching_condition": branching_condition,
                "bend_points": [[bp.pos().x(), bp.pos().y()] for bp in arrow.bend_points]
            }

            node_data["outgoing"].append(arrow_data)

        data.append(node_data)

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    return data

def to_all_caps(name):
    s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return s1.upper()

def to_lower_underscore(name):
    s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return s1.lower()

def generate_header_file(crop_name, data):

    crop_name_all_caps = to_all_caps(crop_name)
    crop_name_lowercase = to_lower_underscore(crop_name)

    nodes = [node for node in data if node.get("type") == "OpNode"]

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('templates/header_file.jinja')

    output = template.render(
        crop_name=crop_name,
        crop_name_all_caps=crop_name_all_caps,
        crop_name_lowercase=crop_name_lowercase,
        nodes=nodes
    )

    with open(f"{crop_name}.h", "w") as f:
        f.write(output)

def generate_cpp_file(crop_name, data):
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
    #
    # TOTAL TEMPLATES NEEDED:
    # CASE START
    # CASE END
    # CASE OPNODE
    # CASE CONDNODE
    # CASE PROBNODE

    return

# ------------------------------------------------------------------------------------------------
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
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
