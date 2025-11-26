from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter

class FlowView(QGraphicsView):
    def __init__(self, scene, window):
        super().__init__(scene)
        self.window = window
        self.setRenderHint(QPainter.Antialiasing)
        self._panning = False
        self._pan_start = QPoint()

    def mousePressEvent(self, event):
        # DELETE MODE (left click)
        if event.button() == Qt.LeftButton and getattr(self.window, "delete_mode", False):
            item = self.itemAt(event.pos())
            if item is None:
                return

            # If clicking on text inside node → treat parent as node
            parent = item.parentItem()
            if parent is not None and (hasattr(parent, "outgoing_arrows") or hasattr(parent, "incoming_arrows")):
                item = parent

            # -------- DELETE ARROW --------
            if hasattr(item, "start_node") and hasattr(item, "end_node"):
                start = item.start_node
                end = item.end_node

                if item in getattr(start, "outgoing_arrows", []):
                    start.outgoing_arrows.remove(item)
                if item in getattr(end, "incoming_arrows", []):
                    end.incoming_arrows.remove(item)

                if hasattr(item, "text_item") and item.text_item is not None:
                    self.scene().removeItem(item.text_item)

                self.scene().removeItem(item)
                return

            # -------- DELETE NODE --------
            if hasattr(item, "outgoing_arrows") or hasattr(item, "incoming_arrows"):

                # Remove outgoing arrows
                for arrow in list(getattr(item, "outgoing_arrows", [])):
                    if arrow in getattr(arrow.end_node, "incoming_arrows", []):
                        arrow.end_node.incoming_arrows.remove(arrow)
                    if hasattr(arrow, "text_item") and arrow.text_item is not None:
                        self.scene().removeItem(arrow.text_item)
                    self.scene().removeItem(arrow)

                # Remove incoming arrows
                for arrow in list(getattr(item, "incoming_arrows", [])):
                    if arrow in getattr(arrow.start_node, "outgoing_arrows", []):
                        arrow.start_node.outgoing_arrows.remove(arrow)
                    if hasattr(arrow, "text_item") and arrow.text_item is not None:
                        self.scene().removeItem(arrow.text_item)
                    self.scene().removeItem(arrow)

                # Remove node from global node list
                if item in self.window.nodes:
                    self.window.nodes.remove(item)

                # Remove node itself
                self.scene().removeItem(item)
                return

            # Fallback for unexpected items
            self.scene().removeItem(item)
            return

        # -------- PANNING --------
        if event.button() == Qt.MiddleButton and not getattr(self.window, "delete_mode", False):
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton and self._panning:
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
            return
        super().mouseReleaseEvent(event)