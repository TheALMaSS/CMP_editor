from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt5.QtGui import QPainter, QTextDocument, QTextOption, QFont, QFontMetricsF
from PyQt5.QtCore import QRectF, Qt
from arrow import Arrow

class GenericTextItem(QGraphicsTextItem):
    def focusOutEvent(self, event):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        super().focusOutEvent(event)

    def contextMenuEvent(self, event):
        pass 

class Node(QGraphicsItem):
    def __init__(self, name):
        super().__init__()

        self.width = 200
        self.height = 100
        self.min_width = 200
        self.min_height = 100
        self.setFlag(self.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.outgoing_arrows = []
        self.incoming_arrows = []

        self.name = name

        # Name text (centered)
        self.name_text = GenericTextItem(self)
        self.name_doc = QTextDocument()
        self.name_doc.setDefaultTextOption(QTextOption(Qt.AlignCenter))
        font = QFont()
        font.setPointSize(9)
        self.name_doc.setDefaultFont(font)
        self.name_doc.setPlainText(name)
        self.name_text.setDocument(self.name_doc)

        # Id text (centered, bold, size 12)
        self.id_text = GenericTextItem(self)
        self.id_doc = QTextDocument()
        self.id_doc.setDefaultTextOption(QTextOption(Qt.AlignCenter))
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        self.id_doc.setDefaultFont(font)
        self.id_doc.setPlainText("ID")
        self.id_text.setDocument(self.id_doc)
        self.id_text.setTextInteractionFlags(Qt.TextEditorInteraction)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arrow in getattr(self, "outgoing_arrows", []):
                arrow.update_path()
            for arrow in getattr(self, "incoming_arrows", []):
                arrow.update_path()
        return super().itemChange(change, value)

    def adjust_size(self):
        fm_name = QFontMetricsF(self.name_text.font())
        name_width = fm_name.width(self.name_doc.toPlainText())
        name_height = fm_name.height()

        fm_id = QFontMetricsF(self.id_text.font())
        id_width = fm_id.width(self.id_doc.toPlainText())
        id_height = fm_id.height()

        padding_vertical = getattr(self, 'padding_vertical', 40)
        padding_horizontal = getattr(self, 'padding_horizontal', 60)
        self.width = max(self.min_width, name_width + padding_horizontal, id_width + padding_horizontal)
        self.height = max(self.min_height, name_height + id_height + padding_vertical)

        # Set text document width to match node width for proper centering
        self.name_doc.setTextWidth(self.width)
        self.id_doc.setTextWidth(self.width * 0.8)

        self.update_positions()

    def update_positions(self):
        vertical_offset_name = getattr(self, 'vertical_offset_name', -10)
        vertical_offset_id = getattr(self, 'vertical_offset_id', -10)
        name_height = self.name_text.boundingRect().height()
        id_height = self.id_text.boundingRect().height()
        id_width = self.id_text.boundingRect().width()

        self.name_text.setPos(0, (self.height - name_height) / 2 - vertical_offset_name)
        self.id_text.setPos((self.width - id_width) / 2, (self.height - name_height) / 2 - id_height - vertical_offset_id)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def add_arrow_to(self, target_node):
        for arrow in self.outgoing_arrows:
            if arrow.end_node == target_node:
                return arrow
        arrow = Arrow(self, target_node)
        self.outgoing_arrows.append(arrow)
        target_node.incoming_arrows.append(arrow)
        return arrow