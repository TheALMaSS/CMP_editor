from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import Qt
from node import Node

# Contains the items and their logical connections
class FlowchartScene(QGraphicsScene):
    # ----------------------------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
    # ----------------------------------------------------------------------------------------------

    # TODO: MOVE ALL OBJECT HANDLING BEHAVIOUR HERE