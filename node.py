from arrow import Arrow

class Node():
    CORNER_SIZE = 20

    def __init__(self):

        self.outgoing_arrows = []
        self.incoming_arrows = []
        self.setFlag(self.ItemIsMovable)

    def add_arrow_to(self, target_node):
        for arrow in self.outgoing_arrows:
            if arrow.end_node == target_node:
                return arrow
        arrow = Arrow(self, target_node)
        self.outgoing_arrows.append(arrow)
        target_node.incoming_arrows.append(arrow)
        return arrow