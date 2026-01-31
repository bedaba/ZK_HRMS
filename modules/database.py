
import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="hrms_data.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS export_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT,
                record_count INTEGER,
                filter_start TEXT,
                filter_end TEXT,
                file_path TEXT,
                timestamp TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                export_id INTEGER,
                user_id INTEGER,
                name TEXT,
                timestamp TEXT,
                punch_type TEXT,
                status INTEGER,
                FOREIGN KEY(export_id) REFERENCES export_logs(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()

    def log_export(self, device_name, record_count, file_path, start_date=None, end_date=None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO export_logs (device_name, record_count, file_path, filter_start, filter_end, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (device_name, record_count, file_path, str(start_date), str(end_date), timestamp))
        export_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return export_id

    def save_export_records(self, export_id, records):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        data_to_insert = []
        for r in records:
            # record dict: {"User ID", "Name", "Time", "Type", "Status"}
            data_to_insert.append((
                export_id,
                r.get("User ID"),
                r.get("Name"),
                str(r.get("Time")),
                str(r.get("Type")),
                r.get("Status")
            ))
            
        cursor.executemany('''
            INSERT INTO attendance_records (export_id, user_id, name, timestamp, punch_type, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', data_to_insert)
        
        conn.commit()
        conn.close()

    def get_export_history(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM export_logs ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_export_records(self, export_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM attendance_records WHERE export_id = ?', (export_id,))
        rows = cursor.fetchall()
        conn.close()
        
        # Convert back to list of dicts for UI
        records = []
        for r in rows:
            # db row: id, export_id, user_id, name, timestamp, punch_type, status
            records.append({
                "User ID": r[2],
                "Name": r[3],
                "Time": r[4],
                "Type": r[5],
                "Status": r[6]
            })
        return records

    def delete_export(self, export_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # Enable FK support for cascade
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("DELETE FROM export_logs WHERE id = ?", (export_id,))
        conn.commit()
        conn.close()
