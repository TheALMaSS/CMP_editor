from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QGraphicsTextItem
from node import Node
from PyQt5.QtGui import QTextDocument, QTextOption, QFont, QColor
import json
from helper_funcs import resource_path

OPERATIONS_FILE = resource_path("operations.json")

class OpNode(Node):
    def __init__(self, name):
        super().__init__(name)

        self.dates_text = QGraphicsTextItem(self)
        
        # Only nodes that are not start and end have a dates field
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

        # Special appearance only for start and end nodes
        # TODO: fix this END/START/NORMAL NODE switching thing
        if name == "END" or name == "START":
            if name == "END":
                self.dates_text.setVisible(False)
                self.vertical_offset_id = -30
            else:
                self.vertical_offset_id = -30
            self.name_text.setVisible(False)
            self.id_text.setPlainText(name)
            self.id_text.setTextInteractionFlags(Qt.NoTextInteraction)

            self.vertical_offset_name = 0
            self.padding_vertical = 0
            self.padding_horizontal = 0

        self.cpp_func = self.get_cpp_func(name)

        self.adjust_size()

    def get_cpp_func(self, name):
        with open(OPERATIONS_FILE, "r") as f:
            data = json.load(f)
            cpp_func = next(item["cpp_func"] for item in data if item.get("name") == name)

            return cpp_func

    def update_positions(self):
        super().update_positions()
        vertical_offset = 5
        margin_horizontal = 0
        
        if self.name != "END":
            self.dates_doc.setTextWidth(self.width - margin_horizontal)
            self.dates_text.setPos(margin_horizontal/2, self.height - self.dates_text.boundingRect().height() - vertical_offset)

    def paint(self, painter, option, widget):
        painter.setBrush(QColor("#ECECEC"))
        painter.drawRoundedRect(QRectF(0, 0, self.width, self.height), 10, 10)