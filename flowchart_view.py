from PyQt5.QtWidgets import QGraphicsView, QApplication, QMenu, QGraphicsTextItem, QPushButton
from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtGui import QPainter
from node import Node
from prob_node import ProbNode
from cond_node import CondNode
from op_node import OpNode
from arrow import BendPoint, Arrow

# Displays a portion of the SCENE inside the WINDOW and handles user interaction
class FlowchartView(QGraphicsView):
    def __init__(self, scene, window):
        super().__init__(scene)
        self.my_window = window
        self.setRenderHint(QPainter.Antialiasing)
        self._panning = False
        self._pan_start = QPoint()
        self.resizing_node = None
        self.selected_node = None
        self.arrow_done = False
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.clipboard = []

        # BUTTONS AND THINGS INSIDE THE VIEW
        self.scroll_back_btn = QPushButton("Scroll back to content", self)
        self.scroll_back_btn.clicked.connect(self.scroll_to_center_of_mass)
        self.scroll_back_btn.resize(220, 40)

    def scroll_to_center_of_mass(self):
        items = self.scene().items()
        if not items:
            return
        center = QPointF(0, 0)
        for item in items:
            center += item.sceneBoundingRect().center()
        center /= len(items)
        self.centerOn(center)

    # --------------------------------------------------------------------
    # USER INTERACTION FUNCTIONS
    def mousePressEvent(self, event):
        # IF LEFT CLICK
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())

            # --------------------------------------------------------------------
            # ARROW MODE (if arrow mode in on)
            # --------------------------------------------------------------------
            if getattr(self.my_window, "arrow_mode"):
                if item is None:
                    return
                
                # If clicking on text inside node -> select parent node
                parent = item.parentItem()
                if parent is not None and isinstance(parent, Node):
                    item = parent

                if isinstance(item, Node):

                    # If a start node has already been selected
                    if (self.selected_node is not None):

                        if item == self.selected_node:
                            self.arrow_done = True
                        
                        else:
                            arrow = self.selected_node.add_arrow_to(item)
                            self.scene().addItem(arrow)
                            self.scene().addItem(arrow.text_item)
                            self.arrow_done = True

                            # If the starting node is a probnode, then arrow needs text with %
                            if isinstance(self.selected_node, CondNode):
                                arrow.text_item.setVisible(True)
                                arrow.set_text("YES/NO")

                            # If the starting node is a condnode, then arrow needs text with yes/no
                            if isinstance(self.selected_node, ProbNode):
                                arrow.text_item.setVisible(True)
                                arrow.set_text("XX%")
                
                    # If a start node has NOT already been selected
                    else:
                        self.selected_node = item

            # --------------------------------------------------------------------
            # DELETE MODE (if delete mode in on)
            # --------------------------------------------------------------------
            elif getattr(self.my_window, "delete_mode"):
                if item is None:
                    return

                # If clicking on text inside node -> delete entire node
                parent = item.parentItem()
                if isinstance(parent, Node):
                    item = parent

                # If clicking on text associated to arrow -> delete arrow
                if isinstance(parent, Arrow):
                    item = parent

                # Delete an arrow
                if isinstance(item, Arrow):
                    start = item.start_node
                    end = item.end_node

                    for bp in list(item.bend_points):
                        self.scene().removeItem(bp)
                    item.bend_points.clear()

                    if item in getattr(start, "outgoing_arrows", []):
                        start.outgoing_arrows.remove(item)
                    if item in getattr(end, "incoming_arrows", []):
                        end.incoming_arrows.remove(item)

                    if hasattr(item, "text_item") and item.text_item is not None:
                        self.scene().removeItem(item.text_item)

                    self.scene().removeItem(item)
                    return

                # Delete a node
                if isinstance(item, Node):
                    for arrow in list(getattr(item, "outgoing_arrows", [])):
                        if arrow in getattr(arrow.end_node, "incoming_arrows", []):
                            arrow.end_node.incoming_arrows.remove(arrow)
                        if hasattr(arrow, "text_item"):
                            self.scene().removeItem(arrow.text_item)
                        for bp in list(arrow.bend_points):
                            self.scene().removeItem(bp)
                        arrow.bend_points.clear()
                        self.scene().removeItem(arrow)

                    for arrow in list(getattr(item, "incoming_arrows", [])):
                        if arrow in getattr(arrow.start_node, "outgoing_arrows", []):
                            arrow.start_node.outgoing_arrows.remove(arrow)
                        if hasattr(arrow, "text_item"):
                            self.scene().removeItem(arrow.text_item)
                        for bp in list(arrow.bend_points):
                            self.scene().removeItem(bp)
                        arrow.bend_points.clear()
                        self.scene().removeItem(arrow)

                    if item in self.my_window.op_nodes:
                        self.my_window.op_nodes.remove(item)

                    if item in self.my_window.prob_nodes:
                        self.my_window.prob_nodes.remove(item)

                    if item in self.my_window.cond_nodes:
                        self.my_window.cond_nodes.remove(item)

                    self.scene().removeItem(item)
                    return

            # ------------------ IF NO SPECIAL MODE IS SELECTED
            else:
                # map click to scene coordinates
                scene_pos = self.mapToScene(event.pos())

                # ----------------------------------------------------------------------------------------------
                # ADD BEND POINT (click on arrow)
                # ----------------------------------------------------------------------------------------------
                if isinstance(item, Arrow):
                        item.add_bend_point(scene_pos)
                        return
                
                # ----------------------------------------------------------------------------------------------
                # MOVE BEND POINT (click on bend point)
                # ----------------------------------------------------------------------------------------------
                if isinstance(item, BendPoint):
                    super().mousePressEvent(event)

                # ----------------------------------------------------------------------------------------------
                # CLICKING ON A NODE: EITHER MOVING OR RESIZING
                # ----------------------------------------------------------------------------------------------
                #if isinstance(item, Node):
                #    pos_in_node = item.mapFromScene(self.mapToScene(event.pos()))
                #    rect = item.boundingRect()
                #    if rect.right() - Node.CORNER_SIZE < pos_in_node.x() < rect.right() and \
                #    rect.bottom() - Node.CORNER_SIZE < pos_in_node.y() < rect.bottom():
                #        self.resizing_node = item
                #        return

        # ----------------------------------------------------------------------------------------------
        # PANNING MODE - MIDDLE BUTTON
        # ----------------------------------------------------------------------------------------------
        elif event.button() == Qt.MiddleButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            return
        
        # ----------------------------------------------------------------------------------------------
        # IF RIGHT CLICK
        # ----------------------------------------------------------------------------------------------
        elif event.button() == Qt.RightButton:
            item = self.itemAt(event.pos())

            # IF NODE -> SHOW OPTIONS
            if isinstance(item, Node):
                menu = QMenu()

                menu.exec_(event.globalPos())

            # IF BEND POINT -> DELETE
            elif isinstance(item, BendPoint):
                item.arrow.bend_points.remove(item)
                item.scene().removeItem(item)
                item.arrow.update_path()

            return

        # ----------------------------------------------------------------------------------------------
        # OTHER. MOVING AN OBJECT FLAGGED AS ItemIsMovable IS HANDLED BY QGraphics
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

        if self.arrow_done:
            self.window().arrow_mode = False
            self.window().add_arrow_btn.setChecked(False)
            self.window().update_mode_indicator()
            self.selected_node = None
            self.arrow_done = False
            for item in self.scene().selectedItems():
                item.setSelected(False)

        self.scene().update()
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

    # ----------------------------------------------------------------------------------------------
    # KEYBOARD
    # ----------------------------------------------------------------------------------------------
    def keyPressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        # Ctrl+C ---------------------------------------------
        if event.key() == Qt.Key_C and modifiers == Qt.ControlModifier:
            selected_items = self.scene().selectedItems()
            if selected_items:
                for item in selected_items:
                    if isinstance(item, Node):
                        self.clipboard.append({
                            'type': type(item),
                            'name': getattr(item, 'name', None),
                            'width': item.width,
                            'height': item.height,
                            'dates': getattr(item, 'dates_doc', None),
                            'cpp_cond': getattr(item, 'cpp_cond', None),
                            'pos': item.pos()
                        })

        # Ctrl+V ---------------------------------------------
        elif event.key() == Qt.Key_V and modifiers == Qt.ControlModifier:
            if self.clipboard:
                for item in self.clipboard:
                    # Only if cond node with condition
                    if item['cpp_cond'] is not None:
                        new_node = item['type'](item['name'], item['cpp_cond'])
                    else:
                        new_node = item['type'](item['name'])

                    # Basic stuff
                    new_node.width = item['width']
                    new_node.height = item['height']
                    new_node.setPos(item['pos'] + QPoint(20, 20))

                    # Only if op node with dates
                    if hasattr(new_node, 'dates_doc') and item['dates'] is not None:
                        new_node.dates_doc.setHtml(item['dates'].toHtml())

                    # Add to scene
                    self.scene().addItem(new_node)

                    # Add to list
                    if hasattr(self.my_window, 'op_nodes') and isinstance(new_node, OpNode):
                        self.my_window.op_nodes.append(new_node)
                    elif hasattr(self.my_window, 'prob_nodes') and isinstance(new_node, ProbNode):
                        self.my_window.prob_nodes.append(new_node)
                    elif hasattr(self.my_window, 'cond_nodes') and isinstance(new_node, CondNode):
                        self.my_window.cond_nodes.append(new_node)

                # Empty clipboard
                self.clipboard = []

        else:
            super().keyPressEvent(event)