
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF
import math

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
