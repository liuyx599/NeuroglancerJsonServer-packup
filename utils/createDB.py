# 创建后端数据库的脚本
# Script for creating a backend database.
import mysql.connector
import sqlite3
import os

def create_table_Mysql():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='neuroglancerjsondb'
    )

    cursor = connection.cursor()

    table_name = 'jsons'

    # 创建表的 SQL 语句
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        json_column LONGBLOB,
        access_counter INT,
        date DATETIME,
        date_last DATETIME
    )
    """

    # 执行创建表的 SQL 语句
    cursor.execute(create_table_query)

    connection.commit()

    cursor.close()
    connection.close()


def create_table_sqlite(database='jsonserve.db'):

    current_directory = os.getcwd()
    database_path = os.path.join(current_directory, database)
    connection = sqlite3.connect(database_path)

    cursor = connection.cursor()

    table_name = 'jsons'

    # 检查表是否存在
    check_table_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    cursor.execute(check_table_query)
    table_exists = cursor.fetchone()

    if table_exists:
        # 清空表的 SQL 语句
        clear_table_query = f"DELETE FROM {table_name}"

        # 执行清空表的 SQL 语句
        cursor.execute(clear_table_query)
        connection.commit()

        # 重置自增计数器
        reset_counter_query = f"DELETE FROM sqlite_sequence WHERE name='{table_name}'"
        cursor.execute(reset_counter_query)
        connection.commit()


    # 创建表的 SQL 语句
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        json_column BLOB,
        access_counter INTEGER,
        date TEXT,
        date_last TEXT
    )
    """

    # 执行创建表的 SQL 语句
    cursor.execute(create_table_query)

    connection.commit()

    cursor.close()
    connection.close()


if __name__ == "__main__":
    create_table_sqlite()