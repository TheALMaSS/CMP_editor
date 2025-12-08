from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen, QBrush, QFont, QTextOption
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsTextItem
)

from node import Node

class ProbNode(QGraphicsEllipseItem, Node):

    def __init__(self, x, y, width=140, height=140, text=""):

        #id = int(self.scene().prob_nodes[-1].id) + 1 if self.scene().prob_nodes else 1

        QGraphicsEllipseItem.__init__(self, 0, 0, width, height)
        Node.__init__(self)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setPos(x, y)
        self.width = width
        self.height = height

        # APPEARANCE
        self.setBrush(QBrush(QColor("#9ABCCD")))
        self.setPen(QPen(Qt.black, 2))

        # TEXT FIELDS

        self.id_text = QGraphicsTextItem("ID", self)
        self.id_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.id_text.document().contentsChanged.connect(self.update_text_positions)
        self.id_text.setTextInteractionFlags(Qt.TextEditorInteraction)

        self.name_text = QGraphicsTextItem("Probability\nNode", self)
        self.name_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.name_text.document().contentsChanged.connect(self.update_text_positions)

        self.update_text_positions()

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

    def update_text_positions(self):
        # get node dimensions
        if hasattr(self, "rect"):  # QGraphicsRectItem
            rect = self.rect()
            width = rect.width()
            height = rect.height()
        else:  # fallback to stored attributes
            width = getattr(self, "width", 100)
            height = getattr(self, "height", 50)

        # center id_text
        id_bounds = self.id_text.boundingRect()
        self.id_text.setPos((width - id_bounds.width()) / 2, (height - id_bounds.height()) / 2 - 40)

        # center name_text
        self.name_text.setTextWidth(width)
        option = QTextOption()
        option.setAlignment(Qt.AlignCenter)
        self.name_text.document().setDefaultTextOption(option)

        name_bounds = self.name_text.boundingRect()
        self.name_text.setPos((width - name_bounds.width()) / 2, (height - name_bounds.height()) / 2 + 10)