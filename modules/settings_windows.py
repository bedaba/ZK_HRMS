from PyQt5.QtWidgets import (
    QDialog, 
    QVBoxLayout, 
    QFormLayout,
    QLineEdit, 
    QPushButton, 
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect,
    QListWidget,
    QHBoxLayout,
    QMessageBox,
    QTabWidget,
    QWidget
)
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import Qt
import json
import os

class SettingsWindow(QDialog):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        # Ensure new structure exists
        if "devices" not in self.settings:
            self.settings["devices"] = []
        if "active_device_index" not in self.settings:
            self.settings["active_device_index"] = 0
            
        self.load_styles()
        self.init_ui()

    def load_styles(self):
        style_path = os.path.join("assets", "styles.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())

    def init_ui(self):
        self.setWindowTitle("Settings")
        self.setFixedWidth(500)
        self.setFixedHeight(600)
        self.setObjectName("MainWindow")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.2); }
            QTabBar::tab { background: rgba(0,0,0,0.2); color: white; padding: 10px; }
            QTabBar::tab:selected { background: rgba(0, 243, 255, 0.2); border-bottom: 2px solid #00f3ff; }
        """)
        
        # --- Devices Tab ---
        devices_tab = QWidget()
        dev_layout = QVBoxLayout(devices_tab)
        
        self.device_list = QListWidget()
        self.device_list.setStyleSheet("background: rgba(0,0,0,0.3); color: white; border: 1px solid rgba(255,255,255,0.1);")
        self.device_list.currentRowChanged.connect(self.load_device_details)
        dev_layout.addWidget(self.device_list)
        
        # Device Actions
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add Device")
        btn_add.clicked.connect(self.add_device)
        btn_del = QPushButton("Remove Device")
        btn_del.clicked.connect(self.remove_device)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_del)
        dev_layout.addLayout(btn_layout)
        
        # Device Details Form
        self.dev_form_frame = QFrame()
        self.dev_form_layout = QFormLayout(self.dev_form_frame)
        
        self.name_edit = self.make_input("")
        self.ip_edit = self.make_input("")
        self.port_edit = self.make_input("4370")
        self.timeout_edit = self.make_input("10")
        self.password_edit = self.make_input("")

        self.dev_form_layout.addRow(self.make_label("Name:"), self.name_edit)
        self.dev_form_layout.addRow(self.make_label("IP:"), self.ip_edit)
        self.dev_form_layout.addRow(self.make_label("Port:"), self.port_edit)
        self.dev_form_layout.addRow(self.make_label("Timeout:"), self.timeout_edit)
        self.dev_form_layout.addRow(self.make_label("Password:"), self.password_edit)
        
        dev_layout.addWidget(self.dev_form_frame)
        
        # Save Device Change Button
        btn_update_dev = QPushButton("Update Selected Device")
        btn_update_dev.clicked.connect(self.update_current_device)
        dev_layout.addWidget(btn_update_dev)

        tabs.addTab(devices_tab, "Devices")
        
        # --- General Tab ---
        gen_tab = QWidget()
        gen_layout = QFormLayout(gen_tab)
        
        self.file_format_edit = self.make_input(self.settings.get('file_format', 'excel'))
        gen_layout.addRow(self.make_label('File Format:'), self.file_format_edit)
        
        self.export_path_edit = self.make_input(self.settings.get('export_path', './'))
        gen_layout.addRow(self.make_label('Export Path:'), self.export_path_edit)
        
        tabs.addTab(gen_tab, "General")
        
        layout.addWidget(tabs)

        # Save All Button
        save_button = QPushButton('SAVE ALL & CLOSE')
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.clicked.connect(self.save_settings)
        self.add_glow(save_button, "#00f3ff")
        layout.addWidget(save_button)

        self.setLayout(layout)
        self.refresh_device_list()

    def make_input(self, text):
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

    def make_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #e0e0e0; font-size: 14px;")
        return lbl

    def add_glow(self, widget, color_hex):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(color_hex))
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)

    def refresh_device_list(self):
        self.device_list.clear()
        for dev in self.settings["devices"]:
            self.device_list.addItem(f"{dev.get('name', 'Unknown')} ({dev.get('ip')})")

    def load_device_details(self, index):
        if index < 0 or index >= len(self.settings["devices"]):
            return
        
        dev = self.settings["devices"][index]
        self.name_edit.setText(dev.get("name", ""))
        self.ip_edit.setText(dev.get("ip", ""))
        self.port_edit.setText(str(dev.get("port", 4370)))
        self.timeout_edit.setText(str(dev.get("timeout", 10)))
        self.password_edit.setText(dev.get("password", ""))

    def add_device(self):
        new_dev = {
            "name": "New Device",
            "ip": "192.168.1.201",
            "port": 4370,
            "timeout": 10,
            "password": ""
        }
        self.settings["devices"].append(new_dev)
        self.refresh_device_list()
        self.device_list.setCurrentRow(len(self.settings["devices"]) - 1)

    def remove_device(self):
        row = self.device_list.currentRow()
        if row >= 0:
            del self.settings["devices"][row]
            self.refresh_device_list()

    def update_current_device(self):
        row = self.device_list.currentRow()
        if row >= 0:
            dev = self.settings["devices"][row]
            dev["name"] = self.name_edit.text()
            dev["ip"] = self.ip_edit.text()
            dev["port"] = int(self.port_edit.text())
            dev["timeout"] = int(self.timeout_edit.text())
            dev["password"] = self.password_edit.text()
            self.refresh_device_list()
            self.device_list.setCurrentRow(row) # Keep selection

    def save_settings(self):
        try:
            # Update General Settings
            self.settings['file_format'] = self.file_format_edit.text()
            self.settings['export_path'] = self.export_path_edit.text()

            with open('settings.json', 'w') as file:
                json.dump(self.settings, file)

            self.close()
        except Exception as e:
            print(f"Error saving settings: {e}")
