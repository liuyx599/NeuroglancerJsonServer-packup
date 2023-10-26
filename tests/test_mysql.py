import json
import datetime
import zlib
import mysql.connector
import unittest
from neuroglancerjsonserver.database import JsonDataBaseMySQL
import os


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
        file_path = os.path.join(os.getcwd(), 'demo.json')
        with open(file_path, 'r') as file:
            json_data = json.load(file)  # dict

        json_id = self.db.add_json(json_data)

        print(json_data)  # dict
        # 获取 JSON 数据
        retrieved_json_data = self.db.get_json(json_id)
        print(retrieved_json_data)
        # 验证 JSON 数据是否一致
        self.assertEqual(json_data, json.loads(retrieved_json_data))
