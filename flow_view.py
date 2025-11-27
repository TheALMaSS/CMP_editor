from PyQt5.QtWidgets import QGraphicsView, QApplication
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter
from node import Node

# Displays a portion of the SCENE and handles user interaction
class FlowView(QGraphicsView):
    def __init__(self, scene, window):
        super().__init__(scene)
        self.window = window
        self.setRenderHint(QPainter.Antialiasing) # TODO: check
        self._panning = False
        self._pan_start = QPoint()
        self.resizing_node = None

    def mousePressEvent(self, event):
        # ----------------------------------------------------------------------------------------------
        # DELETE MODE (left click)
        # ----------------------------------------------------------------------------------------------
        if event.button() == Qt.LeftButton and getattr(self.window, "delete_mode", False):
            item = self.itemAt(event.pos())
            if item is None:
                return

            # If clicking on text inside node -> delete entire node
            parent = item.parentItem()
            if parent is not None and (hasattr(parent, "outgoing_arrows") or hasattr(parent, "incoming_arrows")):
                item = parent

            # If clicking on text associated to arrow -> delete arrow
            if parent is not None and hasattr(parent, "start_node"):
                item = parent

            # Delete an arrow
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

            # Delete a node
            if hasattr(item, "outgoing_arrows") or hasattr(item, "incoming_arrows"):
                for arrow in list(getattr(item, "outgoing_arrows", [])):
                    if arrow in getattr(arrow.end_node, "incoming_arrows", []):
                        arrow.end_node.incoming_arrows.remove(arrow)
                    if hasattr(arrow, "text_item") and arrow.text_item is not None:
                        self.scene().removeItem(arrow.text_item)
                    self.scene().removeItem(arrow)

                for arrow in list(getattr(item, "incoming_arrows", [])):
                    if arrow in getattr(arrow.start_node, "outgoing_arrows", []):
                        arrow.start_node.outgoing_arrows.remove(arrow)
                    if hasattr(arrow, "text_item") and arrow.text_item is not None:
                        self.scene().removeItem(arrow.text_item)
                    self.scene().removeItem(arrow)

                if item in self.window.nodes:
                    self.window.nodes.remove(item)

                self.scene().removeItem(item)
                return

            self.scene().removeItem(item)
            return

        # ----------------------------------------------------------------------------------------------
        # ADD BEND POINT (left click on arrow when NOT deleting)
        # ----------------------------------------------------------------------------------------------
        if event.button() == Qt.LeftButton and not getattr(self.window, "delete_mode", False):
            # map click to scene coordinates
            scene_pos = self.mapToScene(event.pos())
            item = self.itemAt(event.pos())
            if item is not None:
                # If the clicked item is an Arrow (QGraphicsPathItem)
                if hasattr(item, "add_bend_point"):
                    item.add_bend_point(scene_pos)
                    return

        # ----------------------------------------------------------------------------------------------
        # PANNING MODE
        # ----------------------------------------------------------------------------------------------
        if event.button() == Qt.MiddleButton and not getattr(self.window, "delete_mode", False):
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            return
        
        # ----------------------------------------------------------------------------------------------
        # CLICKING ON A NODE: EITHER MOVING OR RESIZING
        # ----------------------------------------------------------------------------------------------
        if isinstance(item, Node):
            pos_in_node = item.mapFromScene(self.mapToScene(event.pos()))
            rect = item.rect()
            if rect.right() - Node.CORNER_SIZE < pos_in_node.x() < rect.right() and \
            rect.bottom() - Node.CORNER_SIZE < pos_in_node.y() < rect.bottom():
                self.resizing_node = item
                return

        # ----------------------------------------------------------------------------------------------
        # MOVING AN OBJECT FLAGGED AS ItemIsMovable IS HANDLED BY QGraphics
        # ----------------------------------------------------------------------------------------------
        super().mousePressEvent(event)

    # ----------------------------------------------------------------------------------------------
    def mouseMoveEvent(self, event):

        if self._panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            return

        if self.resizing_node is not None:
            node = self.resizing_node
            # Map mouse pos to node coordinates
            scene_pos = self.mapToScene(event.pos())
            node_pos = node.mapFromScene(scene_pos)

            new_width = max(node_pos.x(), 30)
            new_height = max(node_pos.y(), 30)
            node.setRect(0, 0, new_width, new_height)
            node.update_text_positions()
            # Update connected arrows
            for arrow in node.outgoing_arrows + node.incoming_arrows:
                arrow.update_path()
            return

        super().mouseMoveEvent(event)

    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton and self._panning:
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
            return
        
        if self.resizing_node is not None:
            self.resizing_node = None

        super().mouseReleaseEvent(event)
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    # ZOOM IN AND OUT WITH SHIFT + WHEEL
    # ----------------------------------------------------------------------------------------------
    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            # Zoom factor
            zoom_in_factor = 1.15
            zoom_out_factor = 1 / zoom_in_factor

            # Determine direction
            if event.angleDelta().y() > 0:
                factor = zoom_in_factor
            else:
                factor = zoom_out_factor

            self.scale(factor, factor)
        else:
            # Default behavior (scroll)
            super().wheelEvent(event)