from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QSizePolicy,
    QToolButton,
    QStatusBar,
    QHBoxLayout,
)
from PyQt5.QtGui import QIcon
from modules.data_converter import DataConverter
from modules.zk_interaction_utils import ZKDeviceController
from modules.settings_windows import SettingsWindow

import json


class ZKGInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.device_controller = None
        self.closeEvent = self.on_close

    def init_ui(self):
        # Main layout
        layout = QVBoxLayout()

        # Title and settings button
        title_layout = QHBoxLayout()
        self.title_label = QLabel("Attendance System")
        title_layout.addWidget(self.title_label)

        # Settings button with tool tip
        self.btn_settings = QToolButton()
        self.btn_settings.setIcon(QIcon("icons/settings.png"))
        self.btn_settings.setToolTip("Open settings")
        self.btn_settings.clicked.connect(self.open_settings)
        title_layout.addWidget(self.btn_settings)

        layout.addLayout(title_layout)

        # Connection and device control section
        button_layout = QGridLayout()

        # Connect button
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_connect.clicked.connect(self.toggle_connection)
        button_layout.addWidget(self.btn_connect, 0, 0)

        # Device status label
        self.status_label = QLabel("Device Status:")
        self.status_label.setText("Disconnected")
        self.status_label.setStyleSheet("color: red;")
        self.status_label.setVisible(True)
        button_layout.addWidget(self.status_label, 0, 1)

        # Enable/disable device button
        self.btn_device = QPushButton("Enable Device")
        self.btn_device.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_device.setEnabled(False)
        self.btn_device.clicked.connect(self.toggle_device)
        button_layout.addWidget(self.btn_device, 1, 0)

        # Export user data button
        self.btn_export_users = QPushButton("Export Users Data")
        self.btn_export_users.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_export_users.setEnabled(False)
        self.btn_export_users.clicked.connect(self.export_users_data)
        button_layout.addWidget(self.btn_export_users, 2, 0)

        # Export attendance data button
        self.btn_export_attendance = QPushButton("Export Attendance Data")
        self.btn_export_attendance.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_export_attendance.setEnabled(False)
        self.btn_export_attendance.clicked.connect(self.export_attendance_data)
        button_layout.addWidget(self.btn_export_attendance, 2, 1)

        layout.addLayout(button_layout)

        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

        # Set layout and window title
        self.setLayout(layout)
        self.setWindowTitle("Attendance System")

    def update_status_label(self):
        if self.device_controller and self.device_controller.connection:
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: green;")
            self.status_label.setVisible(True)
        else:
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setVisible(True)
            
    def toggle_connection(self):
        if not self.device_controller:
            self.connect_to_device()
        else:
            self.disconnect_from_device()
        self.update_status_label()


    def connect_to_device(self):
        settings = read_settings()
        try:
            if self.device_controller:
                # Disconnect if already connected
                self.disconnect_from_device()

            # Connect to device
            self.device_controller = ZKDeviceController(
                ip_address=settings["device_settings"]["ip_address"],
                port=settings["device_settings"]["port"],
                timeout=settings["device_settings"]["timeout"],
                password=settings["device_settings"]["password"],
            )
            self.device_controller.create_zk_instance()
            self.device_controller.connect_to_device()
            self.device_controller.disable_device()
            self.btn_connect.setText('Disconnect')
            self.btn_device.setEnabled(True)
            self.btn_export_users.setEnabled(True)
            self.btn_export_attendance.setEnabled(True)
            
            # Check if the device controller and connection are valid before enabling 'Export Attendance Data' button
            if self.device_controller and self.device_controller.connection:
                self.btn_export_attendance.setEnabled(True)
            else:
                self.btn_export_attendance.setEnabled(False)
        except ValueError as e:
            self.show_error_dialog(f"Error connecting to device: {e}")

    def disconnect_from_device(self):
        try:
            if self.device_controller:
                # Disconnect from the device
                self.device_controller.disconnect_from_device()
                self.device_controller = None
                self.btn_connect.setText('Connect')
                self.btn_device.setEnabled(False)
                self.btn_export_users.setEnabled(False)
                self.btn_export_attendance.setEnabled(False)

        except ValueError as e:
            self.show_error_dialog(f"Error disconnecting from device: {e}")

    def toggle_device(self):
        if self.device_controller:
            try:
                if self.device_controller.is_device_enabled():
                    self.device_controller.disable_device()
                    print("Device disabled")
                    self.btn_device.setText('Enable Device')
                else:
                    self.device_controller.enable_device()
                    print("Device enabled")
                    self.btn_device.setText('Disable Device')
                    
            except ValueError as e:
                self.show_error_dialog(f"Error toggling device: {e}")
        else:
            print("Please connect to the device first")

    def export_users_data(self):
        try:
            users_data = self.device_controller.retrieve_users_data()
            if users_data:
                converter = DataConverter(file_format='excel')
                converter.convert_users_to_file(users_data)
            else: 
                print("No users data retrieved.")
        except ValueError as e:
            self.show_error_dialog(f"Error exporting users data: {e}")
             
    def export_attendance_data(self):
        try:
            attendance_data = self.device_controller.retrieve_attendance_data()
            if attendance_data:
                converter = DataConverter(file_format='excel')
                converter.convert_att_to_file(attendance_data)
            else: 
                print("No attendance data retrieved.")
        except ValueError as e:
            self.show_error_dialog(f"Error exporting attendance data: {e}")

    def show_error_dialog(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()
        
    def open_settings(self):
        with open('settings.json', 'r') as file:
            settings = json.load(file)

        settings_window = SettingsWindow(settings)
        settings_window.exec_()
        
    def on_close(self, event):
        if self.device_controller is not None:
            self.device_controller.disconnect_from_device()
        event.accept()


def read_settings():
    # Read settings from JSON file
    with open('settings.json', 'r') as file:
        settings = json.load(file)
    return settings 
