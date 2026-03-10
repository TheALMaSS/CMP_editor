from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtGui import QColor, QPen, QBrush, QFont
from PyQt5.QtCore import Qt
from generic_text_item import GenericTextItem

class CommentBox(QGraphicsRectItem):
    def __init__(self, x, y):
        super().__init__(0, 0, 100, 50)

        self.padding = 15

        self.setPos(x, y)

        self.setBrush(QBrush(QColor("#F1EFDD")))
        self.setPen(QPen(QColor("#96958C"), 1))

        self.setFlags(
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemIsMovable
        )

        self.text = GenericTextItem(self)
        self.text.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text.setDefaultTextColor(QColor("#5F5E59"))
        self.text.setFont(QFont("Arial", 9))
        self.text.setPos(self.padding/2, self.padding/2)

        self.text.document().contentsChanged.connect(self.update_size)

    def update_size(self):
        rect = self.text.boundingRect()

        w = rect.width() + self.padding
        h = rect.height() + self.padding

        self.setRect(0, 0, w, h)