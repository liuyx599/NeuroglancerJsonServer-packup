import os
import datetime
import zlib
import mysql.connector
import pytz
from . import migration
import sqlite3
HOME = os.path.expanduser('~')


class JsonDataBaseSQLite(object):
    def __init__(self, database='jsonserve.db', tablename='jsons'):
        # create_table_sqlite()
        current_directory = os.getcwd()
        database_path = os.path.join(current_directory, database)
        self._connection = sqlite3.connect(database_path)
        self._tablename = tablename

    @property
    def connection(self):
        return self._connection

    @property
    def tablename(self):
        return self._tablename

    def add_json(self, json_data):
        cursor = self.connection.cursor()

        json_data = migration.convert_precomputed_to_graphene_v1(json_data)  # dict->str
        json_data = str.encode(json_data)  # bytes
        json_data = zlib.compress(json_data)  # bytes

        access_counter = 1
        now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))

        cursor.execute(
            "INSERT INTO {} (json_column, access_counter, date, date_last) VALUES (?, ?, ?, ?)".format(self.tablename),
            (json_data, access_counter, now, now)
        )
        json_id = cursor.lastrowid  # 获取插入的行的ID

        self.connection.commit()
        cursor.close()

        return json_id


    def get_json(self, json_id, decompress=True):
        cursor = self.connection.cursor()

        # SQLite不支持%s占位符号  应该用?
        # SQLite doesn't support the %s placeholder symbol, it should use ?
        # cursor.execute(
        #     "SELECT json_column FROM {} WHERE id = %s".format(self.tablename),
        #     (json_id,)
        # )
        cursor.execute(
            f"SELECT json_column FROM {self.tablename} WHERE id = ?",
            (json_id,)
        )


        row = cursor.fetchone()

        if row:
            json_data = row[0]  # byte

            if decompress:
                json_data = zlib.decompress(json_data)

            # bytes -> str
            json_data = json_data.decode()

            now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))

            # 更新访问计数和最后访问时间
            cursor.execute(
                f"UPDATE {self.tablename} SET access_counter = access_counter + 1, date_last = ? WHERE id = ?",
                (now, json_id)
            )

            self.connection.commit()
            cursor.close()

            return json_data

        cursor.close()
        return None

class JsonDataBaseMySQL(object):
    # 注意，数据库事先已经创建好
    # Note that the database has been created beforehand
    def __init__(self, host='localhost', user='root', password='root', database='neuroglancerjsondb', tablename='jsons'):
        self._connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self._tablename = tablename

    @property
    def connection(self):
        return self._connection

    @property
    def tablename(self):
        return self._tablename


    def add_json(self, json_data):
        cursor = self.connection.cursor()

        json_data = migration.convert_precomputed_to_graphene_v1(json_data)  # dict->str
        json_data = str.encode(json_data)  # bytes
        json_data = zlib.compress(json_data)  # bytes

        access_counter = 1
        now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))

        cursor.execute(
            "INSERT INTO {} (json_column, access_counter, date, date_last) VALUES (%s, %s, %s, %s)".format(self.tablename),
            (json_data, access_counter, now, now)
        )
        json_id = cursor.lastrowid  # 获取插入的行的ID

        self.connection.commit()
        cursor.close()

        return json_id

    def get_json(self, json_id, decompress=True):
        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT json_column FROM {} WHERE id = %s".format(self.tablename),
            (json_id,)
        )
        row = cursor.fetchone()

        if row:    # 检查变量 row 是否存在数据。如果存在，表示找到了具有指定 ID 的 JSON 数据。
            json_data = row[0]  # byte

            if decompress:  # 先解压
                json_data = zlib.decompress(json_data)

            # bytes -> str
            json_data = json_data.decode()

            now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))

            # 更新访问计数和最后访问时间
            cursor.execute(
                "UPDATE {} SET access_counter = access_counter + 1, date_last = %s WHERE id = %s".format(self.tablename),
                (now, json_id)
            )

            self.connection.commit()
            cursor.close()

            return json_data

        cursor.close()
        return None
