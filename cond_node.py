from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtGui import QPolygonF, QBrush, QPen, QColor, QFont, QTextOption
from PyQt5.QtCore import Qt, QPointF
from node import Node

class CondNode(Node):
    def __init__(self, name, cpp_cond, cond_type, cond_value):
        super().__init__(name)
        self.vertical_offset_name = 0
        self.vertical_offset_id = 5
        self.padding_vertical = 110
        self.padding_horizontal = 80
        self.width = 100
        self.height = 60
        self.adjust_size()
        
        self.polygon_shape = QPolygonF([
            QPointF(self.width/2, 0),
            QPointF(self.width, self.height/2),
            QPointF(self.width/2, self.height),
            QPointF(0, self.height/2)
        ])

        self.cpp_cond = cpp_cond
        self.cond_type = cond_type
        self.cond_value = cond_value

    def paint(self, painter, option, widget):
        painter.setBrush(QColor("#A9CFF9"))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(self.polygon_shape)

        if self.isSelected():
            pen_color = QColor("#007BFF")
            pen_width = 3
        else:
            pen_color = QColor("#000000")
            pen_width = 1

        pen = QPen(pen_color, pen_width)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(self.polygon_shape)