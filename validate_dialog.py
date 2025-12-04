from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtCore import Qt

class ValidateDialog(QDialog):
    def __init__(self, warnings, parent=None):
        super().__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle("Validate CMP")
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        text_box = QTextEdit()
        text_box.setReadOnly(True)
        self.text_box = text_box  # store as instance variable so we can refresh later
        layout.addWidget(text_box)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_warnings)
        layout.addWidget(refresh_btn)

        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)

        self.update_text(warnings)

    def update_text(self, warnings):
        if isinstance(warnings, list):
            if not warnings:
                text_to_show = '<span style="color: #006400; font-weight: bold; font-size: 14pt;">No problems found! :)</span>'
            else:
                text_to_show = '<span style="color: #B22222; font-size: 10pt;">' + "<br>".join(warnings) + '</span>'
        else:
            if not warnings:
                text_to_show = '<span style="color: #006400; font-weight: bold; font-size: 10pt;">No problems found! :)</span>'
            else:
                text_to_show = f'<span style="color: #B22222; font-size: 10pt;">{warnings}</span>'

        self.text_box.setHtml(text_to_show)

    def refresh_warnings(self):
        if self.parent():
            new_warnings = self.parent().validate(return_warnings=True)  # parent.validate should return warnings list
            self.update_text(new_warnings)