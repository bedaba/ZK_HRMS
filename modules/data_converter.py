from datetime import datetime
import pandas as pd
import os
import json


class DataConverter:
    def __init__(self, file_format='excel'):
        self.file_format = file_format
        self.export_path = read_settings()['export_path']
    
    def convert_att_to_file(self, att_data):
        file_name = f"attendance_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        aslist = []
        

        for record in att_data:
            aslist.append([record.user_id, record.timestamp, record.punch])
        if self.export_path:
            file_name = os.path.join(self.export_path, file_name)
        if self.file_format == 'excel':
            file_name += ".xlsx" 
            self._convert_to_excel(aslist, ["id", "timestamp", "punch"],file_name)
        # Add support for other formats here
        else:
            raise ValueError(f"Unsupported file format: {self.file_format}")

    def convert_users_to_file(self, users_data):
        file_name = f"users_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        aslist = []
        for record in users_data:
            aslist.append([record.user_id, record.name])
        if self.export_path:
            file_name = os.path.join(self.export_path, file_name)

        if self.file_format == 'excel':
            file_name += ".xlsx"
            self._convert_to_excel(aslist, ["id", "name"],file_name)
        # Add support for other formats here
        else:
            raise ValueError(f"Unsupported file format: {self.file_format}")
    def _convert_to_excel(self, aslist, columns, file_name):
        df = pd.DataFrame(data=aslist, columns=columns)
        df.to_excel(file_name, index=False)
        
def read_settings():
    # Read settings from JSON file
    with open('settings.json', 'r') as file:
        settings = json.load(file)
    return settings 