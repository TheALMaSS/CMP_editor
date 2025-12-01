from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QColorDialog
from PyQt5.QtGui import QColor, QPen, QFont, QBrush
from arrow import Arrow

class TextItemWithBackground(QGraphicsTextItem):
    def __init__(self, text="", parent=None, color=QColor("#8B0000"), padding=3):
        super().__init__(text, parent)
        self.color = color        # used for both background and border
        self.padding = padding

        # white text
        self.setDefaultTextColor(Qt.white)

    def setColor(self, color):
        self.color = color
        self.update()

    def setPadding(self, padding):
        self.padding = padding
        self.update()

    def paint(self, painter, option, widget=None):
        rect = self.boundingRect()

        padded_rect = QRectF(rect.x() - self.padding,
                             rect.y() - self.padding,
                             rect.width() + 2*self.padding,
                             rect.height() + 2*self.padding)

        # background
        painter.setBrush(self.color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(padded_rect)

        # border (same color)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(padded_rect)

        super().paint(painter, option, widget)

class Node(QGraphicsRectItem):
    CORNER_SIZE = 20

    def __init__(self, x, y, width=200, height=120, radius=10):
        super().__init__(0, 0, width, height)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setPos(x, y)
        self.radius = radius
        self.resizing = False
        self.random_chance_on = False
        self.constraints_on = False

        # APPEARANCE
        self.setBrush(QColor("#EBEBEB"))
        self.setPen(QPen(Qt.black, 2))

        # TEXT FIELDS
        self.id_text = QGraphicsTextItem("Id", self)
        self.name_text = QGraphicsTextItem("Name", self)
        self.dates_text = QGraphicsTextItem("dd/MM - dd/MM", self)
        self.constraints_text = TextItemWithBackground("constraints", parent=self, color=QColor("#6E2C2C"))
        self.random_chance_text = TextItemWithBackground("random chance%", parent=self, color=QColor("#4E3284"))
        self.id_text.setTextInteractionFlags(Qt.TextEditorInteraction)
        #self.name_text.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.dates_text.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.random_chance_text.setTextInteractionFlags(Qt.TextEditorInteraction)

        self.constraints_text.setVisible(False)
        self.random_chance_text.setVisible(False)

        self.update_text_positions()
        self.dates_text.document().contentsChanged.connect(self.update_text_positions)
        self.id_text.document().contentsChanged.connect(self.update_text_positions)
        self.name_text.document().contentsChanged.connect(self.update_text_positions)
        self.constraints_text.document().contentsChanged.connect(self.update_text_positions)
        self.random_chance_text.document().contentsChanged.connect(self.update_text_positions)

        # ARROWS
        self.outgoing_arrows = []
        self.incoming_arrows = []

    def update_text_positions(self):
        """Center text horizontally; make ID and Name bold/larger."""
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

        # Constraint text
        self.constraints_text.setFont(QFont("Arial", 12))
        bounds = self.constraints_text.boundingRect()
        x = (rect.width() - bounds.width()) / 2
        y = 110
        self.constraints_text.setPos(x, y)

        # Random chance text
        self.random_chance_text.setFont(QFont("Arial", 12))
        bounds = self.random_chance_text.boundingRect()
        x = (rect.width() - bounds.width()) / 2
        if self.constraints_on:
            y = 160
        else:
            y = 110
        self.random_chance_text.setPos(x, y)

    def add_arrow_to(self, target_node):
        # Avoid duplicates
        for arrow in self.outgoing_arrows:
            if arrow.end_node == target_node:
                return arrow
        arrow = Arrow(self, target_node)
        self.outgoing_arrows.append(arrow)
        target_node.incoming_arrows.append(arrow)
        return arrow

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arrow in getattr(self, "outgoing_arrows", []):
                arrow.update_path()
            for arrow in getattr(self, "incoming_arrows", []):
                arrow.update_path()
        return super().itemChange(change, value)
    
    def change_color(self, color):
        if color.isValid():
            self.setBrush(color)

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)