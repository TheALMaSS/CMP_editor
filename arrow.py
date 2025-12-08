from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPen, QPainterPath, QPolygonF, QFont
import math
from helper_funcs import shape_line_intersection  # your existing helper

class BendPoint(QGraphicsEllipseItem):
    def __init__(self, arrow, pos, radius=8):
        super().__init__(-radius, -radius, 2*radius, 2*radius)
        self.setBrush(Qt.white)
        self.setPen(QPen(Qt.black))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(2)
        self.arrow = arrow
        self.setPos(pos)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.arrow.update_path()
        return super().itemChange(change, value)

class Arrow(QGraphicsPathItem):
    def __init__(self, start_node, end_node, text=""):
        super().__init__()
        self.start_node, self.end_node = start_node, end_node
        self.setPen(QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.bend_points = []

        # Text label
        self.text_item = QGraphicsTextItem(text, self)
        font = QFont()
        font.setPointSize(10)
        self.text_item.setFont(font)
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text_item.setDefaultTextColor(Qt.black)
        self.text_item.document().contentsChanged.connect(lambda: self.update_text_position())
        self.text_item.setVisible(False)

        # Register arrow with end node
        self.end_node.incoming_arrows = getattr(self.end_node, "incoming_arrows", [])
        self.end_node.incoming_arrows.append(self)

        self.update_path()

    def set_text(self, text):
        self.text_item.setPlainText(text)
        self.update_text_position()

    def add_bend_point(self, pos):
        bend = BendPoint(self, pos)
        self.bend_points.append(bend)
        self.scene().addItem(bend)
        self.update_path()

    def update_path(self):
        start_center = self.start_node.sceneBoundingRect().center()
        end_center = self.end_node.sceneBoundingRect().center()

        first_target = self.bend_points[0].scenePos() if self.bend_points else end_center
        last_target = self.bend_points[-1].scenePos() if self.bend_points else start_center

        start = shape_line_intersection(self.start_node, first_target, start_center)
        end = shape_line_intersection(self.end_node, last_target, end_center)

        path = QPainterPath(start)
        for bend in self.bend_points:
            path.lineTo(bend.scenePos())
        path.lineTo(end)

        self.setPath(path)
        self.update_text_position()

    def update_text_position(self, offset=25):
        path = self.path()
        if path.elementCount() < 2:
            return

        points = [QPointF(path.elementAt(i).x, path.elementAt(i).y) for i in range(path.elementCount())]
        seg_lengths = [math.hypot(points[i+1].x()-points[i].x(), points[i+1].y()-points[i].y()) for i in range(len(points)-1)]
        total_length = sum(seg_lengths)
        mid_dist = total_length / 2

        accumulated = 0
        for i, seg_len in enumerate(seg_lengths):
            if accumulated + seg_len >= mid_dist:
                t = (mid_dist - accumulated) / seg_len
                mid_x = points[i].x() + t * (points[i+1].x() - points[i].x())
                mid_y = points[i].y() + t * (points[i+1].y() - points[i].y())
                dx, dy = points[i+1].x() - points[i].x(), points[i+1].y() - points[i].y()
                break
            accumulated += seg_len

        length = math.hypot(dx, dy) or 1
        perp_x, perp_y = -dy / length * offset, dx / length * offset
        rect = self.text_item.boundingRect()
        self.text_item.setPos(mid_x - rect.width()/2 + perp_x, mid_y - rect.height()/2 + perp_y)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        path = self.path()
        if path.elementCount() < 2:
            return

        # Use last two points of the path
        e1, e2 = path.elementAt(path.elementCount() - 2), path.elementAt(path.elementCount() - 1)
        p1, p2 = QPointF(e1.x, e1.y), QPointF(e2.x, e2.y)

        dx, dy = p2.x() - p1.x(), p2.y() - p1.y()
        length = math.hypot(dx, dy)
        if length == 0:
            return  # avoid division by zero / NaN

        angle = math.atan2(dy, dx)
        arrow_size = 14

        # Compute arrowhead points
        point1 = QPointF(
            p2.x() - arrow_size * math.cos(angle - math.pi / 6),
            p2.y() - arrow_size * math.sin(angle - math.pi / 6)
        )
        point2 = QPointF(
            p2.x() - arrow_size * math.cos(angle + math.pi / 6),
            p2.y() - arrow_size * math.sin(angle + math.pi / 6)
        )

        arrow_head = QPolygonF([p2, point1, point2])
        painter.setBrush(Qt.black)
        painter.drawPolygon(arrow_head)