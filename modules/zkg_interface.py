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
    QFrame,
    QDateTimeEdit,
    QCheckBox,
    QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, QDateTime, QPropertyAnimation, QRect, QThread, pyqtSignal
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
    QFrame,
    QDateTimeEdit,
    QCheckBox,
    QGraphicsDropShadowEffect,
    QProgressBar
)
from modules.data_converter import DataConverter
from modules.zk_interaction_utils import ZKDeviceController
from modules.settings_windows import SettingsWindow
import json
import os

class ExportWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, device_controller, start_date, end_date):
        super().__init__()
        self.device_controller = device_controller
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        try:
            # Retrieve Data
            attendance_data = self.device_controller.retrieve_attendance_with_user_names(
                start_date=self.start_date, 
                end_date=self.end_date
            )
            
            if not attendance_data:
                self.finished.emit("No attendance data retrieved for the selected range.")
                return

            # Convert to File
            converter = DataConverter(file_format='excel')
            converter.convert_att_to_file(attendance_data)
            
            count = len(attendance_data)
            self.finished.emit(f"Successfully exported {count} records!")

        except Exception as e:
            self.error.emit(str(e))


class ZKGInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.device_controller = None
        self.load_styles()
        self.init_ui()
        self.closeEvent = self.on_close

    def load_styles(self):
        style_path = os.path.join("assets", "styles.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        else:
            print("Style file not found!")

    def init_ui(self):
        # Window Setup
        self.setWindowTitle("Neon ZK Attendance")
        self.resize(500, 600)
        
        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- Header Section ---
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        
        self.title_label = QLabel("ZK Attendance")
        self.title_label.setObjectName("TitleLabel")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()

        self.btn_settings = QToolButton()
        self.btn_settings.setIcon(QIcon("icons/settings.png")) # Keep existing icon path if valid, or fallback
        self.btn_settings.setText("⚙") # Fallback text
        self.btn_settings.setToolTip("Settings")
        self.btn_settings.setStyleSheet("background: transparent; border: none; font-size: 20px; color: white;")
        self.btn_settings.clicked.connect(self.open_settings)
        header_layout.addWidget(self.btn_settings)

        main_layout.addWidget(header_frame)

        # --- Status Section ---
        status_frame = QFrame()
        status_frame.setObjectName("StatusFrame")
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label_title = QLabel("Device Status:")
        self.status_label = QLabel("Disconnected")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setStyleSheet("color: #ff3333;") # Red for disconnected

        status_layout.addWidget(self.status_label_title)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        main_layout.addWidget(status_frame)

        # --- Controls Section ---
        controls_frame = QFrame()
        controls_frame.setObjectName("ControlsFrame")
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(15)

        # Connect Button
        self.btn_connect = QPushButton("CONNECT DEVICE")
        self.btn_connect.setObjectName("BtnConnect")
        self.btn_connect.setCursor(Qt.PointingHandCursor)
        self.btn_connect.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_connect.setMinimumHeight(50)
        self.btn_connect.clicked.connect(self.toggle_connection)
        self.add_glow(self.btn_connect, "#bc13fe")
        controls_layout.addWidget(self.btn_connect)

        # Device Toggle
        self.btn_device = QPushButton("ENABLE DEVICE")
        self.btn_device.setEnabled(False)
        self.btn_device.setCursor(Qt.PointingHandCursor)
        self.btn_device.clicked.connect(self.toggle_device)
        controls_layout.addWidget(self.btn_device)

        # Export Users
        self.btn_export_users = QPushButton("EXPORT USERS DATA")
        self.btn_export_users.setEnabled(False)
        self.btn_export_users.setCursor(Qt.PointingHandCursor)
        self.btn_export_users.clicked.connect(self.export_users_data)
        controls_layout.addWidget(self.btn_export_users)
        
        main_layout.addWidget(controls_frame)

        # --- Filter & Export Section ---
        filter_frame = QFrame()
        filter_frame.setObjectName("FilterFrame")
        filter_layout = QVBoxLayout(filter_frame)

        filter_label = QLabel("Attendance Export")
        filter_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00f3ff;")
        filter_layout.addWidget(filter_label)
        
        # Checkbox to enable filtering
        self.chk_filter = QCheckBox("Filter by Date & Time")
        self.chk_filter.setStyleSheet("color: white; font-size: 14px;")
        self.chk_filter.setChecked(False)
        self.chk_filter.stateChanged.connect(self.toggle_filter_inputs)
        filter_layout.addWidget(self.chk_filter)

        # Date Inputs
        date_layout = QGridLayout()
        
        self.lbl_from = QLabel("From:")
        self.date_from = QDateTimeEdit(QDateTime.currentDateTime().addDays(-1))
        self.date_from.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.date_from.setCalendarPopup(True)
        self.date_from.setEnabled(False)
        
        self.lbl_to = QLabel("To:")
        self.date_to = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_to.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.date_to.setCalendarPopup(True)
        self.date_to.setEnabled(False)

        date_layout.addWidget(self.lbl_from, 0, 0)
        date_layout.addWidget(self.date_from, 0, 1)
        date_layout.addWidget(self.lbl_to, 1, 0)
        date_layout.addWidget(self.date_to, 1, 1)
        
        filter_layout.addLayout(date_layout)

        self.btn_export_attendance = QPushButton("EXPORT ATTENDANCE LOGS")
        self.btn_export_attendance.setEnabled(False)
        self.btn_export_attendance.setCursor(Qt.PointingHandCursor)
        self.btn_export_attendance.clicked.connect(self.export_attendance_data)
        filter_layout.addWidget(self.btn_export_attendance)

        main_layout.addWidget(filter_frame)
        
        # --- Loading Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setRange(0, 0) # Indeterminate
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #00f3ff, stop:1 #bc13fe);
                border-radius: 2px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Footer / Status
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        main_layout.addWidget(self.status_bar)

        self.footer_label = QLabel()
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setText(
            'Developed by <a href="https://wa.me/201065239871" style="color: #00f3ff; text-decoration: none; font-weight: bold;">Bedaba Edward</a> | '
            '<a href="https://github.com/bedaba/ZK_HRMS" style="color: #bc13fe; text-decoration: none; font-weight: bold;">GitHub</a>'
        )
        self.footer_label.setOpenExternalLinks(True)
        self.footer_label.setStyleSheet("font-size: 12px; margin-top: 5px; margin-bottom: 5px;")
        main_layout.addWidget(self.footer_label)

        self.setLayout(main_layout)

    def add_glow(self, widget, color_hex):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(color_hex))
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)

    def toggle_filter_inputs(self):
        enabled = self.chk_filter.isChecked()
        self.date_from.setEnabled(enabled)
        self.date_to.setEnabled(enabled)

    def update_status_label(self):
        if self.device_controller and self.device_controller.connection:
            self.status_label.setText("CONNECTED")
            self.status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
            # Add glow
            self.add_glow(self.status_label, "#00ff00")
        else:
            self.status_label.setText("DISCONNECTED")
            self.status_label.setStyleSheet("color: #ff3333; font-weight: bold;")
            self.status_label.setGraphicsEffect(None)
            
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
                self.disconnect_from_device()

            self.status_bar.showMessage("Connecting...")
            self.device_controller = ZKDeviceController(
                ip_address=settings["device_settings"]["ip_address"],
                port=settings["device_settings"]["port"],
                timeout=settings["device_settings"]["timeout"],
                password=settings["device_settings"]["password"],
            )
            self.device_controller.create_zk_instance()
            self.device_controller.connect_to_device()
            self.device_controller.disable_device()
            
            self.btn_connect.setText('DISCONNECT')
            self.btn_connect.setStyleSheet("border-color: #ff3333; color: #ff3333;")
            self.add_glow(self.btn_connect, "#ff3333")

            self.btn_device.setEnabled(True)
            self.btn_export_users.setEnabled(True)
            self.btn_export_attendance.setEnabled(True)
            
            if self.device_controller and self.device_controller.connection:
                self.btn_export_attendance.setEnabled(True)
            else:
                self.btn_export_attendance.setEnabled(False)
            
            self.status_bar.showMessage("Connected Successfully")
        except ValueError as e:
            self.show_error_dialog(f"Error connecting to device: {e}")
            self.status_bar.showMessage("Connection Failed")

    def disconnect_from_device(self):
        try:
            if self.device_controller:
                self.device_controller.disconnect_from_device()
                self.device_controller = None
                
                self.btn_connect.setText('CONNECT DEVICE')
                self.btn_connect.setStyleSheet("") # Revert to default stylesheet style (neon purple)
                self.add_glow(self.btn_connect, "#bc13fe")

                self.btn_device.setEnabled(False)
                self.btn_export_users.setEnabled(False)
                self.btn_export_attendance.setEnabled(False)
                self.status_bar.showMessage("Disconnected")

        except ValueError as e:
            self.show_error_dialog(f"Error disconnecting from device: {e}")

    def toggle_device(self):
        if self.device_controller:
            try:
                if self.device_controller.is_device_enabled():
                    self.device_controller.disable_device()
                    self.btn_device.setText('ENABLE DEVICE')
                    self.status_bar.showMessage("Device Disabled")
                else:
                    self.device_controller.enable_device()
                    self.btn_device.setText('DISABLE DEVICE')
                    self.status_bar.showMessage("Device Enabled")
                    
            except ValueError as e:
                self.show_error_dialog(f"Error toggling device: {e}")
        else:
            self.show_error_dialog("Please connect to the device first")

    def export_users_data(self):
        try:
            self.status_bar.showMessage("Exporting Users...")
            users_data = self.device_controller.retrieve_users_data()
            if users_data:
                converter = DataConverter(file_format='excel')
                converter.convert_users_to_file(users_data)
                self.status_bar.showMessage("Users Exported Successfully")
                QMessageBox.information(self, "Success", "Users data exported successfully!")
            else: 
                self.status_bar.showMessage("No users data found")
        except ValueError as e:
            self.show_error_dialog(f"Error exporting users data: {e}")
             
    def export_attendance_data(self):
        # 1. Prepare Dates
        start_date = None
        end_date = None
        
        if self.chk_filter.isChecked():
            start_date = self.date_from.dateTime().toPyDateTime()
            end_date = self.date_to.dateTime().toPyDateTime()

        # 2. Show Loading Bar
        self.progress_bar.setVisible(True)
        self.btn_export_attendance.setEnabled(False) # Prevent double click
        self.status_bar.showMessage("Exporting Data...")

        # 3. Setup Worker
        self.worker = ExportWorker(self.device_controller, start_date, end_date)
        
        # 4. Connect Signals
        self.worker.finished.connect(self.on_export_finished)
        self.worker.error.connect(self.on_export_error)
        
        # 5. Start
        self.worker.start()

    def on_export_finished(self, message):
        self.progress_bar.setVisible(False)
        self.btn_export_attendance.setEnabled(True)
        self.status_bar.showMessage(message)
        if "successfully" in message.lower():
             QMessageBox.information(self, "Success", message)
        else:
             QMessageBox.warning(self, "Export Info", message)

    def on_export_error(self, message):
        self.progress_bar.setVisible(False)
        self.btn_export_attendance.setEnabled(True)
        self.status_bar.showMessage("Export Failed")
        self.show_error_dialog(f"Error exporting data: {message}")

    def show_error_dialog(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()
        
    def open_settings(self):
        try:
            with open('settings.json', 'r') as file:
                settings = json.load(file)
            settings_window = SettingsWindow(settings)
            settings_window.exec_()
        except Exception as e:
            self.show_error_dialog(f"Could not load settings: {e}")
        
    def on_close(self, event):
        if self.device_controller is not None:
            try:
                self.device_controller.disconnect_from_device()
            except:
                pass
        event.accept()


def read_settings():
    with open('settings.json', 'r') as file:
        settings = json.load(file)
    return settings 
