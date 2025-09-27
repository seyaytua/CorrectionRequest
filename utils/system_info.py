# utils/system_info.py
import socket
import platform
import os
from datetime import datetime

class SystemInfo:
    def get_info(self):
        """システム情報を取得"""
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
        except:
            hostname = "Unknown"
            ip_address = "Unknown"
        
        return {
            'ip_address': ip_address,
            'hostname': hostname,
            'os_info': f"{platform.system()} {platform.release()}",
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'timestamp': datetime.now().isoformat()
        }