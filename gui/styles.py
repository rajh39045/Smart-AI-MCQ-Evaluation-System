# gui/styles.py

DARK_THEME = """
QMainWindow {
    background-color: #1E1E1E;
}

QWidget {
    background-color: #1E1E1E;
    color: white;
    font-family: Segoe UI;
    font-size: 14px;
}

QLabel {
    color: white;
    font-size: 15px;
}

QPushButton {
    background-color: #007ACC;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1A8CFF;
}

QPushButton:pressed {
    background-color: #005F99;
}

QPushButton:disabled {
    background-color: #555555;
    color: #AAAAAA;
}

QMessageBox {
    background-color: #252526;
}

QToolTip {
    background-color: #333333;
    color: white;
    border: 1px solid #666666;
}
"""