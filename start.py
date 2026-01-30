#!/usr/bin/python3
import sys
from PyQt5.QtWidgets import QApplication
from modules.zkg_interface import ZKGInterface

def run_attendance_interface():
    app = QApplication(sys.argv)
    main_app = ZKGInterface()
    main_app.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_attendance_interface()
