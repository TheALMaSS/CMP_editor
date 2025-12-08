from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QGraphicsTextItem
from node import Node
from PyQt5.QtGui import QTextDocument, QTextOption, QFont, QColor

class OpNode(Node):
    def __init__(self, name):
        super().__init__(name)

        self.dates_text = QGraphicsTextItem(self)
        self.dates_doc = QTextDocument()
        self.dates_doc.setDefaultTextOption(QTextOption(Qt.AlignCenter))
        self.dates_doc.setPlainText("dd/MM - dd/MM")
        font = QFont()
        font.setPointSize(9)
        self.dates_doc.setDefaultFont(font)
        self.dates_text.setDocument(self.dates_doc)
        self.dates_text.setTextInteractionFlags(Qt.TextEditorInteraction)

        self.vertical_offset_name = 0
        self.vertical_offset_id = 0
        self.padding_vertical = 60
        self.padding_horizontal = 100

        self.adjust_size()

    def update_positions(self):
        super().update_positions()
        vertical_offset = 5
        margin_horizontal = 0
        # Make dates_text slightly narrower than parent rectangle
        self.dates_doc.setTextWidth(self.width - margin_horizontal)
        self.dates_text.setPos(margin_horizontal/2, self.height - self.dates_text.boundingRect().height() - vertical_offset)

    def paint(self, painter, option, widget):
        painter.setBrush(QColor("#ECECEC"))
        painter.drawRoundedRect(QRectF(0, 0, self.width, self.height), 10, 10)