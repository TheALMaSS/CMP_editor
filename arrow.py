from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QPainterPath, QPolygonF, QFont
from helper_funcs import line_rect_intersection
import math

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
    def __init__(self, start_node, end_node, text="Branching\nConditions"):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setPen(QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        # Text label
        self.text_item = QGraphicsTextItem(text, self)
        font = QFont()
        font.setPointSize(10)
        self.text_item.setFont(font)
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text_item.setDefaultTextColor(Qt.black)
        self.text_item.document().contentsChanged.connect(self.update_text_position)

        # Bend points list
        self.bend_points = []

        # Register this arrow with the end node
        self.end_node.incoming_arrows = getattr(self.end_node, "incoming_arrows", [])
        self.end_node.incoming_arrows.append(self)

        self.update_path()

    def add_bend_point(self, pos):
        bend = BendPoint(self, pos)
        self.bend_points.append(bend)
        self.scene().addItem(bend)
        self.update_path()

    def update_path(self):
        start_center = self.start_node.pos() + self.start_node.rect().center()
        end_center = self.end_node.pos() + self.end_node.rect().center()

        # intersections with node borders
        start = line_rect_intersection(self.start_node.sceneBoundingRect(), end_center, start_center)
        end = line_rect_intersection(self.end_node.sceneBoundingRect(), start_center, end_center)

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

        # Approximate midpoint of the polyline
        start_elem = path.elementAt(0)
        end_elem = path.elementAt(path.elementCount() - 1)
        mid_x = (start_elem.x + end_elem.x) / 2
        mid_y = (start_elem.y + end_elem.y) / 2

        # perpendicular offset
        dx = end_elem.x - start_elem.x
        dy = end_elem.y - start_elem.y
        length = math.hypot(dx, dy) or 1
        perp_x = -dy / length * offset
        perp_y = dx / length * offset

        rect = self.text_item.boundingRect()
        self.text_item.setPos(mid_x - rect.width() / 2 + perp_x,
                              mid_y - rect.height() / 2 + perp_y)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        # Draw arrowhead at last segment
        path = self.path()
        if path.elementCount() < 2:
            return

        p1_elem = path.elementAt(path.elementCount() - 2)
        p2_elem = path.elementAt(path.elementCount() - 1)
        p1 = QPointF(p1_elem.x, p1_elem.y)
        p2 = QPointF(p2_elem.x, p2_elem.y)

        angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
        arrow_size = 10
        point1 = QPointF(
            p2.x() - arrow_size * math.cos(angle - math.pi / 6),
            p2.y() - arrow_size * math.sin(angle - math.pi / 6)
        )
        point2 = QPointF(
            p2.x() - arrow_size * math.cos(angle + math.pi / 6),
            p2.y() - arrow_size * math.sin(angle + math.pi / 6)
        )
        polygon = QPolygonF([p2, point1, point2])
        painter.setBrush(Qt.black)
        painter.drawPolygon(polygon)