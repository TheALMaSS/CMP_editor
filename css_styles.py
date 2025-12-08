button_style = """
    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #5E5E5E, stop:1 #3B3B3B);
        color: white;
        border: 1px solid #2A2A2A;
        border-radius: 6px;
        padding: 8px 12px;
        font-weight: bold;
        font-size: 9pt;
        margin: 0px 0px 0px 0px;
    }

    QPushButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #828282, stop:1 #555555);
    }

    QPushButton:pressed {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #3B3B3B, stop:1 #2A2A2A);
    }

    QPushButton:checked {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #4A6FAF, stop:1 #6A89C0);
    }
"""

delete_button_style = """
    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #AA2A2A, stop:1 #7A1E1E);
        color: white;
        border: 1px solid #4A0F0F;
        border-radius: 6px;
        padding: 8px 12px;
        font-weight: bold;
        font-size: 9pt;
        margin: 0px 0px 0px 0px;
    }

    QPushButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #CC3A3A, stop:1 #8A2626);
    }

    QPushButton:pressed {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #B83A3A, stop:1 #D14C4C);
        border: 1px solid #FF6666;
    }

    QPushButton:checked {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #B83A3A, stop:1 #D14C4C);
        border: 1px solid #FF6666;
    }
"""

arrow_button_style = """
    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #3A6EA8, stop:1 #2A4D7A);
        color: white;
        border: 1px solid #1A2E4A;
        border-radius: 6px;
        padding: 8px 12px;
        font-weight: bold;
        font-size: 9pt;
        margin: 0px 0px 0px 0px;
    }

    QPushButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #4A82C4, stop:1 #315A8F);
    }

    QPushButton:pressed {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #4A82C4, stop:1 #6A9FE0);
        border: 1px solid #77AFFF;
    }

    QPushButton:checked {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #4A82C4, stop:1 #6A9FE0);
        border: 1px solid #77AFFF;
    }
"""

validate_button_style = """
    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #3A8F8A, stop:1 #2A6B67);
        color: white;
        border: 1px solid #1A4A47;
        border-radius: 6px;
        padding: 8px 12px;
        font-weight: bold;
        font-size: 9pt;
        margin: 0px 0px 10px 0px;
    }

    QPushButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #4FB4AE, stop:1 #2F807A);
    }

    QPushButton:pressed {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #2A6B67, stop:1 #1A4A47);
    }

    QPushButton:checked {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #3C7FA5, stop:1 #4AA1C2);
    }
"""

left_panel_style = """
    background-color: #F5F5F5;
    border-right: 2px solid #888888;
"""

warnings_box_style = """
    background-color: #DEAB97;
    font-size: 10pt;
    color: #000000;              
    border: 2px solid #943210;
    border-radius: 4px;
    padding: 4px;
"""

warnings_title_style = """
    color: #943210;
    font-weight: bold;    
    font-size: 12pt;      
"""

delete_mode_label_style = """
    QLabel#modeLabel {
        background-color: #C22525;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12pt;
    }
"""

arrow_mode_label_style = """
    QLabel#modeLabel {
        background-color: #254FC2;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12pt;
    }
"""