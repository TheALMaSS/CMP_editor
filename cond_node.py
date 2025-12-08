from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtGui import QPolygonF, QBrush, QPen, QColor, QFont, QTextOption
from PyQt5.QtCore import Qt, QPointF
from node import Node

class CondNode(QGraphicsPolygonItem, Node):
    MAX_WIDTH = 300  # maximum allowed width before wrapping text
    PADDING = 60     # padding around text inside the diamond

    def __init__(self, x, y, width=140, height=140, text=""):

        #id = int(self.scene().cond_nodes[-1].id) + 1 if self.scene().cond_nodes else 1

        QGraphicsPolygonItem.__init__(self)
        Node.__init__(self)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setPos(x, y)
        
        self.width = width
        self.height = height

        self.text = text

        # APPEARANCE
        self.setBrush(QBrush(QColor("#A58DCA")))
        self.setPen(QPen(Qt.black, 2))

        # TEXT FIELDS
        # Center text inside the QGraphicsTextItem
        option = QTextOption()
        option.setAlignment(Qt.AlignCenter)

        self.id_text = QGraphicsTextItem("ID", self)
        self.id_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.id_text.document().setDefaultTextOption(option)
        self.id_text.document().contentsChanged.connect(self.update_text_positions)
        self.id_text.setTextInteractionFlags(Qt.TextEditorInteraction)
        
        self.name_text = QGraphicsTextItem(text, self)
        self.name_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.name_text.document().contentsChanged.connect(self.update_text_positions)

        self.update_diamond()

    def update_diamond(self):
        # Set initial text
        font = self.name_text.font()
        doc = self.name_text.document()
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
            self.name_text.setPlainText(wrapped_text)
            doc.adjustSize()
            text_width = min(doc.size().width() + self.PADDING, self.MAX_WIDTH)
            text_height = doc.size().height() + self.PADDING

        # Diamond dimensions based on text
        self.width = text_width
        self.height = text_height * 1.5

        # Define diamond points
        points = [
            QPointF(self.width / 2, 0),
            QPointF(self.width, self.height / 2),
            QPointF(self.width / 2, self.height),
            QPointF(0, self.height / 2)
        ]
        self.setPolygon(QPolygonF(points))

        # Center the text
        bounds = self.name_text.boundingRect()
        x = (self.width - bounds.width()) / 2
        y = (self.height - bounds.height()) / 2
        self.name_text.setPos(x, y)

        # Center the text
        bounds = self.id_text.boundingRect()
        x = (self.width - bounds.width()) / 2
        self.id_text.setPos((self.width - bounds.width()) / 2, (self.height - bounds.height()) / 2  - 50)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arrow in getattr(self, "outgoing_arrows", []):
                arrow.update_path()
            for arrow in getattr(self, "incoming_arrows", []):
                arrow.update_path()
        return super().itemChange(change, value)
    
    def update_text_positions(self):
        option = QTextOption()
        option.setAlignment(Qt.AlignCenter)

        # center id_text
        self.id_text.setTextWidth(self.width)
        self.id_text.document().setDefaultTextOption(option)

        id_bounds = self.id_text.boundingRect()
        self.id_text.setPos((self.width - id_bounds.width()) / 2, (self.height - id_bounds.height()) / 2  - 50)

        # center name_text
        self.name_text.setTextWidth(self.width)
        self.name_text.document().setDefaultTextOption(option)

        name_bounds = self.name_text.boundingRect()
        self.name_text.setPos((self.width - name_bounds.width()) / 2, (self.height - name_bounds.height()) / 2)