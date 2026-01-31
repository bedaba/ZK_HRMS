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

    def retrieve_attendance_data(self, start_date=None, end_date=None):
        try:
            if self.connection:
                attendances = self.connection.get_attendance()
                if len(attendances) == 0:
                    logging.warning("No attendance data found")
                
                if start_date and end_date:
                    filtered_attendances = []
                    for att in attendances:
                        if start_date <= att.timestamp <= end_date:
                            filtered_attendances.append(att)
                    return filtered_attendances
                
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

    def retrieve_attendance_with_user_names(self, start_date=None, end_date=None):
        try:
            # 1. Get Users Map
            users = self.retrieve_users_data()
            user_map = {u.user_id: u.name for u in users}
            
            # 2. Get Attendance
            attendance = self.retrieve_attendance_data(start_date, end_date)
            
            # 3. Merge
            merged_data = []
            
            punch_type_map = {
                0: "Check-In",
                1: "Check-Out",
                2: "Break-Out",
                3: "Break-In",
                4: "Overtime-In",
                5: "Overtime-Out"
            }
            
            for att in attendance:
                name = user_map.get(att.user_id, "Unknown")
                punch_str = punch_type_map.get(att.punch, str(att.punch))
                
                merged_data.append({
                    "User ID": att.user_id,
                    "Name": name,
                    "Time": att.timestamp,
                    "Type": punch_str,
                    "Status": att.status
                })
            return merged_data
            
        except Exception as e:
            error_msg = f"Error retrieving merged data: {e}"
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
