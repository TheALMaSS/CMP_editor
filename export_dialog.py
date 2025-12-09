from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt

class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Export to ALMaSS")
        self.resize(400, 170)
        self.crop_name = None

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Please enter the name of the crop model.\nFormat required: country code + name of the crop.\nExample: DK_WinterRape"))

        self.input = QLineEdit()
        self.input.setStyleSheet("font-size: 10pt;")
        layout.addWidget(self.input)

        btn = QPushButton("Export")
        btn.clicked.connect(self.on_export)
        layout.addWidget(btn)

        self.setLayout(layout)

    def on_export(self):
        self.crop_name = self.input.text()
        self.accept()