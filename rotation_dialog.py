"""Rotation timing: the operation windows ALMaSS needs to fit a crop into its rotation.

Every hardcoded crop declares a small table before handing control to the rotation: the last day
harvest may happen, start/end windows for the operations that follow it, whether the crop is a
spring crop, and which node runs in the crop's first year. ALMaSS publishes the table on the
field, pulls the windows in if the following crop starts sooner, and refuses a start the calendar
cannot accommodate.

The tables for the existing crops are transcribed in flexdates_reference.json, so a crop that
already exists in ALMaSS can load its own without anybody retyping dates.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox,
                             QPushButton, QDialogButtonBox, QSpinBox, QWidget, QComboBox,
                             QScrollArea, QFrame)
from PyQt5.QtCore import Qt

MAX_OPERATION_ROWS = 4   # the largest table any existing crop uses


class RotationDialog(QDialog):
    def __init__(self, crop_name, current, reference, node_ids, parent=None):
        super().__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Rotation timing")
        self.resize(520, 520)
        self.reference = reference or {}
        self.result_data = None

        outer = QVBoxLayout(self)

        blurb = QLabel(
            "These dates let ALMaSS fit this crop into its rotation: when the harvest must be "
            "finished by, and the windows for any operations after it. Leave a start date empty "
            "for an operation that can be moved as early as needed.\n\n"
            "Without these, the crop still runs, but it takes no part in the rotation's timing."
        )
        blurb.setWordWrap(True)
        outer.addWidget(blurb)

        if crop_name in self.reference:
            row = QHBoxLayout()
            btn = QPushButton(f"Load the dates ALMaSS uses for {crop_name}")
            btn.clicked.connect(self.load_reference)
            row.addWidget(btn)
            outer.addLayout(row)

        form = QVBoxLayout()

        self.spring_check = QCheckBox("Spring crop")
        self.spring_check.setToolTip(
            "Spring crops are allowed a year's grace on a late start, because their sowing is "
            "months after the previous crop finishes."
        )
        form.addWidget(self.spring_check)

        hrow = QHBoxLayout()
        hrow.addWidget(QLabel("Harvest finished by (dd/MM):"))
        self.harvest_edit = QLineEdit()
        self.harvest_edit.setPlaceholderText("31/08")
        hrow.addWidget(self.harvest_edit)
        form.addLayout(hrow)

        lrow = QHBoxLayout()
        lrow.addWidget(QLabel("Last day of the crop (dd/MM):"))
        self.last_edit = QLineEdit()
        self.last_edit.setPlaceholderText("31/08")
        lrow.addWidget(self.last_edit)
        form.addLayout(lrow)

        frow = QHBoxLayout()
        frow.addWidget(QLabel("First-year node:"))
        self.first_year_combo = QComboBox()
        self.first_year_combo.addItem("")
        for nid in node_ids:
            self.first_year_combo.addItem(nid)
        self.first_year_combo.setToolTip(
            "Which node to run in the crop's very first simulated year, when there is no previous "
            "crop to hand over from. Usually the first real operation."
        )
        frow.addWidget(self.first_year_combo)
        form.addLayout(frow)

        outer.addLayout(form)

        outer.addWidget(QLabel("<b>Operations after the harvest</b>"))
        self.rows = []
        holder = QWidget()
        hl = QVBoxLayout(holder)
        for i in range(MAX_OPERATION_ROWS):
            r = QHBoxLayout()
            r.addWidget(QLabel(f"{i + 1}."))
            start = QLineEdit(); start.setPlaceholderText("start dd/MM (optional)")
            end = QLineEdit();   end.setPlaceholderText("end dd/MM")
            r.addWidget(start); r.addWidget(end)
            hl.addLayout(r)
            self.rows.append((start, end))
        area = QScrollArea(); area.setWidget(holder); area.setWidgetResizable(True)
        area.setFrameShape(QFrame.NoFrame)
        outer.addWidget(area)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

        self.crop_name = crop_name
        if current:
            self.populate(current)

    def load_reference(self):
        self.populate(self.reference.get(self.crop_name, {}))

    def populate(self, d):
        self.spring_check.setChecked(bool(d.get("is_spring")))
        self.harvest_edit.setText(d.get("harvest_end") or "")
        self.last_edit.setText(d.get("last_date") or "")
        idx = self.first_year_combo.findText(d.get("first_year_op") or "")
        if idx >= 0:
            self.first_year_combo.setCurrentIndex(idx)
        for i, (s, e) in enumerate(self.rows):
            fd = d.get("flexdates") or []
            if i < len(fd):
                s.setText(fd[i].get("start") or "")
                e.setText(fd[i].get("end") or "")
            else:
                s.clear(); e.clear()

    def accept(self):
        flexdates = []
        for s, e in self.rows:
            st, en = s.text().strip(), e.text().strip()
            # A row counts only once it has an end date; a start alone has nothing to bound.
            if en:
                flexdates.append({"start": st or None, "end": en})
        self.result_data = {
            "is_spring": self.spring_check.isChecked(),
            "harvest_end": self.harvest_edit.text().strip() or None,
            "last_date": self.last_edit.text().strip() or None,
            "first_year_op": self.first_year_combo.currentText() or None,
            "flexdates": flexdates,
        }
        super().accept()
