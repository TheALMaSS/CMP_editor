import sys, json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QWidget
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt, QPointF
from flow_view import FlowView
from node import Node
from flow_scene import FlowScene
import os
import json
from PyQt5.QtWidgets import QDialog, QListWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QLabel, QListWidgetItem, QDialogButtonBox
from PyQt5.QtWidgets import QGraphicsTextItem

ACTIONS_FILE = "actions.json"

def load_actions():
    with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    
class ActionPickerDialog(QDialog):
    def __init__(self, actions, parent=None):
        super().__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle("Select Crop Action")
        self.resize(700, 400)
        self.actions = actions
        self.selected = None

        self.list_widget = QListWidget()
        for a in actions:
            self.list_widget.addItem(a["name"])

        self.desc = QTextEdit()
        self.desc.setReadOnly(True)

        left_label = QLabel("Actions")
        right_label = QLabel("Description")

        help_btn = QPushButton("?")
        help_btn.setFixedWidth(30)
        help_btn.clicked.connect(self.open_help)

        header_layout = QHBoxLayout()
        header_layout.addWidget(left_label)
        header_layout.addStretch()
        header_layout.addWidget(help_btn)

        left_layout = QVBoxLayout()
        left_layout.addLayout(header_layout)
        left_layout.addWidget(self.list_widget)

        right_layout = QVBoxLayout()
        right_layout.addWidget(right_label)
        right_layout.addWidget(self.desc)

        # wrap left layout in a container and set width
        left_container = QWidget()
        left_container.setLayout(left_layout)
        left_container.setMinimumWidth(300)  # or use setFixedWidth(250) to lock it

        main_layout = QHBoxLayout()
        main_layout.addWidget(left_container)
        main_layout.addLayout(right_layout, 2)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        outer = QVBoxLayout()
        outer.addLayout(main_layout)
        outer.addWidget(buttons)
        self.setLayout(outer)

        self.list_widget.currentRowChanged.connect(self.on_row_changed)
        if self.list_widget.count():
            self.list_widget.setCurrentRow(0)

    def open_help(self):
        dlg = QDialog(self, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        dlg.setWindowTitle("Help - select a crop action")
        dlg.resize(400, 400)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText("Select a crop action on the left to see its description.\n\n"
                          "When you press OK, the selected action will be assigned to the new node.")

        layout = QVBoxLayout()
        layout.addWidget(text)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dlg.accept)
        layout.addWidget(buttons)

        dlg.setLayout(layout)
        dlg.exec_()

    def on_row_changed(self, row):
        if row < 0 or row >= len(self.actions):
            self.desc.setPlainText("")
            return
        self.desc.setPlainText(self.actions[row].get("description", ""))

    def accept(self):
        row = self.list_widget.currentRow()
        if row < 0:
            super().reject()
            return
        self.selected = self.actions[row]
        super().accept()

class FlowchartApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CMP Editor")
        self.setGeometry(100, 100, 800, 600)
        self.scene = FlowScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#738DB3")))
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.view = FlowView(self.scene, self)
        self.setCentralWidget(self.view)
        self.nodes = []
        self.lines = []
        self.selected_node = None
        self.add_node_btn = QPushButton("Add Node", self)
        self.add_node_btn.move(200, 50)
        self.add_node_btn.clicked.connect(self.add_node)
        self.delete_mode = False
        self.delete_btn = QPushButton("Delete", self)
        self.delete_btn.move(200, 100)
        self.delete_btn.setCheckable(True)
        self.delete_btn.clicked.connect(self.toggle_delete_mode)
        self.export_btn = QPushButton("Export JSON", self)
        self.export_btn.move(200, 150)
        self.export_btn.clicked.connect(self.export_json)
        self.load_btn = QPushButton("Load JSON", self)
        self.load_btn.move(200, 200)
        self.load_btn.clicked.connect(self.load_json)
        self._actions = load_actions()
        self.load_btn = QPushButton("Need Help?", self)
        self.load_btn.move(200, 250)
        self.load_btn.clicked.connect(self.need_help)
        self._actions = load_actions()

    def add_node(self):
        dlg = ActionPickerDialog(self._actions, self)
        if dlg.exec_() != QDialog.Accepted:
            return
        action = dlg.selected

        node = Node(100 + len(self.nodes)*50, 100)
        node.setZValue(1)
        node.action_data = action
        node.name_text.setPlainText(action["name"])

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

    def toggle_delete_mode(self):
        self.delete_mode = self.delete_btn.isChecked()

    def need_help(self):
        return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlowchartApp()
    window.show()
    sys.exit(app.exec_())