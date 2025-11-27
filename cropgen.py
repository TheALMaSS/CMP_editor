import sys, json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
from PyQt5.QtGui import QColor, QPainter, QBrush
from PyQt5.QtCore import Qt
from flow_view import FlowView
from node import Node
from flow_scene import FlowScene

class FlowchartApp(QMainWindow):

    # ----------------------------------------------------------------------------------------------
    def __init__(self):
        super().__init__()

        # Init WINDOW
        self.setWindowTitle("CMP Editor")
        self.setGeometry(100, 100, 800, 600)

        # Init SCENE
        self.scene = FlowScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#738DB3")))
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)

        # Init VIEW
        self.view = FlowView(self.scene, self)
        self.setCentralWidget(self.view)

        # Init DATA STRUCTURES
        self.nodes = []
        self.lines = []
        self.selected_node = None

        # Init BUTTONS
        self.add_node_btn = QPushButton("Add Node", self)
        self.add_node_btn.move(700, 50)
        self.add_node_btn.clicked.connect(self.add_node)

        self.delete_mode = False
        self.delete_btn = QPushButton("Delete", self)
        self.delete_btn.move(700, 100)
        self.delete_btn.setCheckable(True)
        self.delete_btn.clicked.connect(self.toggle_delete_mode)

        self.export_btn = QPushButton("Export JSON", self)
        self.export_btn.move(700, 150)
        self.export_btn.clicked.connect(self.export_json)

        self.load_btn = QPushButton("Load JSON", self)
        self.load_btn.move(700, 200)
        self.load_btn.clicked.connect(self.load_json)
    # ----------------------------------------------------------------------------------------------

    def add_node(self):
        node = Node(100 + len(self.nodes)*50, 100)
        node.setZValue(1)
        self.scene.addItem(node)
        self.nodes.append(node)

    def mousePressEvent(self, event):
        pos = self.view.mapToScene(event.pos())
        items = self.scene.items(pos)
        nodes = [i for i in items if isinstance(i, Node)]
        if nodes:
            node = nodes[0]
            if event.modifiers() & Qt:  # Shift+Click for arrows
                if self.selected_node and self.selected_node != node:
                    arrow = self.selected_node.add_arrow_to(node)
                    self.scene.addItem(arrow)
                    self.scene.addItem(arrow.text_item)
                    self.selected_node = None
                else:
                    self.selected_node = node
            else:  # Normal click selects node
                self.selected_node = node
        else:
            self.selected_node = None
        super().mousePressEvent(event)

    def export_json(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Diagram JSON", "", "JSON Files (*.json)")
        if not filename:
            return

        data = []
        for node in self.nodes:
            outgoing = []
            for arrow in node.outgoing_arrows:
                outgoing.append({
                    "destination_id": arrow.end_node.id_text.toPlainText(),
                    "branching_condition": arrow.text_item.toPlainText()
                })
            data.append({
                "dates": node.dates_text.toPlainText(),
                "operation_id": node.id_text.toPlainText(),
                "operation_name": node.name_text.toPlainText(),
                "x": node.x(),
                "y": node.y(),
                "width": node.rect().width(),
                "height": node.rect().height(),
                "outgoing": outgoing
            })

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Exported {filename}")

    def load_json(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open JSON", "", "JSON Files (*.json)")
        if not filename:
            return

        # Clear all arrows first
        for node in list(self.nodes):
            for arrow in list(node.outgoing_arrows):
                if arrow.text_item:
                    self.scene.removeItem(arrow.text_item)
                self.scene.removeItem(arrow)
                node.outgoing_arrows.remove(arrow)
            for arrow in list(node.incoming_arrows):
                if arrow.text_item:
                    self.scene.removeItem(arrow.text_item)
                self.scene.removeItem(arrow)
                node.incoming_arrows.remove(arrow)

        # Clear nodes from scene
        for node in list(self.nodes):
            self.scene.removeItem(node)
        self.nodes.clear()

        # Load new nodes
        with open(filename, "r") as f:
            data = json.load(f)

        node_map = {}
        for node_data in data:
            width = node_data.get("width", 120)
            height = node_data.get("height", 60)
            node = Node(node_data["x"], node_data["y"], width=width, height=height)
            node.setZValue(1)
            node.dates_text.setPlainText(node_data.get("dates", ""))
            node.id_text.setPlainText(node_data.get("operation_id", ""))
            node.name_text.setPlainText(node_data.get("operation_name", ""))
            node.update_text_positions()
            self.scene.addItem(node)
            self.nodes.append(node)
            node_map[node_data["operation_id"]] = node

        # Create arrows
        for node_data in data:
            source_node = node_map.get(node_data["operation_id"])
            if not source_node:
                continue
            for arrow_data in node_data.get("outgoing", []):
                dest_node = node_map.get(arrow_data["destination_id"])
                if dest_node:
                    arrow = source_node.add_arrow_to(dest_node)
                    arrow.text_item.setPlainText(arrow_data.get("branching_condition", ""))
                    self.scene.addItem(arrow)
                    self.scene.addItem(arrow.text_item)

    def toggle_delete_mode(self):
        self.delete_mode = self.delete_btn.isChecked()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlowchartApp()
    window.show()
    sys.exit(app.exec_())