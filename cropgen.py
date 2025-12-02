import sys, json
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QDialog, QTextEdit, QLabel, QVBoxLayout, QFrame, QSplitter
from flowchart_view import FlowchartView
from flowchart_scene import FlowchartScene
from node import Node
from choose_operation_dialog import ChooseOperationDialog
from css_styles import button_style, warnings_box_style, warnings_title_style, left_panel_style
OPERATIONS_FILE = "operations.json"

def load_operations():
    with open(OPERATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

class FlowchartApp(QMainWindow):
    # ------------------------------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CMP Editor")
        self.setGeometry(100, 100, 1100, 600)

        self.nodes = []
        self.lines = []
        self.selected_node = None
        self.delete_mode = False
        self._operations = load_operations()

        # -------------------------------------------------------------------
        # SCENE AND VIEW
        self.scene = FlowchartScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#C1C1C1")))
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.view = FlowchartView(self.scene, self)

        # -------------------------------------------------------------------
        # LEFT PANEL
        self.left_panel = QFrame()
        self.left_panel.setStyleSheet(left_panel_style)
        self.left_panel.setMinimumWidth(100)

        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(10)

        # -------------------------------------------------------------------
        # BUTTONS
        self.add_node_btn = QPushButton("Add Node")
        self.add_node_btn.setStyleSheet(button_style)
        self.add_node_btn.clicked.connect(self.add_node)
        left_layout.addWidget(self.add_node_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setCheckable(True)
        self.delete_btn.setStyleSheet(button_style)
        self.delete_btn.clicked.connect(self.toggle_delete_mode)
        left_layout.addWidget(self.delete_btn)

        self.export_btn = QPushButton("Export JSON")
        self.export_btn.setStyleSheet(button_style)
        self.export_btn.clicked.connect(self.export_json)
        left_layout.addWidget(self.export_btn)

        self.load_btn = QPushButton("Load JSON")
        self.load_btn.setStyleSheet(button_style)
        self.load_btn.clicked.connect(self.load_json)
        left_layout.addWidget(self.load_btn)

        self.help_btn = QPushButton("Need Help?")
        self.help_btn.setStyleSheet(button_style)
        self.help_btn.clicked.connect(self.need_help)

        # Add the buttons to the left panel
        left_layout.addWidget(self.help_btn)
        left_layout.addStretch()

        # Warnings box with title, add to the left panel
        title_label = QLabel("Warnings")
        title_label.setStyleSheet(warnings_title_style)
        left_layout.addWidget(title_label)
        self.warnings_box = QTextEdit()
        self.warnings_box.setReadOnly(True)
        self.warnings_box.setFixedHeight(240)
        self.warnings_box.setStyleSheet(warnings_box_style)
        left_layout.addWidget(self.warnings_box)

        # -------------------------------------------------------------------
        # SPLITTER: LEFT PANEL | MAIN SCENE
        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.view)
        splitter.setSizes([300, 800])
        splitter.setHandleWidth(6)

        self.setCentralWidget(splitter)
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def update_warnings(self):
        warnings = []
        names = [node.name_text.toPlainText() for node in self.nodes]
        if "START" not in names:
            warnings.append("△ Warning: No node named 'START' exists.")

        # add other structural checks here
        self.warnings_box.setPlainText("\n".join(warnings))
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def add_node(self):
        dlg = ChooseOperationDialog(self._operations, self)
        if dlg.exec_() != QDialog.Accepted:
            return
        operation = dlg.selected

        node = Node(100 + len(self.nodes)*50, 100)
        node.setZValue(1)
        node.operation_data = operation
        node.name_text.setPlainText(operation["name"])

        self.scene.addItem(node)
        self.nodes.append(node)
        self.update_warnings()
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    # TODO: move to scene
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
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
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
                    "branching_condition": arrow.text_item.toPlainText(),
                    "bend_points": [[bp.scenePos().x(), bp.scenePos().y()] for bp in arrow.bend_points]
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
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def load_json(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open JSON", "", "JSON Files (*.json)")
        if not filename:
            return

        # Clear all arrows
        for node in list(self.nodes):
            for arrow in list(node.outgoing_arrows):
                if arrow.text_item:
                    self.scene.removeItem(arrow.text_item)
                for bp in arrow.bend_points:
                    self.scene.removeItem(bp)
                self.scene.removeItem(arrow)
                node.outgoing_arrows.remove(arrow)
            for arrow in list(node.incoming_arrows):
                if arrow.text_item:
                    self.scene.removeItem(arrow.text_item)
                for bp in arrow.bend_points:
                    self.scene.removeItem(bp)
                self.scene.removeItem(arrow)
                node.incoming_arrows.remove(arrow)

        # Clear nodes
        for node in list(self.nodes):
            self.scene.removeItem(node)
        self.nodes.clear()

        # Load nodes
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

        # Create arrows with bend points
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
                    # recreate bend points
                    for bp_coords in arrow_data.get("bend_points", []):
                        arrow.add_bend_point(QPointF(bp_coords[0], bp_coords[1]))
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def toggle_delete_mode(self):
        self.delete_mode = self.delete_btn.isChecked()
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def need_help(self):
        return
    # ------------------------------------------------------------------------------------------------


# MAIN
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlowchartApp()
    window.show()
    sys.exit(app.exec_())