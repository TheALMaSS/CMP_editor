button_style = """
    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #4D4D4D, stop:1 #2E2E2E);
        color: white;
        border: 1px solid #1C1C1C;
        border-radius: 6px;
        padding: 8px 12px;
        font-weight: bold;
        font-size: 9pt;
        margin: 0px 0px 10px 0px;
    }

    QPushButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #6E6E6E, stop:1 #3D3D3D);
    }

    QPushButton:pressed {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #2E2E2E, stop:1 #1C1C1C);
    }

    QPushButton:checked {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #3D5F9F, stop:1 #5C7BB8);
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