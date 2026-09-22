from PyQt5.QtWidgets import QDialog, QListWidget, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QDialog, QListWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QComboBox

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
        self.resize(700, 300)

        self.selected = []  # final selected path
        self.conditions = conditions  # store the passed-in conditions
        self.composed_condition = None  # final string like "ITEM1->ITEM2 is ITEM3?"
        self.coded_condition = None # final string like "m_farm->gettype() == 5"

        layout = QHBoxLayout(self)
        self.list1 = QListWidget()
        self.list2 = QListWidget()
        self.list3 = QListWidget()
        layout.addWidget(self.list1)
        layout.addWidget(self.list2)
        layout.addWidget(self.list3)

        self.history_widget = QWidget()
        self.history_widget.setFixedWidth(200)
        history_layout = QVBoxLayout(self.history_widget)
        history_layout.setContentsMargins(0, 0, 0, 0)

        self.history_instructions = QLabel(
            "Enter the ID of the operation node for branching.\n"
            "YES branch: operation completed.\n"
            "NO branch: operation not completed."
        )
        self.history_instructions.setWordWrap(True)
        self.text3 = QTextEdit()
        self.text3.setReadOnly(False)
        self.text3.setFixedHeight(50)

        self.history_instructions.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.text3.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Comparison selector, shown only for conditions that compare numbers (vegetation height).
        # HISTORY and DATE keep their fixed meanings, so it stays hidden for those.
        self.op_combo = QComboBox()
        self.op_combo.addItems([">=", ">", "<=", "<", "=="])
        self.op_combo.hide()

        history_layout.addWidget(self.history_instructions)
        history_layout.addWidget(self.op_combo)
        history_layout.addWidget(self.text3)
        self.layout().addWidget(self.history_widget)
        self.history_widget.hide()

        self.list1.addItems(sorted(conditions.keys()))

        self.list1.currentItemChanged.connect(self.on_list1_changed)
        self.list2.currentItemChanged.connect(self.on_list2_changed)
        self.list3.currentItemChanged.connect(self.on_list3_changed)
        self.text3.textChanged.connect(self.on_text3_changed)

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
        second_options = self.conditions[current.text()]["sublayers"].keys()
        self.list2.addItems(sorted(second_options))

    def on_list2_changed(self, current, previous):

        if current is None:
            self.history_widget.hide()
            self.list3.show()
            self.list3.clear()
            self.selected = self.selected[:1]
            self.ok_btn.setEnabled(False)
            return

        elif current.text() in ("HISTORY", "DATE", "VEGETATION HEIGHT", "CROP AGE"):
            self.list3.hide()
            self.history_widget.show()
            self.op_combo.setVisible(current.text() in ("VEGETATION HEIGHT", "CROP AGE"))

            if current.text() == "CROP AGE":
                self.history_instructions.setText(
                    "Choose a comparison and enter a number of years.\n"
                    "0 is the establishment year; 1 is the first year after that.\n"
                    "Only meaningful for a permanent crop, which must also set its cycle length."
                )
            elif current.text() == "VEGETATION HEIGHT":
                self.history_instructions.setText(
                    "Choose a comparison and enter a vegetation height in cm.\n"
                    "YES branch: the field's height satisfies the comparison.\n"
                    "NO branch: it does not."
                )
            elif current.text() == "HISTORY":
                self.history_instructions.setText(
                    "Enter the ID of the operation node for branching.\n"
                    "YES branch: operation completed.\n"
                    "NO branch: operation not completed."
                )
            else:
                self.history_instructions.setText(
                    "Enter the day of the year (1-365) for branching.\n"
                    "YES branch: today's day <= entered day.\n"
                    "NO branch: today's day > entered day."
                )

        else:
            # normal third column behavior
            self.history_widget.hide()
            first_key = self.selected[0]
            third_options = list(self.conditions[first_key]["sublayers"][current.text()].keys())[1:]
            self.list3.show()
            self.list3.clear()
            self.list3.addItems(third_options)

        if len(self.selected) >= 2:
            self.selected[1] = current.text()
        else:
            self.selected.append(current.text())
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

    def on_text3_changed(self):
        self.ok_btn.setEnabled(True)

    def lookup_code(self, layer, sublayer, label):
        """Translate a display label into the machine value ALMaSS compares against.

        conditions.json stores each option as "<label>": "<code>" under the sublayer, alongside a
        leading "func" entry naming the C++ accessor. Falls back to the label itself if the entry
        is missing, so an unmapped option is at least visible rather than silently blank.
        """
        try:
            return self.conditions[layer]["sublayers"][sublayer][label]
        except (KeyError, TypeError):
            return label

    def accept(self):
        if self.selected[1] in ("HISTORY", "DATE", "VEGETATION HEIGHT", "CROP AGE"):
            text = self.text3.toPlainText()
            if text:
                if len(self.selected) < 3:
                    self.selected.append(text)
        if len(self.selected) != 3:
            return  # safety check
        if self.selected[1] == "CROP AGE":
            op = self.op_combo.currentText()
            self.composed_condition = f"Is the crop\n{op} {self.selected[2]} years old?"
            self.coded_condition = "null"
            self.cond_value = self.selected[2]
            self.cond_op = op

        elif self.selected[1] == "VEGETATION HEIGHT":
            op = self.op_combo.currentText()
            self.composed_condition = (
                f"Is vegetation height\n{op} {self.selected[2]} cm?"
            )
            self.coded_condition = "null"
            self.cond_value = self.selected[2]
            self.cond_op = op

        elif self.selected[1] == "HISTORY":
            self.composed_condition = (
                f"Has operation {self.selected[2]}\nbeen performed?"
            )
            self.coded_condition = "null"
            self.cond_value = self.selected[2]

        elif self.selected[1] == "DATE":
            self.composed_condition = (
                f"Is today's DOY\n ≤ {self.selected[2]}?"
            )
            self.coded_condition = "null"
            self.cond_value = self.selected[2]
        else:
            # ALMaSS compares cond_value against the NUMERIC code returned by the accessor
            # (e.g. std::to_string(GetSoilType()) == cond_value), so the stored value must be the
            # code from conditions.json -- not the human-readable label shown in the tree.
            # Writing the label here is why 49 of 57 existing field_soil nodes carry "Clay" and can
            # never match. The label is kept for composed_condition (what the author sees).
            self.composed_condition = f"Is {self.selected[1]}:\n{self.selected[2]}?"
            self.coded_condition = "null"
            self.cond_value = self.lookup_code(self.selected[0], self.selected[1], self.selected[2])
        if self.selected[1] == "SOIL":
            self.cond_type = "field_soil"
        elif self.selected[1] == "SIZE":
            self.cond_type = "farm_size"
        elif self.selected[1] == "FARMING INTENSITY":
            self.cond_type = "farm_intensity"
        elif self.selected[1] == "FARM TYPE":
            # Boolean in ALMaSS (Farm::IsStockFarmer): YES = stock farm, NO = arable.
            # Some crops apply slurry on stock farms where an arable farm applies NPKS.
            self.cond_type = "farm_stock"
        elif self.selected[1] == "HISTORY":
            self.cond_type = "field_history"
        elif self.selected[1] == "DATE":
            self.cond_type = "calendar_date"
        elif self.selected[1] == "VEGETATION HEIGHT":
            self.cond_type = "field_vegheight"
        elif self.selected[1] == "CROP AGE":
            self.cond_type = "crop_age"

        super().accept()