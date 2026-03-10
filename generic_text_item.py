from PyQt5.QtWidgets import QGraphicsTextItem

class GenericTextItem(QGraphicsTextItem):
    def focusOutEvent(self, event):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        super().focusOutEvent(event)

    def contextMenuEvent(self, event):
        pass 