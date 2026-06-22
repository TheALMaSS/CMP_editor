from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtGui import QTextDocument, QTextOption, QFont, QColor, QPen
from node import Node, GenericTextItem
from helper_funcs import resource_path

OPERATIONS_FILE = resource_path("operations.json")


class OpNode(Node):
    def __init__(self, name):
        super().__init__(name)

        self.dates_text = GenericTextItem(self)

        if name != "END":
            self.dates_doc = QTextDocument()
            self.dates_doc.setDefaultTextOption(QTextOption(Qt.AlignCenter))

            if name != "START":
                self.dates_doc.setPlainText("dd/MM - dd/MM")
            else:
                self.dates_doc.setPlainText("dd/MM")

            font = QFont()
            font.setPointSize(9)
            self.dates_doc.setDefaultFont(font)

            self.dates_text.setDocument(self.dates_doc)
            self.dates_text.setTextInteractionFlags(Qt.TextEditorInteraction)

            self.vertical_offset_name = 0
            self.vertical_offset_id = 0
            self.padding_vertical = 60
            self.padding_horizontal = 100

        if name in ("START", "END"):
            if name == "END":
                self.dates_text.setVisible(False)

            self.vertical_offset_id = -30
            self.name_text.setVisible(False)
            self.id_text.setPlainText(name)

        self.adjust_size()

    def update_positions(self):
        super().update_positions()

        if self.name == "END":
            return

        vertical_offset = 5
        dates_width = self.width * 0.8
        self.dates_doc.setTextWidth(dates_width)

        self.dates_text.setPos(
            (self.width - dates_width) / 2,
            self.height - self.dates_text.boundingRect().height() - vertical_offset
        )

    def paint(self, painter, option, widget):
        painter.setBrush(QColor("#ECECEC"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(0, 0, self.width, self.height), 10, 10)

        if self.isSelected():
            pen_color = QColor("#007BFF")
            pen_width = 3
        else:
            pen_color = QColor("#000000")
            pen_width = 1

        pen = QPen(pen_color, pen_width)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(QRectF(0, 0, self.width, self.height), 10, 10)