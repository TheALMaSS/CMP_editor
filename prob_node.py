from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPen, QBrush, QFont, QTextOption
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsTextItem
)

from node import Node

class ProbNode(Node):
    def __init__(self, name):
        super().__init__(name)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.padding_vertical = 30
        self.padding_horizontal = 20

        self.adjust_size()

    def paint(self, painter, option, widget):
        painter.setBrush(QColor("#D2A9F9"))
        painter.drawEllipse(QRectF(0, 0, self.width, self.height))