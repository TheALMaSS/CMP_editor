from PyQt5.QtWidgets import QDialog, QListWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QDialog, QListWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QDialogButtonBox

help_text_choose_condition = """
Select a condition for branching by navigating the three columns:

1. First Column: choose the main category.
2. Second Column: pick a property associated to the main category.
3. Third Column: select the value of the property that will define your branching.

Example: FARM -> SOIL -> CLAY will generate the branching condition:
FARM->SOIL is CLAY?
From which two branches (YES and NO) can come out.

Remember that a branching node with a conditional value must always have exactly 2 outgoing arrows: one for YES (when its condition is true) and one for NO (when its condition is false).

Use the OK button to confirm your selection or Cancel to exit without selecting.
"""

class ChooseConditionDialog(QDialog):
    def __init__(self, conditions, parent=None):
        super().__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Select Condition For Branching")
        self.resize(600, 300)

        self.selected = []  # final selected path
        self.conditions = conditions  # store the passed-in conditions
        self.composed_condition = None  # final string like "ITEM1->ITEM2 is ITEM3?"

        layout = QHBoxLayout(self)
        self.list1 = QListWidget()
        self.list2 = QListWidget()
        self.list3 = QListWidget()
        layout.addWidget(self.list1)
        layout.addWidget(self.list2)
        layout.addWidget(self.list3)

        self.list1.addItems(sorted(conditions.keys()))

        self.list1.currentItemChanged.connect(self.on_list1_changed)
        self.list2.currentItemChanged.connect(self.on_list2_changed)
        self.list3.currentItemChanged.connect(self.on_list3_changed)

        btn_layout = QVBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setEnabled(False)  # disabled until all 3 selected
        cancel_btn = QPushButton("Cancel")
        help_btn = QPushButton("?")
        self.ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        help_btn.clicked.connect(self.open_help)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(help_btn)
        layout.addLayout(btn_layout)

    def open_help(self):
        dlg = QDialog(self, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        dlg.setWindowTitle("Help - select a condition")
        dlg.resize(400, 400)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(help_text_choose_condition)

        layout = QVBoxLayout()
        layout.addWidget(text)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dlg.accept)
        layout.addWidget(buttons)

        dlg.setLayout(layout)
        dlg.exec_()

    def on_list1_changed(self, current, previous):
        self.list2.clear()
        self.list3.clear()
        self.selected = []
        self.ok_btn.setEnabled(False)
        if current is None:
            return
        self.selected.append(current.text())
        second_options = self.conditions.get(current.text(), {})
        self.list2.addItems(sorted(second_options.keys()))

    def on_list2_changed(self, current, previous):
        self.list3.clear()
        if current is None:
            self.selected = self.selected[:1]
            self.ok_btn.setEnabled(False)
            return
        if len(self.selected) >= 2:
            self.selected[1] = current.text()
        else:
            self.selected.append(current.text())
        first_key = self.selected[0]
        third_options = self.conditions.get(first_key, {}).get(current.text(), [])
        self.list3.addItems(sorted(third_options))
        self.ok_btn.setEnabled(False)

    def on_list3_changed(self, current, previous):
        if current is None:
            self.selected = self.selected[:2]
            self.ok_btn.setEnabled(False)
            return
        if len(self.selected) >= 3:
            self.selected[2] = current.text()
        else:
            self.selected.append(current.text())
        # Enable OK only if all three selections are made
        self.ok_btn.setEnabled(len(self.selected) == 3)

    def accept(self):
        if len(self.selected) != 3:
            return  # safety check
        # Compose string like "ITEM1->ITEM2 is ITEM3?"
        self.composed_condition = f"{self.selected[0]}->{self.selected[1]}<br>is {self.selected[2]}?"
        super().accept()