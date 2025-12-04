import sys, json, re
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QDialog, QTextEdit, QLabel, QVBoxLayout, QFrame, QSplitter
from flowchart_view import FlowchartView
from flowchart_scene import FlowchartScene
from node import Node
from prob_node import ProbNode
from choose_operation_dialog import ChooseOperationDialog
from op_node import OpNode
from prob_node import ProbNode
from cond_node import CondNode
from choose_condition_dialog import ChooseConditionDialog
from validate_dialog import ValidateDialog
from css_styles import button_style, validate_button_style, left_panel_style, delete_button_style, arrow_button_style, delete_mode_label_style, arrow_mode_label_style
OPERATIONS_FILE = "operations.json"
CONDITIONS_FILE = "conditions.json"

def load_operations():
    with open(OPERATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    
def load_conditions():
        with open(CONDITIONS_FILE,  "r", encoding="utf-8") as f:
            return json.load(f)

class FlowchartWindow(QMainWindow):
    # ------------------------------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CMP Editor")
        self.setGeometry(100, 100, 1100, 600)

        self.op_nodes = []
        self.prob_nodes = []
        self.cond_nodes = []
        self.arrows = []
        self.delete_mode = False
        self.arrow_mode = False
        self._operations = load_operations()
        self._conditions = load_conditions()

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
        left_layout.setContentsMargins(20, 12, 20, 12)
        left_layout.setSpacing(10)

        # -------------------------------------------------------------------
        # BUTTONS
        self.add_node_btn = QPushButton("Add Operation Node")
        self.add_node_btn.setStyleSheet(button_style)
        self.add_node_btn.clicked.connect(self.add_operation_node)
        left_layout.addWidget(self.add_node_btn)

        self.add_prob_node_btn = QPushButton("Add Probability Node")
        self.add_prob_node_btn.setStyleSheet(button_style)
        self.add_prob_node_btn.clicked.connect(self.add_probability_node)
        left_layout.addWidget(self.add_prob_node_btn)

        self.add_cond_node_btn = QPushButton("Add Conditional Node")
        self.add_cond_node_btn.setStyleSheet(button_style)
        self.add_cond_node_btn.clicked.connect(self.add_conditional_node)
        left_layout.addWidget(self.add_cond_node_btn)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet("color: #525252;")
        left_layout.addWidget(line)

        self.add_arrow_btn = QPushButton("Add Arrow")
        self.add_arrow_btn.setCheckable(True)
        self.add_arrow_btn.setStyleSheet(arrow_button_style)
        self.add_arrow_btn.clicked.connect(self.toggle_arrow_mode)
        left_layout.addWidget(self.add_arrow_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setCheckable(True)
        self.delete_btn.setStyleSheet(delete_button_style)
        self.delete_btn.clicked.connect(self.toggle_delete_mode)
        left_layout.addWidget(self.delete_btn)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Plain)
        line2.setStyleSheet("color: #525252;")
        left_layout.addWidget(line2)

        self.export_btn = QPushButton("Export JSON")
        self.export_btn.setStyleSheet(button_style)
        self.export_btn.clicked.connect(self.export_json)
        left_layout.addWidget(self.export_btn)

        self.load_btn = QPushButton("Load JSON")
        self.load_btn.setStyleSheet(button_style)
        self.load_btn.clicked.connect(self.load_json)
        left_layout.addWidget(self.load_btn)

        self.validate_btn = QPushButton("VALIDATE CMP")
        self.validate_btn.setStyleSheet(validate_button_style)
        self.validate_btn.clicked.connect(self.validate)
        left_layout.addWidget(self.validate_btn)

        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Plain)
        line3.setStyleSheet("color: #525252;")
        left_layout.addWidget(line3)

        self.help_btn = QPushButton("Need Help?")
        self.help_btn.setStyleSheet(button_style)
        self.help_btn.clicked.connect(self.need_help)
        left_layout.addWidget(self.help_btn)

        left_layout.addStretch()

        # -------------------------------------------------------------------
        # SPLITTER: LEFT PANEL | MAIN SCENE
        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.view)
        splitter.setSizes([300, 800])
        splitter.setHandleWidth(6)

        self.setCentralWidget(splitter)

        # MODE INDICATOR LABEL
        self.mode_indicator = QLabel(self.view)
        self.mode_indicator.move(20, 20)
        self.mode_indicator.setObjectName("modeLabel")
        self.mode_indicator.hide()

        # TODO: fix this issue when unfocusing on a text box
        #self.setFocusPolicy(Qt.StrongFocus)
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def update_mode_indicator(self):
        txt = ""
        if self.delete_mode:
            txt += "DELETE MODE"
            self.setStyleSheet(delete_mode_label_style)
        if self.arrow_mode:
            txt += (" | " if txt else "") + "ARROW MODE"
            self.setStyleSheet(arrow_mode_label_style)

        if txt:
            self.mode_indicator.setText(txt)
            self.mode_indicator.adjustSize()
            self.mode_indicator.show()
        else:
            self.mode_indicator.hide()
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def validate(self):
        warnings = []

        op_names = [op_node.name_text.toPlainText() for op_node in self.op_nodes]
        ids = [node.id_text.toPlainText() for node in self.op_nodes]

        # CHECK FOR START NODE
        if "START" not in op_names:
            warnings.append("△ PROBLEM: No operation named 'START' exists.")

        # CHECK FOR END NODE
        if "END" not in ids:
            warnings.append("△ PROBLEM: No operation with id 'END' exists.")

        # Check that all prob nodes have arrows with a total outgoing flow of 100%
        for prob_node in self.prob_nodes:
            total_flow = 0.0
            for arrow in prob_node.outgoing_arrows:
                flow_str = arrow.text_item.toPlainText().strip()

                # Validate format: must be "X%" or "XX%"
                if not re.fullmatch(r'\d{1,2}%', flow_str):
                    warnings.append(
                        "△ PROBLEM: One of your arrows has an invalid probability format. Must be a percentage in the format XX%."
                    )

                # Sum numeric values
                flow_value = 0.0
                try:
                    flow_value = float(flow_str.replace('%',''))
                except ValueError:
                    pass  # already reported format issue
                total_flow += flow_value

            # Check total outgoing flow
            if abs(total_flow - 100.0) > 0.01:
                warnings.append(
                    "△ PROBLEM: One of your Probability Nodes has an outgoing probability flow different than 100%."
                )

        # Check conditional nodes
        for cond_node in self.cond_nodes:
            outgoing = cond_node.outgoing_arrows
            if len(outgoing) != 2:
                warnings.append(
                    "△ PROBLEM: One of your Conditional Nodes does not have exactly 2 outgoing arrows."
                )
                continue  # skip further checks if count is wrong

            texts = [arrow.flow_text.toPlainText().strip().upper() for arrow in outgoing]
            if "YES" not in texts or "NO" not in texts:
                warnings.append(
                    "△ PROBLEM: One of your Conditional Nodes must have one arrow labeled 'YES' and one labeled 'NO'."
                )

        # Join the warnings
        warnings_string = "<br>".join(warnings)

        dlg = ValidateDialog(warnings_string, self)
        #dlg.exec_() # blocks interactions with main window
        dlg.show()
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def add_operation_node(self):
        dlg = ChooseOperationDialog(self._operations, self)
        if dlg.exec_() != QDialog.Accepted:
            return
        operation = dlg.selected

        node = OpNode(100 + len(self.op_nodes)*50, 100)
        node.setZValue(1)
        node.operation_data = operation
        node.name_text.setPlainText(operation["name"])

        self.scene.addItem(node)
        self.op_nodes.append(node)
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def add_probability_node(self):
        node = ProbNode(100 + len(self.op_nodes)*50, 100)
        node.setZValue(1)

        self.scene.addItem(node)
        self.prob_nodes.append(node)
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def add_conditional_node(self):
        dlg = ChooseConditionDialog(self._conditions, self)
        if dlg.exec_() != QDialog.Accepted:
            return
        condition = dlg.composed_condition

        node = CondNode(100 + len(self.op_nodes)*50, 100, condition)
        node.setZValue(1)

        self.scene.addItem(node)
        self.cond_nodes.append(node)
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def toggle_arrow_mode(self):
        if not self.delete_mode:
            self.arrow_mode = self.add_arrow_btn.isChecked()
        else:
            self.add_arrow_btn.setChecked(False)
            self.update_mode_indicator()
        self.update_mode_indicator()
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def toggle_delete_mode(self):
        if not self.arrow_mode:
            self.delete_mode = self.delete_btn.isChecked()
        else:
            self.delete_btn.setChecked(False)
            self.update_mode_indicator()
        self.update_mode_indicator()
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def export_json(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Diagram JSON", "", "JSON Files (*.json)")
        if not filename:
            return

        data = []
        for node in self.op_nodes:
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
        for node in list(self.op_nodes):
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
        for node in list(self.op_nodes):
            self.scene.removeItem(node)
        self.op_nodes.clear()

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
            self.op_nodes.append(node)
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
    def need_help(self):
        return
    # ------------------------------------------------------------------------------------------------


# MAIN
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlowchartWindow()
    window.show()
    sys.exit(app.exec_())