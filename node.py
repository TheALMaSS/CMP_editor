from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtGui import QColor, QPen, QFont
from arrow import Arrow

class HighlightableTextItem(QGraphicsTextItem):
    def paint(self, painter, option, widget=None):
        if self.hasFocus() and self.textCursor().hasSelection():
            rect = self.boundingRect()
            painter.fillRect(rect, QColor("yellow"))
        super().paint(painter, option, widget)

class Node(QGraphicsRectItem):
    HANDLE_SIZE = 10  # bottom-right corner sensitive area

    def __init__(self, x, y, width=180, height=120, radius=10):
        super().__init__(0, 0, width, height)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setPos(x, y)
        self.radius = radius
        self.resizing = False

        # Appearance
        self.setBrush(QColor("#EBEBEB"))
        self.setPen(QPen(Qt.black, 2))

        # TEXT FIELDS
        self.constraints_text = HighlightableTextItem("Constraints", self)
        self.id_text = QGraphicsTextItem("Operation Id", self)
        self.name_text = QGraphicsTextItem("Operation Name", self)
        self.constraints_text.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.id_text.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.name_text.setTextInteractionFlags(Qt.TextEditorInteraction)

        self.update_text_positions()
        self.constraints_text.document().contentsChanged.connect(self.update_text_positions)
        self.id_text.document().contentsChanged.connect(self.update_text_positions)
        self.name_text.document().contentsChanged.connect(self.update_text_positions)

        # Arrows
        self.outgoing_arrows = []
        self.incoming_arrows = []

    def update_text_positions(self):
        """Center text horizontally; make ID and Name bold/larger."""
        rect = self.rect()

        # Constraints
        constraints_font = QFont("Arial", 10)
        self.constraints_text.setFont(constraints_font)
        bounds = self.constraints_text.boundingRect()
        x = (rect.width() - bounds.width()) / 2
        y = 5  # small margin from top
        self.constraints_text.setPos(x, y)

        # ID
        id_font = QFont("Arial", 12, QFont.Bold)
        self.id_text.setFont(id_font)
        bounds = self.id_text.boundingRect()
        x = (rect.width() - bounds.width()) / 2
        y = 35
        self.id_text.setPos(x, y)

        # Operation Name
        name_font = QFont("Arial", 10, QFont.Bold)
        self.name_text.setFont(name_font)
        bounds = self.name_text.boundingRect()
        x = (rect.width() - bounds.width()) / 2
        y = 65
        self.name_text.setPos(x, y)

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
                arrow.update_position()
            for arrow in getattr(self, "incoming_arrows", []):
                arrow.update_position()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)

    # -------------------- Resizing --------------------
    def mousePressEvent(self, event):
        rect = self.rect()
        pos = event.pos()
        # Bottom-right corner sensitive area
        if rect.right() - self.HANDLE_SIZE < pos.x() < rect.right() and rect.bottom() - self.HANDLE_SIZE < pos.y() < rect.bottom():
            self.resizing = True
        else:
            self.resizing = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            # Resize rectangle
            new_width = max(event.pos().x(), 30)
            new_height = max(event.pos().y(), 30)
            self.setRect(0, 0, new_width, new_height)
            self.update_text_positions()
            # Update arrows
            for arrow in getattr(self, "outgoing_arrows", []):
                arrow.update_position()
            for arrow in getattr(self, "incoming_arrows", []):
                arrow.update_position()
        else:
            super().mouseMoveEvent(event)