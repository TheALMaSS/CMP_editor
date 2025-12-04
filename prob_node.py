from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen, QBrush, QFont
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsTextItem
)

from node import Node

class ProbNode(QGraphicsEllipseItem, Node):

    def __init__(self, x, y, width=140, height=140):
        QGraphicsEllipseItem.__init__(self, 0, 0, width, height)
        Node.__init__(self)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setPos(x, y)

        # APPEARANCE
        self.setBrush(QBrush(QColor("#9ABCCD")))
        self.setPen(QPen(Qt.black, 2))

        # TEXT FIELD
        self.text = QGraphicsTextItem("Probability\n    Node", self)
        self.text.setFont(QFont("Arial", 10, QFont.Bold))
        self.text.setDefaultTextColor(Qt.black)
        self.text.document().contentsChanged.connect(self.update_text_positions)
        self.update_text_positions(width, height)

    # -----------------------------------------------------------------------------------
    # CALLBACK FUNCTION FOR WHEN THE PARENT CHANGES - ALL ARROWS CONNECTED FOLLOW IT
    # -----------------------------------------------------------------------------------
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arrow in getattr(self, "outgoing_arrows", []):
                arrow.update_path()
            for arrow in getattr(self, "incoming_arrows", []):
                arrow.update_path()
        return super().itemChange(change, value)

    def update_text_positions(self, width, height):
        bounds = self.text.boundingRect()
        x = (width - bounds.width()) / 2
        y = (height - bounds.height()) / 2
        self.text.setPos(x, y)