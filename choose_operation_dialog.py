from PyQt5.QtWidgets import QWidget, QPushButton, QDialog, QListWidget, QTextEdit, QLabel, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QLineEdit
from PyQt5.QtCore import Qt

help_text_choose_operation = "Select a crop operation on the left to see its description.\n\n" \
"When you press OK, the selected operation will be assigned to the new node.\n\n" \
"--------------------------------\n\n" \
"If no existing farm operation matches your needs, please contact: elena.fini@agro.au.dk"
#"If no existing farm operation matches your needs, you may follow these steps to create a new one:\n\n" \
#"1) Open the file operations.json and add your new farm operation following the format of the other entries." \
#"You will have to specify a C++ function name for it, which will have to match the function you generate in step 2.\n\n" \
#"2) Open the ALMaSS project in a code editor and find the file FarmFuncs.cpp (+ its associated header FarmFuncs.h)." \
#"You may use an existing function with a behaviour similar to what you want to obtain, copy-paste it, rename it, and modify its behaviour to match exactly what you want to achieve.\n\n" \
#"Creating a new farm operation requires some knowledge of the existing ALMaSS codebase, and also of C++ coding. If you find any issue, please contact: elena.fini@agro.au.dk.\n\n" \
#"For the purpose of flowchart design, if cannot complete step 2 (which requires programming knowledge), you may still perform step 1 locally -" \
#"just keep in mind that, in order for your farm operation to be correctly simulated, someone else will have to complete step 2, eventually."


class ChooseOperationDialog(QDialog):
    def __init__(self, operations, parent=None):
        super().__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle("Select Crop Operation")
        self.resize(650, 400)
        self.operations = operations
        self.filtered_operations = operations
        self.selected = None

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search operations...")
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.search_btn)

        self.list_widget = QListWidget()
        self.update_list(self.operations)

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
        left_layout.addLayout(search_layout)
        left_layout.addWidget(self.list_widget)

        right_layout = QVBoxLayout()
        right_layout.addWidget(right_label)
        right_layout.addWidget(self.desc)

        left_container = QWidget()
        left_container.setLayout(left_layout)
        left_container.setMinimumWidth(350)

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

    # searches both in name and description
    def perform_search(self):
        text = self.search_field.text().lower()
        if not text:
            self.filtered_operations = self.operations
        else:
            self.filtered_operations = [
                op for op in self.operations
                if text in op["name"].lower() or text in op.get("description", "").lower()
            ]
        self.update_list(self.filtered_operations)
        if self.list_widget.count():
            self.list_widget.setCurrentRow(0)

    def update_list(self, ops):
        self.list_widget.clear()
        for op in ops:
            self.list_widget.addItem(op["name"])

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
        if row < 0 or row >= len(self.filtered_operations):
            self.desc.setPlainText("")
            return
        self.desc.setPlainText(self.filtered_operations[row].get("description", ""))

    def accept(self):
        row = self.list_widget.currentRow()
        if row < 0:
            super().reject()
            return
        self.selected = self.filtered_operations[row]
        super().accept()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.search_field.hasFocus():
                self.perform_search()
                return
        super().keyPressEvent(event)