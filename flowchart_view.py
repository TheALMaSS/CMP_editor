from PyQt5.QtWidgets import QGraphicsView, QApplication, QMenu, QAction, QColorDialog, QGraphicsTextItem, QColorDialog
from PyQt5.QtCore import Qt, QPoint, QRectF
from PyQt5.QtGui import QPainter
from node import Node
from arrow import BendPoint, Arrow

# Displays a portion of the SCENE and handles user interaction
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

                        if Node == self.selected_node:
                            return
                        
                        arrow = self.selected_node.add_arrow_to(item)
                        self.scene().addItem(arrow)
                        self.scene().addItem(arrow.text_item)
                        self.selected_node = None
                        self.arrow_done = True
                
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
                        if hasattr(arrow, "text_item") and arrow.text_item is not None:
                            self.scene().removeItem(arrow.text_item)
                        self.scene().removeItem(arrow)

                    if item in self.my_window.nodes:
                        self.my_window.nodes.remove(item)
                        self.my_window.update_warnings()

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
                    # TODO: check this. I think it causes a glitch when first a click is made on a node, and then a bend point is moved around
                    super().mousePressEvent(event)

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
        # PANNING MODE - MIDDLE BUTTON
        # ----------------------------------------------------------------------------------------------
        if event.button() == Qt.MiddleButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            return
        
        # ----------------------------------------------------------------------------------------------
        # RIGHT BUTTON
        # ----------------------------------------------------------------------------------------------
        if event.button() == Qt.RightButton:
            item = self.itemAt(event.pos())

            # TODO: check why does it crash when i right click on the text???
            if isinstance(item, QGraphicsTextItem):
                return

            # IF NODE -> SHOW OPTIONS
            if isinstance(item, Node):
                menu = QMenu()

                # CHANGE NODE COLOR
                change_color_action = QAction("Change Color", self)
                def on_change_color():
                    color = QColorDialog.getColor(item.brush().color(), self.my_window, "Select Node Color")
                    item.change_color(color)
                change_color_action.triggered.connect(on_change_color)
                menu.addAction(change_color_action)

                # TOGGLE ON CONSTRAINTS
                toggle_on_constraints_action = QAction("Toggle ON Constraints", self)
                def on_toggle_on_constraints():
                    if not item.constraints_on:
                        item.constraints_on = True
                        item.constraints_text.setVisible(True)
                        old_rect = item.rect()
                        new_height = old_rect.height() + 50
                        item.setRect(old_rect.x(), old_rect.y(), old_rect.width(), new_height)
                        item.update_text_positions()
                toggle_on_constraints_action.triggered.connect(on_toggle_on_constraints)
                menu.addAction(toggle_on_constraints_action)

                # TOGGLE OFF CONSTRAINTS
                toggle_off_constraints_action = QAction("Toggle OFF Constraints", self)
                def on_toggle_off_constraints():
                    if item.constraints_on:
                        item.constraints_on = False
                        item.constraints_text.setVisible(False)
                        old_rect = item.rect()
                        new_height = old_rect.height() - 50
                        item.setRect(old_rect.x(), old_rect.y(), old_rect.width(), new_height)
                        item.update_text_positions()
                toggle_off_constraints_action.triggered.connect(on_toggle_off_constraints)
                menu.addAction(toggle_off_constraints_action)

                # TOGGLE ON RANDOM CHANCE
                toggle_on_random_chance_action = QAction("Toggle ON Random Chance", self)
                def on_toggle_on_random_chance():
                    if not item.random_chance_on:
                        item.random_chance_on = True
                        item.random_chance_text.setVisible(True)
                        old_rect = item.rect()
                        new_height = old_rect.height() + 50
                        item.setRect(old_rect.x(), old_rect.y(), old_rect.width(), new_height)
                        item.update_text_positions()
                toggle_on_random_chance_action.triggered.connect(on_toggle_on_random_chance)
                menu.addAction(toggle_on_random_chance_action)

                # TOGGLE OFF RANDOM CHANCE
                toggle_off_random_chance_action = QAction("Toggle OFF Random Chance", self)
                def on_toggle_off_random_chance():
                    if item.random_chance_on:
                        item.random_chance_on = False
                        item.random_chance_text.setVisible(False)
                        old_rect = item.rect()
                        new_height = old_rect.height() - 50
                        item.setRect(old_rect.x(), old_rect.y(), old_rect.width(), new_height)
                        item.update_text_positions()
                toggle_off_random_chance_action.triggered.connect(on_toggle_off_random_chance)
                menu.addAction(toggle_off_random_chance_action)

                menu.exec_(event.globalPos())
                return

            # IF BEND POINT -> DELETE
            if isinstance(item, BendPoint):
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
            self.selected_node = None
            self.arrow_done = False
        
        # TODO: maybe optimize by not redrawing entire scene, but just the nodes in the node lists
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