from zk import ZK, const
import logging
import hashlib
import re

class ZKDeviceController:
    def __init__(self, ip_address: str, port: int, timeout: int, password: str):
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip_address):
            raise ValueError("Invalid IP address format")
        if not isinstance(port, int):
            raise ValueError("Invalid port")
        if not isinstance(timeout, int):
            raise ValueError("Invalid timeout")
        self.connection = None
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.password = hashlib.sha256(password.encode()).hexdigest()
        self.zk = None

    def create_zk_instance(self):
        try:
            self.zk = ZK(self.ip_address, self.port, self.timeout, 0, force_udp=False, ommit_ping=False)
        except Exception as e:
            error_msg = f"Failed to initialize ZK: {e}"
            logging.error(error_msg)
            raise ValueError(error_msg)

    def connect_to_device(self):
        try:
            if self.zk is None:
                raise ValueError("ZK instance not created")
            
            # connect to device
            self.connection = self.zk.connect()
            self.connection.read_sizes()
            return self.connection
        except Exception as e:
            error_msg = f"Failed to connect to device {self.ip_address}:{self.port}: {e}"
            logging.error(error_msg)
            raise ValueError(error_msg)

    def disable_device(self):
        if self.connection:
            self.connection.disable_device()
        else:
            raise ValueError("Invalid Connection")

    def enable_device(self):
        if self.connection:
            self.connection.enable_device()
        else:
            raise ValueError("Invalid Connection")

    def disconnect_from_device(self):
        try:
            if self.connection:
                self.enable_device()
                self.connection.disconnect()
                self.connection = None
            else:
                raise ValueError("Invalid Connection")
        except Exception as e:
            error_msg = f"Failed to disconnect from device: {e}"
            logging.error(error_msg)
            raise ValueError(error_msg)

    def retrieve_attendance_data(self):
        try:
            if self.connection:
                attendances = self.connection.get_attendance()
                if len(attendances) == 0:
                    logging.warning("No attendance data found")
                return attendances
            else:
                raise ValueError("Invalid Connection")
        except Exception as e:
            error_msg = f"Error retrieving attendance data: {e}"
            logging.error(error_msg)
            raise ValueError(error_msg)

    def retrieve_users_data(self):
        try:
            if self.connection:
                users = self.connection.get_users()
                if len(users) == 0:
                    logging.warning("No users data found")
                return users
            else:
                raise ValueError("Invalid Connection")
        except Exception as e:
            error_msg = f"Error retrieving users data: {e}"
            logging.error(error_msg)
            raise ValueError(error_msg)

    def is_device_enabled(self):
        try:
            if self.connection.is_enabled:
                return self.connection.is_enabled
            else:
                return False
        except Exception as e:
            error_msg = f"Error checking device status: {e}"
            logging.error(error_msg)
            raise ValueError(error_msg)
