from PyQt5.QtWidgets import (
    QDialog, 
    QVBoxLayout, 
    QFormLayout,
    QLineEdit, 
    QPushButton, 
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import json
import os

class SettingsWindow(QDialog):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.load_styles()
        self.init_ui()

    def load_styles(self):
        style_path = os.path.join("assets", "styles.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())

    def init_ui(self):
        self.setWindowTitle("Settings")
        self.setFixedWidth(400)
        self.setObjectName("MainWindow") # Recycle the main styling
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Frame
        frame = QFrame()
        frame.setObjectName("ControlsFrame") # Recycle frame styling
        frame_layout = QFormLayout(frame)
        frame_layout.setLabelAlignment(Qt.AlignRight)
        frame_layout.setVerticalSpacing(15)

        # Style helpers
        def make_input(text):
            inp = QLineEdit(str(text))
            inp.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 5px;
                    color: white;
                    padding: 5px;
                    font-size: 14px;
                }
            """)
            return inp

        def make_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #e0e0e0; font-size: 14px;")
            return lbl

        self.ip_address_edit = make_input(self.settings['device_settings']['ip_address'])
        frame_layout.addRow(make_label('IP Address:'), self.ip_address_edit)

        self.port_edit = make_input(self.settings['device_settings']['port'])
        frame_layout.addRow(make_label('Port:'), self.port_edit)

        self.timeout_edit = make_input(self.settings['device_settings']['timeout'])
        frame_layout.addRow(make_label('Timeout:'), self.timeout_edit)

        self.password_edit = make_input(self.settings['device_settings']['password'])
        self.password_edit.setEchoMode(QLineEdit.Password)
        frame_layout.addRow(make_label('Password:'), self.password_edit)

        self.file_format_edit = make_input(self.settings['file_format'])
        frame_layout.addRow(make_label('File Format:'), self.file_format_edit)
        
        self.export_path_edit = make_input(self.settings['export_path'])
        frame_layout.addRow(make_label('Export Path:'), self.export_path_edit)

        layout.addWidget(frame)

        save_button = QPushButton('SAVE SETTINGS')
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.clicked.connect(self.save_settings)
        
        # Add glow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor("#00f3ff"))
        shadow.setOffset(0, 0)
        save_button.setGraphicsEffect(shadow)
        
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_settings(self):
        try:
            self.settings['device_settings']['ip_address'] = self.ip_address_edit.text()
            self.settings['device_settings']['port'] = int(self.port_edit.text())
            self.settings['device_settings']['timeout'] = int(self.timeout_edit.text())
            self.settings['device_settings']['password'] = self.password_edit.text()
            self.settings['file_format'] = self.file_format_edit.text()
            self.settings['export_path'] = self.export_path_edit.text()

            with open('settings.json', 'w') as file:
                json.dump(self.settings, file)

            self.close()
        except Exception as e:
            print(f"Error saving settings: {e}")
