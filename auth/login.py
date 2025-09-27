# auth/login.py
import tkinter as tk
from tkinter import ttk, messagebox
import hashlib

class LoginDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("ログイン")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.user_info = None
        
        self.setup_ui()
        
        # ウィンドウを中央に配置
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """ログインUI設定"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        ttk.Label(main_frame, text="成績訂正申請システム", 
                 font=('', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
        
        # ユーザー名
        ttk.Label(main_frame, text="ユーザー名:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.username_var, width=25).grid(row=1, column=1, padx=5, pady=5)
        
        # パスワード
        ttk.Label(main_frame, text="パスワード:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=25).grid(row=2, column=1, padx=5, pady=5)
        
        # ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="ログイン", command=self.login).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="キャンセル", command=self.cancel).grid(row=0, column=1, padx=5)
        
        # Enterキーでログイン
        self.dialog.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """ログイン処理"""
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("エラー", "ユーザー名とパスワードを入力してください")
            return
        
        # 簡易的な認証（実際の運用では適切な認証システムを使用）
        # ここではデモ用のハードコードされた認証
        users = {
            'admin': {
                'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
                'name': '管理者',
                'id': 'ADM001',
                'is_admin': True
            },
            'user1': {
                'password_hash': hashlib.sha256('user123'.encode()).hexdigest(),
                'name': '田中太郎',
                'id': 'USR001',
                'is_admin': False
            }
        }
        
        if username in users:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if users[username]['password_hash'] == password_hash:
                self.user_info = {
                    'username': username,
                    'name': users[username]['name'],
                    'id': users[username]['id'],
                    'is_admin': users[username]['is_admin']
                }
                self.dialog.destroy()
            else:
                messagebox.showerror("ログインエラー", "パスワードが正しくありません")
        else:
            messagebox.showerror("ログインエラー", "ユーザー名が見つかりません")
    
    def cancel(self):
        """キャンセル"""
        self.dialog.destroy()