from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import Qt
from node import Node

class FlowScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.selected_node = None

    def mousePressEvent(self, event):
        pos = event.scenePos()
        items = self.items(pos)
        nodes = [i for i in items if isinstance(i, Node)]

        if nodes:
            node = nodes[0]
            # ----- SHIFT + LEFT CLICK REQUIRED -----
            if event.button() == Qt.LeftButton and event.modifiers() & Qt.ShiftModifier:
                if self.selected_node and self.selected_node != node:
                    # Create arrow from previously selected node to current
                    arrow = self.selected_node.add_arrow_to(node)
                    self.addItem(arrow)
                    self.addItem(arrow.text_item)
                    self.selected_node = None
                else:
                    # Select starting node for next arrow
                    self.selected_node = node
            else:
                # Normal click does nothing for arrows
                self.selected_node = None
        else:
            self.selected_node = None

        super().mousePressEvent(event)