from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF


def line_rect_intersection(rect: QRectF, p1: QPointF, p2: QPointF) -> QPointF:
    """Return intersection point of line p1→p2 with rectangle rect."""
    edges = [
        (QPointF(rect.left(), rect.top()), QPointF(rect.right(), rect.top())),      # top
        (QPointF(rect.right(), rect.top()), QPointF(rect.right(), rect.bottom())),  # right
        (QPointF(rect.right(), rect.bottom()), QPointF(rect.left(), rect.bottom())),# bottom
        (QPointF(rect.left(), rect.bottom()), QPointF(rect.left(), rect.top())),    # left
    ]
    
    for edge_start, edge_end in edges:
        denom = (edge_end.x() - edge_start.x()) * (p2.y() - p1.y()) - (edge_end.y() - edge_start.y()) * (p2.x() - p1.x())
        if denom == 0:
            continue  # parallel, no intersection
        ua = ((p2.x() - p1.x()) * (edge_start.y() - p1.y()) - (p2.y() - p1.y()) * (edge_start.x() - p1.x())) / denom
        ub = ((edge_end.x() - edge_start.x()) * (edge_start.y() - p1.y()) - (edge_end.y() - edge_start.y()) * (edge_start.x() - p1.x())) / denom
        if 0 <= ua <= 1 and 0 <= ub <= 1:
            # intersection point
            x = edge_start.x() + ua * (edge_end.x() - edge_start.x())
            y = edge_start.y() + ua * (edge_end.y() - edge_start.y())
            return QPointF(x, y)
    return p2  # fallback if no intersection found