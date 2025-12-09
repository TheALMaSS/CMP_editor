import sys, json, re, os
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QDialog, QTextEdit, QLabel, QVBoxLayout, QFrame, QSplitter, QDialogButtonBox
from flowchart_view import FlowchartView
from flowchart_scene import FlowchartScene
from prob_node import ProbNode
from choose_operation_dialog import ChooseOperationDialog
from op_node import OpNode
from prob_node import ProbNode
from cond_node import CondNode
from choose_condition_dialog import ChooseConditionDialog
from validate_dialog import ValidateDialog
from help_dialog import HelpDialog
from css_styles import button_style, validate_button_style, left_panel_style, delete_button_style, arrow_button_style, delete_mode_label_style, arrow_mode_label_style

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

OPERATIONS_FILE = resource_path("operations.json")
CONDITIONS_FILE = resource_path("conditions.json")

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
        self.scene.setBackgroundBrush(QBrush(QColor("#BCBCBC")))
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

        self.save_btn = QPushButton("Save CMP")
        self.save_btn.setStyleSheet(button_style)
        self.save_btn.clicked.connect(self.save_CMP)
        left_layout.addWidget(self.save_btn)

        self.load_btn = QPushButton("Load CMP")
        self.load_btn.setStyleSheet(button_style)
        self.load_btn.clicked.connect(self.load_CMP)
        left_layout.addWidget(self.load_btn)
    
        self.export_btn = QPushButton("Export to ALMaSS")
        self.export_btn.setStyleSheet(button_style)
        self.export_btn.clicked.connect(self.export_to_almass)
        left_layout.addWidget(self.export_btn)

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
    def validate(self, return_warnings=False):
        warnings = []

        op_names = [op_node.name_text.toPlainText() for op_node in self.op_nodes]
        print(op_names)
        ids = [node.id_text.toPlainText() for node in (self.op_nodes + self.prob_nodes + self.cond_nodes)]

        # CHECK FOR START NODE
        if "START" not in op_names:
            warnings.append("⚠ <b>WARNING:</b> no operation named 'START' exists.")

        # CHECK FOR END NODE
        if "END" not in op_names:
            warnings.append("⚠ <b>WARNING:</b> no operation named 'END' exists.")

        # Check no repetitions in ids
        if len(ids) != len(set(ids)):
            warnings.append("⚠ <b>WARNING:</b> two or more Nodes share the same ID.")

        # Check that all prob nodes have arrows with a total outgoing flow of 100%
        for prob_node in self.prob_nodes:
            total_flow = 0.0
            for arrow in prob_node.outgoing_arrows:
                flow_str = arrow.text_item.toPlainText().strip()

                # Validate format: must be "X%" or "XX%"
                if not re.fullmatch(r'\d{1,2}%', flow_str):
                    warnings.append(
                        "⚠ <b>WARNING:</b> one of your arrows has an invalid probability format. Must be a percentage in the format XX%."
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
                    "⚠ <b>WARNING:</b> Node '" + str(prob_node.id_text.toPlainText()) + "' has an outgoing probability flow different than 100%."
                )

        # Check conditional nodes
        for cond_node in self.cond_nodes:
            outgoing = cond_node.outgoing_arrows
            if len(outgoing) != 2:
                warnings.append(
                    "⚠ <b>WARNING:</b> Node '" + str(prob_node.id_text.toPlainText()) + "' does not have exactly 2 outgoing arrows."
                )
                break

            texts = [arrow.flow_text.toPlainText().strip().upper() for arrow in outgoing]
            if "YES" not in texts or "NO" not in texts:
                warnings.append(
                    "⚠ <b>WARNING:</b> Node '" + str(cond_node.id_text.toPlainText()) + "' must have one arrow labeled 'YES' and one labeled 'NO'."
                )

        # Check that operation nodes have exactly 1 outgoing arrow if not end
        for op_node in self.op_nodes:
            outgoing = op_node.outgoing_arrows
            if len(outgoing) != 1 and op_node.id_text.toPlainText() != "END":
                warnings.append(
                    "⚠ <b>WARNING:</b> Node '" + str(op_node.id_text.toPlainText()) + "' must have exactly 1 outgoing arrow."
                )
                break

            texts = [arrow.flow_text.toPlainText().strip().upper() for arrow in outgoing]
            if "YES" not in texts or "NO" not in texts:
                warnings.append(
                    "⚠ <b>WARNING:</b> Node '" + str(cond_node.id_text.toPlainText()) + "' must have one arrow labeled 'YES' and one labeled 'NO'."
                )

        # Check operation nodes' dates format
        for op_node in self.op_nodes:
            dates_str = op_node.dates_text.toPlainText().strip()
            # Regex: two digits / two digits, space-dash-space, two digits / two digits
            if not re.fullmatch(r'\d{2}/\d{2} - \d{2}/\d{2}', dates_str) and op_node.name_text.toPlainText() != "START" and op_node.name_text.toPlainText() != "END":
                warnings.append(
                    "⚠ <b>WARNING:</b> Node '" + str(op_node.id_text.toPlainText()) + "' has an invalid date format. Must be 'xx/xx - xx/xx'."
                )
                break

        # Join the warnings
        warnings_string = "<br>".join(warnings)

        # TODO: Add previous logic to helper funcs
        if return_warnings:
            return warnings

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

        node = OpNode('<span style="font-size:9pt;">' + str(operation["name"]) + '</span>')
        node.setZValue(1)

        self.scene.addItem(node)
        self.op_nodes.append(node)
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def add_probability_node(self):
        node = ProbNode('<span style="font-size:9pt; font-weight:bold;">Probability<br>Node</span>')
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

        node = CondNode('<span style="font-size:9pt; font-weight:bold;">' + str(condition) + '</span>')
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
    def save_CMP(self):
        data = []

        all_nodes = self.op_nodes + self.cond_nodes + self.prob_nodes
        ids = [node.id_text.toPlainText() for node in all_nodes]
        # Check no repetitions in ids
        if len(ids) != len(set(ids)):
            dlg = QDialog(self, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            dlg.setWindowTitle("WARNING")
            dlg.resize(400, 250)

            text = QTextEdit()
            text.setReadOnly(True)
            text.setHtml('<span style="color: #B22222; font-weight: bold; font-size: 12pt;">Some of your nodes share the same ID. If you proceed with saving, your data will be corrupted.</span>')

            layout = QVBoxLayout()
            layout.addWidget(text)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(dlg.accept)
            layout.addWidget(buttons)

            dlg.setLayout(layout)
            dlg.exec_()

        for node in all_nodes:
            node_data = {
                "type": node.__class__.__name__,
                "x": node.scenePos().x(),
                "y": node.scenePos().y(),
                "width": getattr(node, "width", 120),
                "height": getattr(node, "height", 60),
                "id": node.id_text.toPlainText(),
                "name": node.name_text.toPlainText(),
                "outgoing": []
            }

            if isinstance(node, OpNode):
                node_data.update({
                    "dates": node.dates_text.toPlainText()
                })

            for arrow in node.outgoing_arrows:
                if arrow.end_node:
                    if hasattr(arrow.end_node, "id_text"):
                        destination_id = arrow.end_node.id_text.toPlainText()
                    else:
                        destination_id = "no_id"

                branching_condition = arrow.text_item.toPlainText() if arrow.text_item else ""

                arrow_data = {
                    "destination_type": arrow.end_node.__class__.__name__ if arrow.end_node else "",
                    "destination_id": destination_id,
                    "branching_condition": branching_condition,
                    "bend_points": [[bp.pos().x(), bp.pos().y()] for bp in arrow.bend_points]
                }

                node_data["outgoing"].append(arrow_data)

            data.append(node_data)

        filename, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json)")
        if filename:
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def load_CMP(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open JSON", "", "JSON Files (*.json)")
        if not filename:
            return

        # Clear existing nodes and arrows
        for node_list in [self.op_nodes, self.cond_nodes, self.prob_nodes]:
            for node in list(node_list):
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
            for node in list(node_list):
                self.scene.removeItem(node)
            node_list.clear()

        with open(filename, "r") as f:
            data = json.load(f)

        node_map = {}

        for node_data in data:
            node_type = node_data.get("type", "OpNode")
            if node_type == "OpNode":
                node = OpNode('<span style="font-size:9pt;">' + str(node_data["name"]) + '</span>')
                self.op_nodes.append(node)
            elif node_type == "ProbNode":
                node = ProbNode('<span style="font-size:9pt; font-weight:bold;">Probability<br>Node</span>')
                self.prob_nodes.append(node)
            elif node_type == "CondNode":
                node = CondNode('<span style="font-size:9pt; font-weight:bold;">' + str(node_data["name"]) + '</span>')
                self.cond_nodes.append(node)

            node.setPos(node_data["x"], node_data["y"])
            node.adjust_size()  # recompute dimensions

            node.id_text.setPlainText(node_data.get("id", "ID"))
            if hasattr(node, "dates_text") and "dates" in node_data:
                node.dates_text.setPlainText(node_data["dates"])

            node.setZValue(1)
            node.update_positions()
            self.scene.addItem(node)

            # Use id as key for node map for arrows
            node_key = node_data.get("id", node_data.get("name", f"{id(node)}"))
            node_map[node_key] = node

        # Recreate arrows
        for node_data in data:
            source_key = node_data.get("id", node_data.get("name"))
            source_node = node_map.get(source_key)
            if not source_node:
                continue

            for arrow_data in node_data.get("outgoing", []):
                dest_node = node_map.get(arrow_data.get("destination_id"))
                if dest_node:
                    arrow = source_node.add_arrow_to(dest_node)
                    if arrow_data.get("branching_condition", "") != "":
                        arrow.text_item.setVisible(True)
                    if arrow.text_item:
                        arrow.text_item.setPlainText(arrow_data.get("branching_condition", ""))
                        self.scene.addItem(arrow.text_item)
                    self.scene.addItem(arrow)

                    for bp_coords in arrow_data.get("bend_points", []):
                        arrow.add_bend_point(QPointF(bp_coords[0], bp_coords[1]))
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def need_help(self):
        dlg = HelpDialog(self)
        dlg.exec_()
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    def export_to_almass(self):
        return
    # ------------------------------------------------------------------------------------------------


# MAIN
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlowchartWindow()
    window.show()
    sys.exit(app.exec_())