# ui/main_window.py - 完全版（レイアウト調整・最大化起動）
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from datetime import datetime
import json
import re

class MainWindow:
    def __init__(self, root, db_manager, current_user, system_info):
        self.root = root
        self.db_manager = db_manager
        self.current_user = current_user
        self.system_info = system_info
        
        # ウィンドウを最大化して起動
        self.root.state('zoomed')  # Windows
        try:
            self.root.attributes('-zoomed', True)  # Linux
        except:
            pass
        
        # macOSの場合の最大化
        self.root.update()
        self.root.attributes('-fullscreen', False)
        
        # スタイル設定
        self.setup_styles()
        
        # 管理者かユーザーかで異なるUIを表示
        if self.current_user.get('is_admin', False):
            self.setup_admin_ui()
        else:
            self.setup_user_ui()
    
    def setup_styles(self):
        """カスタムスタイルの設定"""
        style = ttk.Style()
        
        # フォントサイズ
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Section.TLabelframe.Label', font=('Arial', 11, 'bold'))
        style.configure('Required.TLabel', foreground='red', font=('Arial', 9, 'bold'))
        
        # ボタンスタイル
        style.configure('Submit.TButton', font=('Arial', 10, 'bold'))
        style.configure('Clear.TButton', font=('Arial', 10))
        style.configure('Approve.TButton', font=('Arial', 10, 'bold'))
        style.configure('Reject.TButton', font=('Arial', 10, 'bold'))
    
    def setup_user_ui(self):
        """一般ユーザー用UI"""
        self.setup_ui()
    
    def setup_admin_ui(self):
        """管理者用UI - 承認機能付き"""
        # メインコンテナ
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # PanedWindowで左右の比率を調整
        paned_window = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 左側：入力エリア（30%）
        left_frame = ttk.Frame(paned_window)
        
        # 右側：一覧・承認エリア（70%）
        right_frame = ttk.Frame(paned_window)
        
        # PanedWindowに追加（比率設定）
        paned_window.add(left_frame, weight=30)
        paned_window.add(right_frame, weight=70)
        
        # 左側のコンテンツ（入力フォーム）
        self.setup_left_panel(left_frame)
        
        # 右側のコンテンツ（管理者用の承認機能付き一覧）
        self.setup_admin_right_panel(right_frame)
    
    def setup_ui(self):
        """通常ユーザー用UI設定"""
        # メインコンテナ
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # PanedWindowで左右の比率を調整
        paned_window = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 左側：入力エリア（30%）
        left_frame = ttk.Frame(paned_window)
        
        # 右側：履歴一覧エリア（70%）
        right_frame = ttk.Frame(paned_window)
        
        # PanedWindowに追加（比率設定）
        paned_window.add(left_frame, weight=30)
        paned_window.add(right_frame, weight=70)
        
        # 左側のコンテンツ
        self.setup_left_panel(left_frame)
        
        # 右側のコンテンツ
        self.setup_right_panel(right_frame)
    
    def setup_left_panel(self, parent):
        """左側パネル - 入力フォーム（30%幅）"""
        # タイトル
        title_label = ttk.Label(parent, text="成績訂正申請システム", style='Title.TLabel')
        title_label.pack(pady=(5, 10))
        
        # スクロール可能なフレーム
        canvas = tk.Canvas(parent, bg='white')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # セクション1: 記入者情報
        self.setup_applicant_section(scrollable_frame)
        
        # セクション2: 訂正理由
        self.setup_reason_section(scrollable_frame)
        
        # セクション3: 対象者選択
        self.setup_target_section(scrollable_frame)
        
        # セクション4: 訂正種別
        self.setup_correction_type_section(scrollable_frame)
        
        # セクション5: 対象期間
        self.setup_period_section(scrollable_frame)
        
        # ボタングループ
        self.setup_buttons(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_applicant_section(self, parent):
        """記入者情報セクション"""
        frame = ttk.LabelFrame(parent, text="1. 記入者情報", 
                              style='Section.TLabelframe', padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        row_frame = ttk.Frame(frame)
        row_frame.pack(fill=tk.X)
        
        ttk.Label(row_frame, text="記入者名:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.applicant_name_var = tk.StringVar(value=self.current_user.get('name', ''))
        entry = ttk.Entry(row_frame, textvariable=self.applicant_name_var, 
                         font=('Arial', 9), width=20)
        entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(row_frame, text="*必須", style='Required.TLabel').pack(side=tk.LEFT)
    
    def setup_reason_section(self, parent):
        """訂正理由セクション"""
        frame = ttk.LabelFrame(parent, text="2. 訂正理由", 
                              style='Section.TLabelframe', padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        label_frame = ttk.Frame(frame)
        label_frame.pack(fill=tk.X)
        ttk.Label(label_frame, text="訂正が必要な理由を具体的に記入してください", 
                 font=('Arial', 9)).pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*必須", style='Required.TLabel').pack(side=tk.LEFT, padx=(5, 0))
        
        self.reason_text = tk.Text(frame, height=3, font=('Arial', 9), 
                                  wrap=tk.WORD, borderwidth=2, relief="groove")
        self.reason_text.pack(fill=tk.BOTH, pady=(5, 0))
    
    def setup_target_section(self, parent):
        """対象者選択セクション"""
        frame = ttk.LabelFrame(parent, text="3. 対象者選択", 
                              style='Section.TLabelframe', padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # ラジオボタン
        radio_frame = ttk.Frame(frame)
        radio_frame.pack(fill=tk.X)
        
        self.target_type_var = tk.StringVar(value="individual")
        ttk.Radiobutton(radio_frame, text="個人", variable=self.target_type_var,
                       value="individual", command=self.toggle_target_type).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(radio_frame, text="複数（同一理由）", variable=self.target_type_var,
                       value="multiple", command=self.toggle_target_type).pack(side=tk.LEFT)
        
        # 個人入力フレーム
        self.individual_frame = ttk.Frame(frame)
        self.individual_frame.pack(fill=tk.X, pady=(8, 0))
        
        # 組番号
        number_frame = ttk.Frame(self.individual_frame)
        number_frame.pack(fill=tk.X, pady=2)
        ttk.Label(number_frame, text="組番号:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.student_number_var = tk.StringVar()
        ttk.Entry(number_frame, textvariable=self.student_number_var,
                 font=('Arial', 9), width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(number_frame, text="(例: F1234)", font=('Arial', 8), foreground='gray').pack(side=tk.LEFT)
        
        # 氏名
        name_frame = ttk.Frame(self.individual_frame)
        name_frame.pack(fill=tk.X, pady=2)
        ttk.Label(name_frame, text="氏名:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.student_name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.student_name_var,
                 font=('Arial', 9), width=15).pack(side=tk.LEFT)
        
        # 複数入力フレーム（初期は非表示）
        self.multiple_frame = ttk.Frame(frame)
        self.setup_multiple_students_table()
    
    def setup_multiple_students_table(self):
        """複数生徒入力テーブル"""
        # ヘッダー
        header_frame = ttk.Frame(self.multiple_frame)
        header_frame.pack(fill=tk.X, pady=(5, 3))
        
        ttk.Label(header_frame, text="No.", width=4, font=('Arial', 8, 'bold')).pack(side=tk.LEFT, padx=3)
        ttk.Label(header_frame, text="組番号", width=8, font=('Arial', 8, 'bold')).pack(side=tk.LEFT, padx=3)
        ttk.Label(header_frame, text="氏名", width=12, font=('Arial', 8, 'bold')).pack(side=tk.LEFT, padx=3)
        ttk.Label(header_frame, text="操作", width=6, font=('Arial', 8, 'bold')).pack(side=tk.LEFT, padx=3)
        
        # 生徒入力行を格納するフレーム
        self.students_container = ttk.Frame(self.multiple_frame)
        self.students_container.pack(fill=tk.BOTH, expand=True)
        
        # 追加ボタン
        add_button = ttk.Button(self.multiple_frame, text="+ 追加",
                               command=self.add_student_row)
        add_button.pack(pady=5)
        
        self.student_entries = []
        self.add_student_row()  # 初期行を1つ追加
    
    def add_student_row(self):
        """生徒入力行を追加"""
        row_frame = ttk.Frame(self.students_container)
        row_frame.pack(fill=tk.X, pady=1)
        
        row_num = len(self.student_entries) + 1
        
        ttk.Label(row_frame, text=str(row_num), width=4, font=('Arial', 8)).pack(side=tk.LEFT, padx=3)
        
        number_var = tk.StringVar()
        ttk.Entry(row_frame, textvariable=number_var, width=8, font=('Arial', 8)).pack(side=tk.LEFT, padx=3)
        
        name_var = tk.StringVar()
        ttk.Entry(row_frame, textvariable=name_var, width=12, font=('Arial', 8)).pack(side=tk.LEFT, padx=3)
        
        def remove_this_row():
            if len(self.student_entries) > 1:
                row_frame.destroy()
                self.student_entries.remove((number_var, name_var))
                self.update_row_numbers()
            else:
                messagebox.showwarning("警告", "最低1名は必要です")
        
        ttk.Button(row_frame, text="削除", command=remove_this_row, width=6).pack(side=tk.LEFT, padx=3)
        
        self.student_entries.append((number_var, name_var))
    
    def update_row_numbers(self):
        """行番号を更新"""
        for i, child in enumerate(self.students_container.winfo_children()):
            if child.winfo_class() == 'Frame':
                label = child.winfo_children()[0]
                if label.winfo_class() == 'Label':
                    label.config(text=str(i + 1))
    
    def setup_correction_type_section(self, parent):
        """訂正種別セクション"""
        frame = ttk.LabelFrame(parent, text="4. 訂正種別", 
                              style='Section.TLabelframe', padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # ラジオボタン
        radio_frame = ttk.Frame(frame)
        radio_frame.pack(fill=tk.X)
        
        self.correction_type_var = tk.StringVar(value="attendance")
        ttk.Radiobutton(radio_frame, text="出欠関連", variable=self.correction_type_var,
                       value="attendance", command=self.toggle_correction_type).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(radio_frame, text="成績のみ", variable=self.correction_type_var,
                       value="grade", command=self.toggle_correction_type).pack(side=tk.LEFT)
        
        # 詳細入力エリア
        self.correction_detail_frame = ttk.Frame(frame)
        self.correction_detail_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        
        # 出欠詳細フレーム
        self.attendance_frame = ttk.Frame(self.correction_detail_frame)
        self.setup_attendance_details()
        
        # 成績詳細フレーム
        self.grade_frame = ttk.Frame(self.correction_detail_frame)
        self.setup_grade_details()
        
        # 初期表示は出欠
        self.attendance_frame.pack(fill=tk.BOTH, expand=True)
    
    def setup_attendance_details(self):
        """出欠詳細入力"""
        # 日付入力（DateEntryカレンダー使用）
        date_frame = ttk.Frame(self.attendance_frame)
        date_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(date_frame, text="日付:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.attendance_date = DateEntry(date_frame, bootstyle="primary", dateformat='%Y-%m-%d')
        self.attendance_date.pack(side=tk.LEFT)
        
        # 時限選択（チェックボックスグリッド）
        period_label = ttk.Label(self.attendance_frame, text="時限（複数選択可）:", font=('Arial', 9))
        period_label.pack(anchor=tk.W, pady=(5, 3))
        
        period_container = ttk.Frame(self.attendance_frame)
        period_container.pack(fill=tk.X)
        
        self.period_checkboxes = {}
        
        # 3行4列のグリッド
        for row in range(3):
            row_frame = ttk.Frame(period_container)
            row_frame.pack(fill=tk.X, pady=1)
            for col in range(4):
                period_num = row * 4 + col + 1
                if period_num <= 12:
                    var = tk.BooleanVar()
                    self.period_checkboxes[period_num] = var
                    cb = ttk.Checkbutton(row_frame, text=f"{period_num}限", variable=var)
                    cb.pack(side=tk.LEFT, padx=(0, 8))
        
        # 科目・講座名
        subject_frame = ttk.Frame(self.attendance_frame)
        subject_frame.pack(fill=tk.X, pady=(8, 5))
        
        ttk.Label(subject_frame, text="科目:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.subject_var = tk.StringVar()
        subject_combo = ttk.Combobox(subject_frame, textvariable=self.subject_var,
                                    font=('Arial', 9), width=12, state="readonly")
        subject_combo['values'] = ['国語', '数学', '英語', '理科', '社会', '体育', '音楽', '美術', '技術', '家庭', '情報', '総合']
        subject_combo.pack(side=tk.LEFT)
        
        course_frame = ttk.Frame(self.attendance_frame)
        course_frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(course_frame, text="講座名:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.course_name_var = tk.StringVar()
        ttk.Entry(course_frame, textvariable=self.course_name_var,
                 font=('Arial', 9), width=20).pack(side=tk.LEFT)
        
        # 変更内容
        change_frame = ttk.LabelFrame(self.attendance_frame, text="変更内容", padding=5)
        change_frame.pack(fill=tk.X, pady=(8, 5))
        
        change_row = ttk.Frame(change_frame)
        change_row.pack()
        
        ttk.Label(change_row, text="訂正前:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 3))
        self.before_status_var = tk.StringVar(value="欠席")
        before_combo = ttk.Combobox(change_row, textvariable=self.before_status_var,
                                   font=('Arial', 9), width=10, state="readonly")
        before_combo['values'] = ['出席', '欠席', '遅刻', '早退', '出席停止', '忌引']
        before_combo.pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Label(change_row, text="→", font=('Arial', 12, 'bold'), foreground='red').pack(side=tk.LEFT, padx=8)
        
        ttk.Label(change_row, text="訂正後:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 3))
        self.after_status_var = tk.StringVar(value="出席")
        after_combo = ttk.Combobox(change_row, textvariable=self.after_status_var,
                                  font=('Arial', 9), width=10, state="readonly")
        after_combo['values'] = ['出席', '欠席', '遅刻', '早退', '出席停止', '忌引']
        after_combo.pack(side=tk.LEFT)
        
        # 成績連動設定
        link_frame = ttk.LabelFrame(self.attendance_frame, text="成績への連動", padding=5)
        link_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.link_grade_var = tk.BooleanVar(value=True)
        self.link_observation_var = tk.BooleanVar(value=True)
        self.link_total_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(link_frame, text="評価評定に反映", variable=self.link_grade_var).pack(anchor=tk.W)
        ttk.Checkbutton(link_frame, text="観点別評価に反映", variable=self.link_observation_var).pack(anchor=tk.W)
        ttk.Checkbutton(link_frame, text="総合評価に反映", variable=self.link_total_var).pack(anchor=tk.W)
    
    def setup_grade_details(self):
        """成績詳細入力"""
        # 科目選択
        subject_frame = ttk.Frame(self.grade_frame)
        subject_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(subject_frame, text="科目:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.grade_subject_var = tk.StringVar()
        subject_combo = ttk.Combobox(subject_frame, textvariable=self.grade_subject_var,
                                    font=('Arial', 9), width=12, state="readonly")
        subject_combo['values'] = ['国語', '数学', '英語', '理科', '社会', '体育', '音楽', '美術', '技術', '家庭', '情報', '総合']
        subject_combo.pack(side=tk.LEFT)
        
        # 講座名
        course_frame = ttk.Frame(self.grade_frame)
        course_frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(course_frame, text="講座名:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.grade_course_name_var = tk.StringVar()
        ttk.Entry(course_frame, textvariable=self.grade_course_name_var,
                 font=('Arial', 9), width=20).pack(side=tk.LEFT)
        
        # 訂正項目
        items_frame = ttk.LabelFrame(self.grade_frame, text="訂正項目（複数選択可）", padding=5)
        items_frame.pack(fill=tk.X, pady=(8, 8))
        
        self.grade_evaluation_var = tk.BooleanVar()
        self.grade_observation_var = tk.BooleanVar()
        self.grade_total_var = tk.BooleanVar()
        
        ttk.Checkbutton(items_frame, text="評価評定", variable=self.grade_evaluation_var,
                       command=self.toggle_grade_items).pack(anchor=tk.W)
        ttk.Checkbutton(items_frame, text="観点別評価", variable=self.grade_observation_var,
                       command=self.toggle_grade_items).pack(anchor=tk.W)
        ttk.Checkbutton(items_frame, text="総合評価", variable=self.grade_total_var,
                       command=self.toggle_grade_items).pack(anchor=tk.W)
        
        # 評価評定の変更
        self.evaluation_frame = ttk.LabelFrame(self.grade_frame, text="評価評定の変更", padding=5)
        
        eval_row = ttk.Frame(self.evaluation_frame)
        eval_row.pack()
        
        ttk.Label(eval_row, text="訂正前:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 3))
        self.before_evaluation_var = tk.StringVar(value="3")
        ttk.Combobox(eval_row, textvariable=self.before_evaluation_var,
                    font=('Arial', 9), width=5, state="readonly",
                    values=['0', '1', '2', '3', '4', '5']).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Label(eval_row, text="→", font=('Arial', 12, 'bold'), foreground='red').pack(side=tk.LEFT, padx=8)
        
        ttk.Label(eval_row, text="訂正後:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 3))
        self.after_evaluation_var = tk.StringVar(value="4")
        ttk.Combobox(eval_row, textvariable=self.after_evaluation_var,
                    font=('Arial', 9), width=5, state="readonly",
                    values=['0', '1', '2', '3', '4', '5']).pack(side=tk.LEFT)
        
        ttk.Label(self.evaluation_frame, text="(0:評価なし, 1～5:評価)",
                 font=('Arial', 8), foreground='gray').pack(pady=(5, 0))
        
        # 観点別評価の変更
        self.observation_frame = ttk.LabelFrame(self.grade_frame, text="観点別評価の変更", padding=5)
        
        obs_row = ttk.Frame(self.observation_frame)
        obs_row.pack()
        
        ttk.Label(obs_row, text="訂正前:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 3))
        
        self.before_obs_vars = []
        for i in range(3):
            var = tk.StringVar(value="B")
            combo = ttk.Combobox(obs_row, textvariable=var, font=('Arial', 9), width=3, state="readonly",
                                values=['A', 'B', 'C'])
            combo.pack(side=tk.LEFT, padx=1)
            self.before_obs_vars.append(var)
        
        ttk.Label(obs_row, text="→", font=('Arial', 12, 'bold'), foreground='red').pack(side=tk.LEFT, padx=8)
        
        ttk.Label(obs_row, text="訂正後:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 3))
        
        self.after_obs_vars = []
        for i in range(3):
            var = tk.StringVar(value="A")
            combo = ttk.Combobox(obs_row, textvariable=var, font=('Arial', 9), width=3, state="readonly",
                                values=['A', 'B', 'C'])
            combo.pack(side=tk.LEFT, padx=1)
            self.after_obs_vars.append(var)
    
    def toggle_grade_items(self):
        """成績項目の表示切り替え"""
        if self.grade_evaluation_var.get():
            self.evaluation_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.evaluation_frame.pack_forget()
        
        if self.grade_observation_var.get():
            self.observation_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.observation_frame.pack_forget()
    
    def setup_period_section(self, parent):
        """対象期間セクション"""
        frame = ttk.LabelFrame(parent, text="5. 対象期間（複数選択可）", 
                              style='Section.TLabelframe', padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        periods = ['前期中間', '前期期末', '前期総合', '後期中間', 
                  '後期期末', '後期総合', '仮評定', '最終評定']
        
        self.period_vars = {}
        
        # 2行4列
        for row in range(2):
            row_frame = ttk.Frame(frame)
            row_frame.pack(fill=tk.X, pady=2)
            for col in range(4):
                idx = row * 4 + col
                if idx < len(periods):
                    var = tk.BooleanVar()
                    self.period_vars[periods[idx]] = var
                    cb = ttk.Checkbutton(row_frame, text=periods[idx], variable=var)
                    cb.pack(side=tk.LEFT, padx=(0, 10))
    
    def setup_buttons(self, parent):
        """ボタングループ"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=15, padx=5)
        
        ttk.Button(button_frame, text="プレビュー", 
                  command=self.show_preview,
                  style='primary.TButton', width=10).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="申請実行", 
                  command=self.submit_request,
                  style='success.TButton', width=10).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="クリア", 
                  command=self.clear_form,
                  style='warning.TButton', width=10).pack(side=tk.LEFT)
    
    def setup_right_panel(self, parent):
        """右側パネル - 履歴一覧表示（70%幅）"""
        # タイトル
        title_label = ttk.Label(parent, text="訂正申請履歴", style='Title.TLabel')
        title_label.pack(pady=(5, 8))
        
        # フィルタセクション
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill=tk.X, pady=(0, 8), padx=8)
        
        ttk.Label(filter_frame, text="フィルタ:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_filter = tk.StringVar(value="all")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter,
                                   font=('Arial', 9), width=10, state="readonly")
        status_combo['values'] = ['全て', '承認済', '処理中', '差戻し']
        status_combo.pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(filter_frame, text="更新", 
                  command=self.refresh_history, width=6).pack(side=tk.LEFT)
        
        # 履歴リスト
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        # スクロールバー
        scrollbar_y = ttk.Scrollbar(list_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 列定義
        columns = ('申請日', '時刻', '記入者', '組番号', '氏名', 
                  '種別', '科目', '講座名', '時限', '変更内容', '理由', '状態', '承認者')
        
        self.history_tree = ttk.Treeview(list_frame, columns=columns,
                                        show='tree headings',
                                        yscrollcommand=scrollbar_y.set,
                                        xscrollcommand=scrollbar_x.set)
        
        # カラム設定
        self.history_tree.heading('#0', text='ID')
        for col in columns:
            self.history_tree.heading(col, text=col)
        
        # カラム幅
        widths = {
            '#0': 40,
            '申請日': 80,
            '時刻': 60,
            '記入者': 80,
            '組番号': 70,
            '氏名': 90,
            '種別': 50,
            '科目': 60,
            '講座名': 120,
            '時限': 50,
            '変更内容': 120,
            '理由': 150,
            '状態': 60,
            '承認者': 80
        }
        
        for col, width in widths.items():
            self.history_tree.column(col, width=width)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.config(command=self.history_tree.yview)
        scrollbar_x.config(command=self.history_tree.xview)
        
        # ダブルクリックで詳細表示
        self.history_tree.bind('<Double-Button-1>', self.show_history_detail)
        
        # 初期データ読み込み
        self.refresh_history()
    
    def setup_admin_right_panel(self, parent):
        """管理者用右側パネル - 承認機能付き（70%幅）"""
        # タイトル
        title_label = ttk.Label(parent, text="訂正申請履歴（管理者モード）", style='Title.TLabel')
        title_label.pack(pady=(5, 8))
        
        # 上部：承認待ち一覧
        pending_frame = ttk.LabelFrame(parent, text="承認待ち申請", padding=5)
        pending_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 5))
        
        # 承認ボタンエリア
        approve_button_frame = ttk.Frame(pending_frame)
        approve_button_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(approve_button_frame, text="選択項目を承認", 
                  command=self.approve_selected,
                  style='success.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(approve_button_frame, text="選択項目を却下", 
                  command=self.reject_selected,
                  style='danger.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(approve_button_frame, text="詳細表示", 
                  command=self.show_pending_detail).pack(side=tk.LEFT)
        
        # 承認待ちリスト
        pending_list_frame = ttk.Frame(pending_frame)
        pending_list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(pending_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ('申請日', '記入者', '組番号', '氏名', '種別', '変更内容', '理由')
        
        self.pending_tree = ttk.Treeview(pending_list_frame, columns=columns,
                                        show='tree headings', height=10,
                                        yscrollcommand=scrollbar.set)
        
        self.pending_tree.heading('#0', text='ID')
        for col in columns:
            self.pending_tree.heading(col, text=col)
        
        widths = {'#0': 40, '申請日': 100, '記入者': 80, '組番号': 70, 
                 '氏名': 90, '種別': 50, '変更内容': 120, '理由': 200}
        for col, width in widths.items():
            self.pending_tree.column(col, width=width)
        
        self.pending_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.pending_tree.yview)
        
        # 下部：全履歴一覧
        history_frame = ttk.LabelFrame(parent, text="全申請履歴", padding=5)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(5, 8))
        
        # フィルタ
        filter_frame = ttk.Frame(history_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(filter_frame, text="フィルタ:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.status_filter = tk.StringVar(value="all")
        ttk.Combobox(filter_frame, textvariable=self.status_filter,
                    font=('Arial', 9), width=10, state="readonly",
                    values=['全て', '承認済', '処理中', '差戻し']).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(filter_frame, text="更新", 
                  command=self.refresh_all_lists, width=6).pack(side=tk.LEFT)
        
        # 全履歴リスト
        history_list_frame = ttk.Frame(history_frame)
        history_list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar2 = ttk.Scrollbar(history_list_frame)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_tree = ttk.Treeview(history_list_frame, columns=columns,
                                        show='tree headings',
                                        yscrollcommand=scrollbar2.set)
        
        self.history_tree.heading('#0', text='ID')
        for col in columns:
            self.history_tree.heading(col, text=col)
        
        for col, width in widths.items():
            self.history_tree.column(col, width=width)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.config(command=self.history_tree.yview)
        
        self.history_tree.bind('<Double-Button-1>', self.show_history_detail)
        
        # 初期データ読み込み
        self.refresh_all_lists()
    
    def approve_selected(self):
        """選択された申請を承認"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("選択エラー", "承認する申請を選択してください")
            return
        
        item = self.pending_tree.item(selection[0])
        request_id = item['text']
        
        if messagebox.askyesno("確認", f"申請ID {request_id} を承認しますか？"):
            cursor = self.db_manager.connect()
            
            try:
                cursor.execute('''
                    UPDATE correction_requests 
                    SET status = 'approved',
                        approved_date = CURRENT_TIMESTAMP,
                        approver_name = ?,
                        approver_id = ?
                    WHERE request_id = ?
                ''', (
                    self.current_user['name'],
                    self.current_user.get('id'),
                    request_id
                ))
                
                self.db_manager.connection.commit()
                messagebox.showinfo("成功", "申請を承認しました")
                self.refresh_all_lists()
                
            except Exception as e:
                self.db_manager.connection.rollback()
                messagebox.showerror("エラー", f"承認処理に失敗しました: {str(e)}")
            
            finally:
                self.db_manager.close()
    
    def reject_selected(self):
        """選択された申請を却下"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("選択エラー", "却下する申請を選択してください")
            return
        
        item = self.pending_tree.item(selection[0])
        request_id = item['text']
        
        # 却下理由入力ダイアログ
        reason = simpledialog.askstring("却下理由", "却下理由を入力してください:")
        
        if reason:
            cursor = self.db_manager.connect()
            
            try:
                cursor.execute('''
                    UPDATE correction_requests 
                    SET status = 'rejected',
                        rejection_reason = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE request_id = ?
                ''', (reason, request_id))
                
                self.db_manager.connection.commit()
                messagebox.showinfo("成功", "申請を却下しました")
                self.refresh_all_lists()
                
            except Exception as e:
                self.db_manager.connection.rollback()
                messagebox.showerror("エラー", f"却下処理に失敗しました: {str(e)}")
            
            finally:
                self.db_manager.close()
    
    def show_pending_detail(self):
        """承認待ち申請の詳細表示"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("選択エラー", "表示する申請を選択してください")
            return
        
        item = self.pending_tree.item(selection[0])
        request_id = item['text']
        self.show_request_detail(request_id)
    
    def refresh_all_lists(self):
        """管理者用：全リストを更新"""
        # 承認待ちリストを更新
        for item in self.pending_tree.get_children():
            self.pending_tree.delete(item)
        
        cursor = self.db_manager.connect()
        
        # 承認待ち申請を取得
        cursor.execute('''
            SELECT 
                r.request_id,
                r.request_date,
                r.applicant_name,
                t.student_number,
                t.student_name,
                r.correction_type,
                r.reason,
                CASE 
                    WHEN r.correction_type = 'attendance' THEN
                        (SELECT a.before_status || '→' || a.after_status
                         FROM attendance_corrections a
                         WHERE a.target_id = t.target_id LIMIT 1)
                    ELSE
                        (SELECT 
                            CASE 
                                WHEN g.before_evaluation IS NOT NULL THEN
                                    '評価:' || g.before_evaluation || '→' || g.after_evaluation
                                ELSE
                                    '観点:' || g.before_observation || '→' || g.after_observation
                            END
                         FROM grade_corrections g
                         WHERE g.target_id = t.target_id LIMIT 1)
                END as change_detail
            FROM correction_requests r
            LEFT JOIN correction_targets t ON r.request_id = t.request_id
            WHERE r.status = 'pending'
            ORDER BY r.request_date DESC
        ''')
        
        for row in cursor.fetchall():
            type_map = {'attendance': '出欠', 'grade': '成績'}
            date_str = row['request_date'][:10] if row['request_date'] else ''
            reason_short = row['reason'][:30] + '...' if len(row['reason'] or '') > 30 else row['reason']
            
            self.pending_tree.insert('', 'end', 
                                    text=row['request_id'],
                                    values=(
                                        date_str,
                                        row['applicant_name'] or '',
                                        row['student_number'] or '',
                                        row['student_name'] or '',
                                        type_map.get(row['correction_type'], ''),
                                        row['change_detail'] or '',
                                        reason_short or ''
                                    ))
        
        self.db_manager.close()
        
        # 全履歴リストも更新
        self.refresh_history()
    
    def toggle_target_type(self):
        """対象者タイプの切り替え"""
        if self.target_type_var.get() == "individual":
            self.multiple_frame.pack_forget()
            self.individual_frame.pack(fill=tk.X, pady=(8, 0))
        else:
            self.individual_frame.pack_forget()
            self.multiple_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
    
    def toggle_correction_type(self):
        """訂正種別の切り替え"""
        if self.correction_type_var.get() == "attendance":
            self.grade_frame.pack_forget()
            self.attendance_frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.attendance_frame.pack_forget()
            self.grade_frame.pack(fill=tk.BOTH, expand=True)
            self.toggle_grade_items()
    
    def show_preview(self):
        """プレビュー表示"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("訂正内容確認")
        preview_window.geometry("700x500")
        
        preview_text = tk.Text(preview_window, wrap=tk.WORD, font=('Arial', 10))
        preview_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        content = self.generate_preview_content()
        preview_text.insert(1.0, content)
        preview_text.config(state=tk.DISABLED)
        
        button_frame = ttk.Frame(preview_window)
        button_frame.pack(pady=8)
        
        ttk.Button(button_frame, text="この内容で申請", 
                  command=lambda: self.submit_from_preview(preview_window),
                  style='success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="修正する", 
                  command=preview_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def generate_preview_content(self):
        """プレビュー内容を生成"""
        content = "=" * 60 + "\n"
        content += "成績訂正申請内容\n"
        content += "=" * 60 + "\n\n"
        
        content += f"記入者: {self.applicant_name_var.get()}\n"
        content += f"申請日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        content += f"訂正理由:\n{self.reason_text.get(1.0, tk.END).strip()}\n\n"
        
        if self.target_type_var.get() == "individual":
            content += f"対象者: {self.student_number_var.get()} {self.student_name_var.get()}\n\n"
        else:
            content += "対象者（複数）:\n"
            for num, name in self.student_entries:
                if num.get() and name.get():
                    content += f"  {num.get()} {name.get()}\n"
            content += "\n"
        
        content += f"訂正種別: {'出欠関連' if self.correction_type_var.get() == 'attendance' else '成績のみ'}\n\n"
        
        if self.correction_type_var.get() == "attendance":
            content += f"日付: {self.attendance_date.entry.get()}\n"
            
            selected_periods = []
            for period, var in self.period_checkboxes.items():
                if var.get():
                    selected_periods.append(str(period))
            
            content += f"時限: {', '.join(selected_periods)}限\n"
            content += f"科目: {self.subject_var.get()}\n"
            content += f"講座名: {self.course_name_var.get()}\n"
            content += f"変更: {self.before_status_var.get()} → {self.after_status_var.get()}\n\n"
            
            content += "成績連動:\n"
            if self.link_grade_var.get():
                content += "  ✓ 評価評定に反映\n"
            if self.link_observation_var.get():
                content += "  ✓ 観点別評価に反映\n"
            if self.link_total_var.get():
                content += "  ✓ 総合評価に反映\n"
        else:
            content += f"科目: {self.grade_subject_var.get()}\n"
            content += f"講座名: {self.grade_course_name_var.get()}\n\n"
            
            if self.grade_evaluation_var.get():
                content += f"評価評定: {self.before_evaluation_var.get()} → {self.after_evaluation_var.get()}\n"
            
            if self.grade_observation_var.get():
                before_obs = ''.join([v.get() for v in self.before_obs_vars])
                after_obs = ''.join([v.get() for v in self.after_obs_vars])
                content += f"観点別評価: {before_obs} → {after_obs}\n"
        
        content += "\n対象期間:\n"
        for period, var in self.period_vars.items():
            if var.get():
                content += f"  ✓ {period}\n"
        
        return content
    
    def submit_from_preview(self, preview_window):
        """プレビューから申請実行"""
        preview_window.destroy()
        self.submit_request()
    
    def clear_form(self):
        """フォームクリア"""
        if messagebox.askyesno("確認", "入力内容をクリアしますか？"):
            self.reason_text.delete(1.0, tk.END)
            self.student_number_var.set("")
            self.student_name_var.set("")
            self.attendance_date.entry.delete(0, tk.END)
            self.attendance_date.entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
            self.subject_var.set("")
            self.course_name_var.set("")
            self.grade_subject_var.set("")
            self.grade_course_name_var.set("")
            
            for var in self.period_vars.values():
                var.set(False)
            for var in self.period_checkboxes.values():
                var.set(False)
            
            self.target_type_var.set("individual")
            self.correction_type_var.set("attendance")
            
            self.toggle_target_type()
            self.toggle_correction_type()
    
    def submit_request(self):
        """申請送信"""
        if not self.validate_form():
            return
        
        form_data = self.collect_form_data()
        system_info = self.system_info.get_info()
        
        result = self.db_manager.save_correction_request(form_data, system_info)
        
        if result['success']:
            messagebox.showinfo("成功", f"申請を送信しました。\n申請ID: {result['request_id']}")
            self.clear_form()
            if hasattr(self, 'refresh_all_lists'):
                self.refresh_all_lists()
            else:
                self.refresh_history()
        else:
            messagebox.showerror("エラー", f"申請の送信に失敗しました。\n{result['error']}")
    
    def validate_form(self):
        """フォームバリデーション"""
        errors = []
        
        if not self.applicant_name_var.get():
            errors.append("記入者名を入力してください")
        
        if not self.reason_text.get(1.0, tk.END).strip():
            errors.append("訂正理由を入力してください")
        
        if self.target_type_var.get() == "individual":
            if not self.student_number_var.get():
                errors.append("組番号を入力してください")
            elif not re.match(r'^[A-Za-z][0-9]{4}$', self.student_number_var.get()):
                errors.append("組番号は「アルファベット1文字+4桁数字」の形式で入力してください（例: F1234）")
            if not self.student_name_var.get():
                errors.append("氏名を入力してください")
        
        if not any(var.get() for var in self.period_vars.values()):
            errors.append("対象期間を選択してください")
        
        if errors:
            messagebox.showerror("入力エラー", "\n".join(errors))
            return False
        
        return True
    
    def collect_form_data(self):
        """フォームデータを収集"""
        form_data = {
            'applicant_name': self.applicant_name_var.get(),
            'applicant_id': self.current_user.get('id'),
            'reason': self.reason_text.get(1.0, tk.END).strip(),
            'correction_type': self.correction_type_var.get(),
            'students': [],
            'periods': [period for period, var in self.period_vars.items() if var.get()]
        }
        
        if self.target_type_var.get() == "individual":
            form_data['students'] = [{
                'number': self.student_number_var.get(),
                'name': self.student_name_var.get()
            }]
        else:
            form_data['students'] = [
                {'number': num.get(), 'name': name.get()}
                for num, name in self.student_entries
                if num.get() and name.get()
            ]
        
        if self.correction_type_var.get() == "attendance":
            selected_periods = []
            for period, var in self.period_checkboxes.items():
                if var.get():
                    selected_periods.append(str(period))
            
            form_data['attendance'] = {
                'date': self.attendance_date.entry.get(),
                'period': ','.join(selected_periods),
                'subject': self.subject_var.get(),
                'course_name': self.course_name_var.get(),
                'before_status': self.before_status_var.get(),
                'after_status': self.after_status_var.get(),
                'link_to_grade': self.link_grade_var.get(),
                'link_to_observation': self.link_observation_var.get(),
                'link_to_total': self.link_total_var.get()
            }
        else:
            form_data['grade'] = {
                'subject': self.grade_subject_var.get(),
                'course_name': self.grade_course_name_var.get(),
                'correction_item': self.get_correction_items()
            }
            
            if self.grade_evaluation_var.get():
                form_data['grade']['before_evaluation'] = self.before_evaluation_var.get()
                form_data['grade']['after_evaluation'] = self.after_evaluation_var.get()
            
            if self.grade_observation_var.get():
                form_data['grade']['before_observation'] = ''.join([v.get() for v in self.before_obs_vars])
                form_data['grade']['after_observation'] = ''.join([v.get() for v in self.after_obs_vars])
        
        return form_data
    
    def get_correction_items(self):
        """選択された訂正項目を取得"""
        items = []
        if self.grade_evaluation_var.get():
            items.append('evaluation')
        if self.grade_observation_var.get():
            items.append('observation')
        if self.grade_total_var.get():
            items.append('total')
        return ','.join(items)
    
    def refresh_history(self):
        """履歴リストを更新"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        cursor = self.db_manager.connect()
        
        cursor.execute('''
            SELECT 
                r.request_id,
                r.request_date,
                r.applicant_name,
                t.student_number,
                t.student_name,
                r.correction_type,
                r.status,
                r.approver_name,
                r.reason,
                CASE 
                    WHEN r.correction_type = 'attendance' THEN a.subject
                    ELSE ''
                END as subject,
                CASE 
                    WHEN r.correction_type = 'attendance' THEN a.course_name
                    ELSE g.course_name
                END as course_name,
                CASE 
                    WHEN r.correction_type = 'attendance' THEN a.period_number
                    ELSE ''
                END as period,
                CASE 
                    WHEN r.correction_type = 'attendance' THEN
                        a.before_status || '→' || a.after_status
                    ELSE
                        CASE 
                            WHEN g.before_evaluation IS NOT NULL THEN
                                '評価:' || g.before_evaluation || '→' || g.after_evaluation
                            ELSE
                                '観点:' || g.before_observation || '→' || g.after_observation
                        END
                END as change_detail
            FROM correction_requests r
            LEFT JOIN correction_targets t ON r.request_id = t.request_id
            LEFT JOIN attendance_corrections a ON t.target_id = a.target_id
            LEFT JOIN grade_corrections g ON t.target_id = g.target_id
            ORDER BY r.request_date DESC
            LIMIT 200
        ''')
        
        for row in cursor.fetchall():
            status_map = {'pending': '処理中', 'approved': '承認済', 'rejected': '差戻し'}
            type_map = {'attendance': '出欠', 'grade': '成績'}
            
            if row['request_date']:
                date_parts = row['request_date'].split(' ')
                date_str = date_parts[0] if len(date_parts) > 0 else ''
                time_str = date_parts[1][:5] if len(date_parts) > 1 else ''
            else:
                date_str = ''
                time_str = ''
            
            reason_short = row['reason'][:30] + '...' if len(row['reason'] or '') > 30 else row['reason']
            
            self.history_tree.insert('', 'end', 
                                    text=row['request_id'],
                                    values=(
                                        date_str,
                                        time_str,
                                        row['applicant_name'] or '',
                                        row['student_number'] or '',
                                        row['student_name'] or '',
                                        type_map.get(row['correction_type'], ''),
                                        row['subject'] or '',
                                        row['course_name'] or '',
                                        row['period'] + '限' if row['period'] else '',
                                        row['change_detail'] or '',
                                        reason_short or '',
                                        status_map.get(row['status'], ''),
                                        row['approver_name'] or ''
                                    ))
        
        self.db_manager.close()
    
    def show_request_detail(self, request_id):
        """申請詳細を表示"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"申請詳細 - ID: {request_id}")
        detail_window.geometry("800x600")
        
        detail_text = tk.Text(detail_window, wrap=tk.WORD, font=('Arial', 10))
        detail_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        cursor = self.db_manager.connect()
        cursor.execute('SELECT * FROM correction_requests WHERE request_id = ?', (request_id,))
        request = cursor.fetchone()
        
        if request:
            details = f"""
================================================================================
申請詳細情報
================================================================================

【基本情報】
申請ID: {request['request_id']}
申請日時: {request['request_date']}
記入者: {request['applicant_name']}
ステータス: {request['status']}

【訂正理由】
{request['reason']}
"""
            detail_text.insert(1.0, details)
            detail_text.config(state=tk.DISABLED)
        
        self.db_manager.close()
        
        ttk.Button(detail_window, text="閉じる", 
                  command=detail_window.destroy).pack(pady=8)
    
    def show_history_detail(self, event):
        """履歴の詳細を表示"""
        selection = self.history_tree.selection()
        if not selection:
            return
        
        item = self.history_tree.item(selection[0])
        request_id = item['text']
        self.show_request_detail(request_id)