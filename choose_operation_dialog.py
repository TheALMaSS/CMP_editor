from PyQt5.QtWidgets import QWidget, QPushButton, QDialog, QListWidget, QTextEdit, QLabel, QHBoxLayout, QVBoxLayout, QDialogButtonBox
from PyQt5.QtCore import Qt

help_text_choose_operation = "Select a crop operation on the left to see its description.\n\n" \
"When you press OK, the selected operation will be assigned to the new node.\n\n" \
"If no operation matches your requirements, refer to the 'how to create a new farm operation' manual in this folder."

class ChooseOperationDialog(QDialog):
    def __init__(self, operations, parent=None):
        super().__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle("Select Crop Operation")
        self.resize(700, 400)
        self.operations = operations
        self.selected = None

        self.list_widget = QListWidget()
        for a in operations:
            self.list_widget.addItem(a["name"])

        self.desc = QTextEdit()
        self.desc.setReadOnly(True)

        left_label = QLabel("Operations")
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

        left_container = QWidget()
        left_container.setLayout(left_layout)
        left_container.setMinimumWidth(300)

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
        dlg.setWindowTitle("Help - select a crop operation")
        dlg.resize(400, 400)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(help_text_choose_operation)

        layout = QVBoxLayout()
        layout.addWidget(text)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dlg.accept)
        layout.addWidget(buttons)

        dlg.setLayout(layout)
        dlg.exec_()

    def on_row_changed(self, row):
        if row < 0 or row >= len(self.operations):
            self.desc.setPlainText("")
            return
        self.desc.setPlainText(self.operations[row].get("description", ""))

    def accept(self):
        row = self.list_widget.currentRow()
        if row < 0:
            super().reject()
            return
        self.selected = self.operations[row]
        super().accept()