import sqlite3
import os

working_dir = os.path.dirname(os.path.abspath(__file__))

class APIDatabase:
    def __init__(self, db_name=working_dir+'/api_storage.db'):
        print(db_name)
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # 创建用于存储 API 信息的表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_name TEXT NOT NULL,
                api_key TEXT,
                app_id TEXT,
                secret_key TEXT,
                base_url TEXT
            )
        ''')
        self.connection.commit()

    def insert_api_key(self, api_name, api_key=None, app_id=None, secret_key=None, base_url=None):
        # 插入新的 API 信息
        self.cursor.execute('''
            INSERT INTO api_keys (api_name, api_key, app_id, secret_key, base_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (api_name, api_key, app_id, secret_key, base_url))
        self.connection.commit()

    def get_api_key(self, api_name):
        # 根据 API 名称获取对应的 API 信息
        self.cursor.execute('''
            SELECT * FROM api_keys WHERE api_name = ?
        ''', (api_name,))
        return self.cursor.fetchone()

    def update_api_key(self, api_name, api_key=None, app_id=None, secret_key=None, base_url=None):
        # 更新已有的 API 信息
        self.cursor.execute('''
            UPDATE api_keys
            SET api_key = ?, app_id = ?, secret_key = ?, base_url = ?
            WHERE api_name = ?
        ''', (api_key, app_id, secret_key, base_url, api_name))
        self.connection.commit()

    def delete_api_key(self, api_name):
        # 删除指定 API 的信息
        self.cursor.execute('''
            DELETE FROM api_keys WHERE api_name = ?
        ''', (api_name,))
        self.connection.commit()

    def __del__(self):
        # 关闭数据库连接
        self.connection.close()


db = APIDatabase()
