from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import Qt
from node import Node

# Contains the items and their logical connections
class FlowchartScene(QGraphicsScene):
    # ----------------------------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
#    def mousePressEvent(self, event):
#        pos = event.scenePos()
#        items = self.items(pos)
#        nodes = [i for i in items if isinstance(i, Node)]

#        if nodes:
#            node = nodes[0]
            
            # ADD AN ARROW: SHIFT + CLICK
#            if event.button() == Qt.LeftButton and event.modifiers() & Qt.ShiftModifier:

                # Create arrow from previously selected node to current
#                if self.selected_node and self.selected_node != node:
#                    arrow = self.selected_node.add_arrow_to(node)
#                    self.addItem(arrow)
#                    self.addItem(arrow.text_item)
#                    self.selected_node = None

                # Select starting node for next arrow
#                else:
#                    self.selected_node = node

            # Normal click does nothing for arrows
#            else:
#                self.selected_node = None
#        else:
#            self.selected_node = None

#        super().mousePressEvent(event)
    # ----------------------------------------------------------------------------------------------