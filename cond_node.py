from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtGui import QPolygonF, QBrush, QPen, QColor, QFont, QTextOption
from PyQt5.QtCore import Qt, QPointF
from node import Node

class CondNode(QGraphicsPolygonItem, Node):
    MAX_WIDTH = 300  # maximum allowed width before wrapping text
    PADDING = 60     # padding around text inside the diamond

    def __init__(self, x, y, text="conditional expr here"):
        QGraphicsPolygonItem.__init__(self)
        Node.__init__(self)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setPos(x, y)

        self.text = text

        # APPEARANCE
        self.setBrush(QBrush(QColor("#A58DCA")))
        self.setPen(QPen(Qt.black, 2))

        # TEXT FIELD
        self.text_box = QGraphicsTextItem(self)
        self.text_box.setFont(QFont("Arial", 10, QFont.Bold))
        self.text_box.setDefaultTextColor(Qt.black)
        # Center text inside the QGraphicsTextItem
        option = QTextOption()
        option.setAlignment(Qt.AlignCenter)
        self.text_box.document().setDefaultTextOption(option)

        self.update_diamond()

    def update_diamond(self):
        # Set initial text
        font = self.text_box.font()
        doc = self.text_box.document()
        doc.setDefaultFont(font)
        doc.setPlainText(" ".join(self.text) if isinstance(self.text, list) else str(self.text))
        doc.adjustSize()

        # Measure text size
        text_width = doc.size().width() + self.PADDING
        text_height = doc.size().height() + self.PADDING

        # Wrap text by words if width exceeds MAX_WIDTH
        if text_width > self.MAX_WIDTH:
            words = self.text.split(" ")
            wrapped_lines = []
            current_line = ""
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                doc.setPlainText(test_line)
                doc.adjustSize()
                if doc.size().width() + self.PADDING > self.MAX_WIDTH:
                    if current_line:  # push current line to wrapped_lines
                        wrapped_lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            if current_line:
                wrapped_lines.append(current_line)

            # Update text with line breaks
            wrapped_text = "\n".join(wrapped_lines)
            self.text_box.setPlainText(wrapped_text)
            doc.adjustSize()
            text_width = min(doc.size().width() + self.PADDING, self.MAX_WIDTH)
            text_height = doc.size().height() + self.PADDING

        # Diamond dimensions based on text
        width = text_width
        height = text_height * 1.5

        # Define diamond points
        points = [
            QPointF(width / 2, 0),
            QPointF(width, height / 2),
            QPointF(width / 2, height),
            QPointF(0, height / 2)
        ]
        self.setPolygon(QPolygonF(points))

        # Center the text
        bounds = self.text_box.boundingRect()
        x = (width - bounds.width()) / 2
        y = (height - bounds.height()) / 2
        self.text_box.setPos(x, y)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arrow in getattr(self, "outgoing_arrows", []):
                arrow.update_path()
            for arrow in getattr(self, "incoming_arrows", []):
                arrow.update_path()
        return super().itemChange(change, value)