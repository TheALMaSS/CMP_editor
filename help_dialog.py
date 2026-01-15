from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtCore import Qt

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle("Help")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        text_box = QTextEdit()
        text_box.setReadOnly(True)
        layout.addWidget(text_box)

        help_text = """
<span style="font-size:10pt;">
<b>CMP Editor - Quick Guide</b><br>
CMP Editor lets you design your Crop Management Plan, using a decision tree structure. From here, you can export your CMP as a C++ class compatible with ALMaSS.<br><br>

<b>The Nodes</b><br>
All nodes must have a univocal ID of your choosing.<br>
• Operation Nodes: a standard Farm Operation, with a date range indicating the time of year in which the operation can be performed. You must select the farm operation from the ones available inside ALMaSS.<br>
• Probability Nodes: for probability-based branching.<br>
• Conditional Nodes: for condition-based branching. You must select the branching conditions from the field and farm properties inside ALMaSS.<br><br>

<b>Connecting Nodes</b><br>
• Click "Add Arrow" to enter arrow mode.<br>
• Click a first node, then a second one to create a sequential flow of operations.<br>
• For probability nodes, assign each outgoing arrow a probability. The total outgoing flow must of course be 100%.<br>
• For conditional nodes, set the labels of its outgoing arrows to YES and NO.<br><br>

<b>Deleting Elements</b><br>
• Enable Delete mode and click on any arrow and node to delete them. Deleting a node causes deletion of all its incoming and outgoing arrows.<br><br>

<b>Validation</b><br>
• Press "VALIDATE CMP" to check for errors in the CMP.<br><br>

<b>Saving/Loading</b><br>
• "Save CMP" saves your CMP to a JSON file, which you can reopen later with "Load CMP".<br>
• "Export to ALMaSS" will build an ALMaSS compatible C++ class + header file, which you can then plug into the software.<br>Remember to validate your CMP before exporting!<br><br>

<b>User Controls</b><br>
• Drag nodes to reposition them.<br>
• Left-click on arrows to create bending points. Right-click on a bending point to delete it.<br>
• Zoom in/out by pressing SHIFT and scrolling with the mouse.<br>
• Navigate around the canvas by pressing the mouse wheel.<br>
• Use CTRL+C and CTRL+V to copy-paste selected nodes.<br><br>

<b>Issues?</b><br>
If you have issues with the software, contact: elena.fini@agro.au.dk
</span>

"""

        text_box.setHtml(help_text)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)