from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen, QFont
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem

from node import Node

class OpNode(QGraphicsRectItem, Node):

    def __init__(self, x, y, width=200, height=120, radius=10):
        QGraphicsRectItem.__init__(self, 0, 0, width, height)
        Node.__init__(self)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setPos(x, y)

        # RECT SHAPE WITH ROUNDED CORNERS
        self.radius = radius

        # KEEPING TRACK OF STATE
        self.resizing = False

        # APPEARANCE
        self.setBrush(QColor("#F0F0F0"))
        self.setPen(QPen(Qt.black, 2))

        # TEXT FIELDS
        self.id_text = QGraphicsTextItem("Id", self)
        self.name_text = QGraphicsTextItem("Name", self)
        self.dates_text = QGraphicsTextItem("dd/MM - dd/MM", self)

        self.id_text.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.dates_text.setTextInteractionFlags(Qt.TextEditorInteraction)

        self.dates_text.document().contentsChanged.connect(self.update_text_positions)
        self.id_text.document().contentsChanged.connect(self.update_text_positions)
        self.name_text.document().contentsChanged.connect(self.update_text_positions)
        self.update_text_positions()

    # -----------------------------------------------------------------------------------
    # CALLBACK FUNCTION FOR WHEN THE SHAPE AND POSITION OF PARENT CHANGE
    # -----------------------------------------------------------------------------------
    def update_text_positions(self):
        rect = self.rect()
        # ID
        self.id_text.setFont(QFont("Arial", 12, QFont.Bold))
        bounds = self.id_text.boundingRect()
        x = (rect.width() - bounds.width()) / 2
        y = 5
        self.id_text.setPos(x, y)
        # Name
        self.name_text.setFont(QFont("Arial", 10, QFont.Bold))
        bounds = self.name_text.boundingRect()
        x = (rect.width() - bounds.width()) / 2
        y = 40
        self.name_text.setPos(x, y)
        # Dates range
        self.dates_text.setFont(QFont("Arial", 10))
        bounds = self.dates_text.boundingRect()
        x = (rect.width() - bounds.width()) / 2
        y = 70
        self.dates_text.setPos(x, y)

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

    # -----------------------------------------------------------------------------------
    # PAINT
    # -----------------------------------------------------------------------------------
    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)