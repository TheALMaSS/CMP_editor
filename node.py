from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QColorDialog
from PyQt5.QtGui import QColor, QPen, QFont, QBrush
from arrow import Arrow

class PrefixedTextItem(QGraphicsTextItem):
    def __init__(self, prefix, text="", parent=None):
        super().__init__(prefix + text, parent)
        self.prefix = prefix
        self.setTextInteractionFlags(Qt.TextEditorInteraction)

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        if cursor.position() < len(self.prefix):
            cursor.setPosition(len(self.prefix))
            self.setTextCursor(cursor)
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        cursor = self.textCursor()
        if cursor.position() < len(self.prefix):
            cursor.setPosition(len(self.prefix))
            self.setTextCursor(cursor)

# TODO: EVENTUALLY REMOVE THIS CLASS
class HighlightableTextItem(QGraphicsTextItem):
    def paint(self, painter, option, widget=None):
        if self.hasFocus() and self.textCursor().hasSelection():
            rect = self.boundingRect()
            painter.fillRect(rect, QColor("yellow"))
        super().paint(painter, option, widget)

    def mousePressEvent(self, event):
        cursor = self.textCursor()
        cursor.clearSelection()  # remove any initial selection
        self.setTextCursor(cursor)
        super().mousePressEvent(event)

class Node(QGraphicsRectItem):
    CORNER_SIZE = 20

    def __init__(self, x, y, width=180, height=120, radius=10):
        super().__init__(0, 0, width, height)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setPos(x, y)
        self.radius = radius
        self.constraint_bg = False
        self.resizing = False

        # APPEARANCE
        self.setBrush(QColor("#EBEBEB"))
        self.setPen(QPen(Qt.black, 2))

        # TEXT FIELDS
        self.id_text = QGraphicsTextItem("Id", self)
        self.name_text = QGraphicsTextItem("Name", self)
        self.dates_text = HighlightableTextItem("dd/MM - dd/MM", self)
        self.id_text.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.name_text.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.dates_text.setTextInteractionFlags(Qt.TextEditorInteraction)

        # BACKGROUND RECTANGLES FOR CONSTRAINTS AND RANDOM CHANCE

        self.update_text_positions()
        self.dates_text.document().contentsChanged.connect(self.update_text_positions)
        self.id_text.document().contentsChanged.connect(self.update_text_positions)
        self.name_text.document().contentsChanged.connect(self.update_text_positions)

        # ARROWS
        self.outgoing_arrows = []
        self.incoming_arrows = []

    def add_boolean_constraint(self):
        if self.constraint_bg:
            return  # already exists
        self.constraint_bg = True
        self.scene().update()

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
        if getattr(self, "constraint_bg", False):
            margin = 50
            rect = self.rect()
            bg_rect = rect.adjusted(-margin/2, -margin/2, margin/2, margin/2)
            light_blue = QColor("#DBC7A9")
            painter.setBrush(QBrush(light_blue))
            painter.setPen(QPen(light_blue, 2))
            painter.drawRoundedRect(bg_rect, self.radius, self.radius)

        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)