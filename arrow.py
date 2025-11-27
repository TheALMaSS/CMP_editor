from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QPolygonF, QFont
from helper_funcs import line_rect_intersection
import math

class Arrow(QGraphicsLineItem):
    def __init__(self, start_node, end_node, text="Branching\nConditions"):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setPen(QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        self.text_item = QGraphicsTextItem(text, self)
        font = QFont()
        font.setPointSize(10)
        self.text_item.setFont(font)
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text_item.setDefaultTextColor(Qt.black)
        self.text_item.document().contentsChanged.connect(self.update_text_position)

        self.update_position()

        self.end_node.incoming_arrows = getattr(self.end_node, "incoming_arrows", [])
        self.end_node.incoming_arrows.append(self)

    def update_position(self):
        start_center = self.start_node.pos() + self.start_node.rect().center()
        end_center = self.end_node.pos() + self.end_node.rect().center()

        # intersection with start node
        start = line_rect_intersection(self.start_node.sceneBoundingRect(), end_center, start_center)

        # intersection with end node
        end = line_rect_intersection(self.end_node.sceneBoundingRect(), start_center, end_center)

        self.setLine(start.x(), start.y(), end.x(), end.y())
        self.update_text_position()

    def update_text_position(self, offset=25):
        line = self.line()
        mid_x = (line.x1() + line.x2()) / 2
        mid_y = (line.y1() + line.y2()) / 2

        dx = line.x2() - line.x1()
        dy = line.y2() - line.y1()

        # compute perpendicular offset
        length = math.hypot(dx, dy)
        if length == 0:
            perp_x, perp_y = 0, 0
        else:
            perp_x = -dy / length * offset
            perp_y = dx / length * offset

        rect = self.text_item.boundingRect()
        self.text_item.setPos(mid_x - rect.width() / 2 + perp_x,
                            mid_y - rect.height() / 2 + perp_y)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        line = self.line()
        angle = math.atan2(line.y2() - line.y1(), line.x2() - line.x1())
        arrow_size = 10
        p1 = QPointF(
            line.x2() - arrow_size * math.cos(angle - math.pi / 6),
            line.y2() - arrow_size * math.sin(angle - math.pi / 6)
        )
        p2 = QPointF(
            line.x2() - arrow_size * math.cos(angle + math.pi / 6),
            line.y2() - arrow_size * math.sin(angle + math.pi / 6)
        )
        polygon = QPolygonF([QPointF(line.x2(), line.y2()), p1, p2])
        painter.setBrush(Qt.black)
        painter.drawPolygon(polygon)