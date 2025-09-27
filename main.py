# main.py - メインアプリケーション
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from datetime import datetime
import sqlite3
import json
import socket
import platform
import os
from pathlib import Path

# データベースとモジュールのインポート
from database.db_manager import DatabaseManager
from ui.main_window import MainWindow
from utils.system_info import SystemInfo
from auth.login import LoginDialog

class GradeCorrectionApp:
    def __init__(self):
        self.root = tb.Window(themename="cosmo")
        self.root.title("成績訂正申請システム")
        self.root.geometry("1200x800")
        
        # データベース初期化
        self.db_manager = DatabaseManager()
        self.db_manager.initialize_database()
        
        # システム情報取得
        self.system_info = SystemInfo()
        
        # ユーザー情報
        self.current_user = None
        
        # ログイン処理
        if self.show_login():
            self.setup_main_window()
        else:
            self.root.destroy()
    
    def show_login(self):
        """ログインダイアログを表示"""
        login_dialog = LoginDialog(self.root)
        self.root.wait_window(login_dialog.dialog)
        
        if login_dialog.user_info:
            self.current_user = login_dialog.user_info
            return True
        return False
    
    def setup_main_window(self):
        """メインウィンドウの設定"""
        self.main_window = MainWindow(
            self.root, 
            self.db_manager, 
            self.current_user,
            self.system_info
        )
    
    def run(self):
        """アプリケーション実行"""
        self.root.mainloop()

if __name__ == "__main__":
    app = GradeCorrectionApp()
    app.run()
    quit
    