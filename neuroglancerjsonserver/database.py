import os
from google.cloud import datastore
import datetime
import zlib
import mysql.connector
import pytz
from neuroglancerjsonserver import migration

HOME = os.path.expanduser('~')

# Setting environment wide credential path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
           HOME + "/.cloudvolume/secrets/google-secret.json"
import json


class JsonDataBase(object):
    def __init__(self, project_id="neuromancer-seung-import",
                 client=None, credentials=None):
        if client is not None:
            self._client = client
        else:
            self._client = datastore.Client(project=project_id,
                                            credentials=credentials)

    @property
    def client(self):
        return self._client

    @property
    def namespace(self):
        return 'neuroglancerjsondb'

    @property
    def kind(self):
        return "ngl_json"

    @property
    def json_column(self):
        return 'json_graphene_v1'

    @property
    def json_col_history(self):
        return "json", 'json_graphene_v1'

    def add_json(self, json_data):
        key = self.client.key(self.kind, namespace=self.namespace)
        entity = datastore.Entity(key,
                                  exclude_from_indexes=self.json_col_history)

        json_data = migration.convert_precomputed_to_graphene_v1(json_data)
        json_data = str.encode(json_data)

        entity[self.json_column] = zlib.compress(json_data)
        entity['access_counter'] = int(1)

        now = datetime.datetime.utcnow()
        entity['date'] = now
        entity["date_last"] = now

        self.client.put(entity)

        return entity.key.id

    def get_json(self, json_id, decompress=True):
        key = self.client.key(self.kind, json_id, namespace=self.namespace)

        entity = self.client.get(key)

        # Handle data migration to newer formats
        if self.json_column in entity.keys():
            json_data = entity.get(self.json_column)
        else:
            # Handles migration from almost precomputed (json) to first
            # graphene format (json_graphene_v1)

            assert self.json_column == 'json_graphene_v1'

            entity.exclude_from_indexes.add(self.json_column)

            json_data = zlib.decompress(entity.get("json"))

            json_data = migration.convert_precomputed_to_graphene_v1(json_data)
            json_data = str.encode(json_data)
            json_data = zlib.compress(json_data)

            entity[self.json_column] = json_data

        if decompress:
            json_data = zlib.decompress(json_data)

        if 'access_counter' in entity:
            entity['access_counter'] += int(1)
        else:
            entity['access_counter'] = int(2)

        entity["date_last"] = datetime.datetime.utcnow()

        self.client.put(entity)

        return json_data




class JsonDataBaseMySQL(object):
    # 注意，数据库事先已经创建好
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


# 创建sql的脚本
# import mysql.connector
#
# def create_table():
#     connection = mysql.connector.connect(
#         host='localhost',
#         user='root',
#         password='root',
#         database='neuroglancerjsondb'
#     )
#
#     cursor = connection.cursor()
#
#     table_name = 'jsons'
#
#     # 创建表的 SQL 语句
#     create_table_query = f"""
#     CREATE TABLE IF NOT EXISTS {table_name} (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         json_column LONGBLOB,
#         access_counter INT,
#         date DATETIME,
#         date_last DATETIME
#     )
#     """
#
#     # 执行创建表的 SQL 语句
#     cursor.execute(create_table_query)
#
#     connection.commit()
#
#     cursor.close()
#     connection.close()
#
# # 调用函数创建表
# create_table()
