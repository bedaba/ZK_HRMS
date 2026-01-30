from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton
import json

class SettingsWindow(QDialog):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.ip_address_edit = QLineEdit(self.settings['device_settings']['ip_address'])
        layout.addRow('IP Address:', self.ip_address_edit)

        self.port_edit = QLineEdit(str(self.settings['device_settings']['port']))
        layout.addRow('Port:', self.port_edit)

        self.timeout_edit = QLineEdit(str(self.settings['device_settings']['timeout']))
        layout.addRow('Timeout:', self.timeout_edit)

        self.password_edit = QLineEdit(self.settings['device_settings']['password'])
        layout.addRow('Password:', self.password_edit)

        self.file_format_edit = QLineEdit(self.settings['file_format'])
        layout.addRow('File Format:', self.file_format_edit)
        
        self.export_path_edit = QLineEdit(self.settings['export_path'])
        layout.addRow('Export Path:', self.export_path_edit)

        save_button = QPushButton('Save Settings')
        save_button.clicked.connect(self.save_settings)
        layout.addRow(save_button)

        self.setLayout(layout)

    def save_settings(self):
        self.settings['device_settings']['ip_address'] = self.ip_address_edit.text()
        self.settings['device_settings']['port'] = int(self.port_edit.text())
        self.settings['device_settings']['timeout'] = int(self.timeout_edit.text())
        self.settings['device_settings']['password'] = self.password_edit.text()
        self.settings['file_format'] = self.file_format_edit.text()
        self.settings['export_path'] = self.export_path_edit.text()


        with open('settings.json', 'w') as file:
            json.dump(self.settings, file)

        self.close()

