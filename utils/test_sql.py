# 测试数据库是否能正确解析json文件
# Test whether the database can correctly parse JSON files.
import json
import unittest
from utils.database import JsonDataBaseMySQL, JsonDataBaseSQLite
import os

# MySQL要求本地开启了mysql server 详情请看database.py
class JsonDataBaseMySQLTest(unittest.TestCase):
    def setUp(self):
        self.db = JsonDataBaseMySQL(
            host='localhost',
            user='root',
            password='root',
            database='neuroglancerjsondb'
        )

    def tearDown(self):
        self.db.connection.close()

    def test_add_json_and_get_json(self):
        # 添加 JSON 数据
        # 从文件中读取 JSON 数据
        file_path = os.path.join(os.getcwd(), 'utils/demo.json')
        with open(file_path, 'r') as file:
            json_data = json.load(file)  # dict

        json_id = self.db.add_json(json_data)

        print(json_data)  # dict
        # 获取 JSON 数据
        retrieved_json_data = self.db.get_json(json_id)
        print(retrieved_json_data)
        # 验证 JSON 数据是否一致
        self.assertEqual(json_data, json.loads(retrieved_json_data))

# 用SQLite的话 可以连同本地文件一起打包了
# If you use SQLite, you can package it with local files #
class JsonDataBaseSQLiteT(unittest.TestCase):
    def setUp(self):
        self.db = JsonDataBaseSQLite()

    def tearDown(self):
        self.db.connection.close()

    def test_add_json_and_get_json(self):
        # 添加 JSON 数据
        # 从文件中读取 JSON 数据
        file_path = os.path.join(os.getcwd(), 'utils/demo.json')
        with open(file_path, 'r') as file:
            json_data = json.load(file)  # dict

        json_id = self.db.add_json(json_data)

        print(json_data)  # dict
        # 获取 JSON 数据
        retrieved_json_data = self.db.get_json(json_id)
        print(retrieved_json_data)
        # 验证 JSON 数据是否一致
        self.assertEqual(json_data, json.loads(retrieved_json_data))