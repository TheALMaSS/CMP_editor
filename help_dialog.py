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
CMP Editor lets you design your Crop Management Plan, using a decision tree structure. From here, you can export your CMP as a JSON file compatible with ALMaSS.<br><br>

<b>The Nodes</b><br>
All nodes must have a univocal ID of your choosing.<br>
• Operation Nodes: a standard Farm Operation, with a date range indicating the time of year in which the operation can be performed. You must select the farm operation from the ones available inside ALMaSS.<br>
• Probability Nodes: for probability-based branching.<br>
• Conditional Nodes: for condition-based branching. Conditional branching can be based on properties of the field or of the farm, or on previous operation having been carried out on the field.<br><br>

<b>Mandatory Operations</b><br>
A mandatory operation will <b>always</b> be performed, even if its time window has elapsed. The farmer will "push through" and perform the operation anyway.<br>
When creating a new operation node, check the "mandatory" flag to create a mandatory operation (it is checked by default). It will be marked by a golden star in the UI.<br>
If an operation is not mandatory, it means that it may not be executed if the right circumstances do not present themselves -- but this will not prevent it from scheduling all subsequent operations connected by arrows.<br><br>

<b>Connecting Nodes</b><br>
• Click "Add Arrow" to enter arrow mode.<br>
• Click on a first node, then on a second one to create a flow of operations.<br>
• Multischeduling (having multiple outgoing arrows for an operation node) is allowed.When the parent node is executed, it will schedule all of its children nodes.<br>
• For probability nodes, assign each outgoing arrow a probability. The total outgoing flow must of course be 100%.<br>
• For conditional nodes, set the labels of its outgoing arrows to YES and NO.<br><br>

<b>Deleting Elements</b><br>
• Enable Delete mode and click on any arrow and node to delete them. Deleting a node causes deletion of all its incoming and outgoing arrows.<br><br>

<b>Validation</b><br>
• Press "VALIDATE CMP" to check for errors in the CMP.<br><br>

<b>Saving/Loading</b><br>
• "Save CMP" saves your CMP to a .cmp file, which you can reopen later with "Load CMP".<br>
• "Export to ALMaSS" will generate a JSON file that can be parsed by ALMaSS into a Generic Crop class. <br>Remember to validate your CMP before exporting!<br><br>

<b>User Controls</b><br>
• Drag nodes to reposition them.<br>
• Left-click on arrows to create bending points. Right-click on a bending point to delete it.<br>
• Zoom in/out by pressing SHIFT and scrolling with the mouse.<br>
• Navigate around the canvas by pressing the mouse wheel.<br>
• Use CTRL+C and CTRL+V to copy-paste selected nodes.<br>
• The button "scroll back to content" will reposition your view on the center of mass of your flowchart.<br><br>

<b>Issues?</b><br>
If you have issues with the software, contact: elena.fini@agro.au.dk
</span>

"""

        text_box.setHtml(help_text)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)