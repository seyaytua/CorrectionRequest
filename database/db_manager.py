# database/db_manager.py
import sqlite3
from datetime import datetime
import json
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path="grade_correction.db"):
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """データベース接続"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection.cursor()
    
    def close(self):
        """データベース切断"""
        if self.connection:
            self.connection.close()
    
    def initialize_database(self):
        """データベース初期化"""
        cursor = self.connect()
        
        # 1. 訂正申請マスタテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS correction_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                applicant_name VARCHAR(100) NOT NULL,
                applicant_id VARCHAR(50),
                reason TEXT NOT NULL,
                correction_type VARCHAR(20) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by_ip VARCHAR(45),
                created_by_hostname VARCHAR(255),
                created_by_user_agent TEXT,
                created_by_os VARCHAR(100),
                
                approved_date DATETIME,
                approver_name VARCHAR(100),
                approver_id VARCHAR(50),
                approved_by_ip VARCHAR(45),
                approved_by_hostname VARCHAR(255),
                approved_by_user_agent TEXT,
                approved_by_os VARCHAR(100),
                
                rejection_reason TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. 訂正対象者テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS correction_targets (
                target_id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                student_number VARCHAR(4) NOT NULL,
                student_name VARCHAR(100) NOT NULL,
                FOREIGN KEY (request_id) REFERENCES correction_requests(request_id)
            )
        ''')
        
        # 3. 出欠訂正詳細テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_corrections (
                correction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER NOT NULL,
                attendance_date DATE NOT NULL,
                period_number INTEGER NOT NULL,
                subject VARCHAR(50) NOT NULL,
                course_name VARCHAR(100) NOT NULL,
                before_status VARCHAR(20) NOT NULL,
                after_status VARCHAR(20) NOT NULL,
                link_to_grade BOOLEAN DEFAULT 1,
                link_to_observation BOOLEAN DEFAULT 1,
                link_to_total BOOLEAN DEFAULT 1,
                FOREIGN KEY (target_id) REFERENCES correction_targets(target_id)
            )
        ''')
        
        # 4. 成績訂正詳細テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grade_corrections (
                correction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER NOT NULL,
                course_name VARCHAR(100) NOT NULL,
                correction_item VARCHAR(20) NOT NULL,
                before_evaluation INTEGER,
                after_evaluation INTEGER,
                before_observation VARCHAR(3),
                after_observation VARCHAR(3),
                FOREIGN KEY (target_id) REFERENCES correction_targets(target_id)
            )
        ''')
        
        # 5. 対象期間テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS correction_periods (
                period_id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER NOT NULL,
                period_name VARCHAR(30) NOT NULL,
                FOREIGN KEY (target_id) REFERENCES correction_targets(target_id)
            )
        ''')
        
        # 6. 操作ログテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operation_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER,
                operation_type VARCHAR(50) NOT NULL,
                operator_name VARCHAR(100),
                operator_id VARCHAR(50),
                operation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                hostname VARCHAR(255),
                user_agent TEXT,
                os_info VARCHAR(100),
                details TEXT,
                FOREIGN KEY (request_id) REFERENCES correction_requests(request_id)
            )
        ''')
        
        # インデックス作成
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_request_status ON correction_requests(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_request_date ON correction_requests(request_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_number ON correction_targets(student_number)')
        
        self.connection.commit()
        self.close()
    
    def save_correction_request(self, form_data, system_info):
        """訂正申請を保存"""
        cursor = self.connect()
        
        try:
            # トランザクション開始
            self.connection.execute('BEGIN')
            
            # 1. 申請マスタ登録
            cursor.execute('''
                INSERT INTO correction_requests (
                    applicant_name, applicant_id, reason, correction_type,
                    created_by_ip, created_by_hostname, created_by_os
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                form_data['applicant_name'],
                form_data.get('applicant_id'),
                form_data['reason'],
                form_data['correction_type'],
                system_info['ip_address'],
                system_info['hostname'],
                system_info['os_info']
            ))
            
            request_id = cursor.lastrowid
            
            # 2. 操作ログ記録
            cursor.execute('''
                INSERT INTO operation_logs (
                    request_id, operation_type, operator_name, operator_id,
                    ip_address, hostname, os_info, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request_id,
                'create',
                form_data['applicant_name'],
                form_data.get('applicant_id'),
                system_info['ip_address'],
                system_info['hostname'],
                system_info['os_info'],
                json.dumps({'action': '新規申請作成', 'form_data': form_data})
            ))
            
            # 3. 対象者登録
            for student in form_data['students']:
                cursor.execute('''
                    INSERT INTO correction_targets (
                        request_id, student_number, student_name
                    ) VALUES (?, ?, ?)
                ''', (request_id, student['number'], student['name']))
                
                target_id = cursor.lastrowid
                
                # 4. 訂正種別に応じた詳細登録
                if form_data['correction_type'] == 'attendance':
                    attendance = form_data['attendance']
                    cursor.execute('''
                        INSERT INTO attendance_corrections (
                            target_id, attendance_date, period_number,
                            subject, course_name, before_status, after_status,
                            link_to_grade, link_to_observation, link_to_total
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        target_id,
                        attendance['date'],
                        attendance['period'],
                        attendance['subject'],
                        attendance['course_name'],
                        attendance['before_status'],
                        attendance['after_status'],
                        attendance.get('link_to_grade', True),
                        attendance.get('link_to_observation', True),
                        attendance.get('link_to_total', True)
                    ))
                else:
                    grade = form_data['grade']
                    cursor.execute('''
                        INSERT INTO grade_corrections (
                            target_id, course_name, correction_item,
                            before_evaluation, after_evaluation,
                            before_observation, after_observation
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        target_id,
                        grade['course_name'],
                        grade['correction_item'],
                        grade.get('before_evaluation'),
                        grade.get('after_evaluation'),
                        grade.get('before_observation'),
                        grade.get('after_observation')
                    ))
                
                # 5. 対象期間登録
                for period in form_data['periods']:
                    cursor.execute('''
                        INSERT INTO correction_periods (
                            target_id, period_name
                        ) VALUES (?, ?)
                    ''', (target_id, period))
            
            # コミット
            self.connection.commit()
            return {'success': True, 'request_id': request_id}
            
        except Exception as e:
            # ロールバック
            self.connection.rollback()
            return {'success': False, 'error': str(e)}
        
        finally:
            self.close()