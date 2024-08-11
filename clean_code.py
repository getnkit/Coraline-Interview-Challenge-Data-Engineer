### Import to PostgreSQL ###

import psycopg2
import pandas as pd
import configparser
from psycopg2 import sql
from datetime import datetime

### ฟังก์ชันสำหรับเชื่อมต่อกับฐานข้อมูล โดยใช้การตั้งค่าที่ได้จากไฟล์ config
def connect_to_db(config):
    return psycopg2.connect(
        database=config.get('database', 'database'),
        user=config.get('database', 'user'),
        password=config.get('database', 'password'),
        host=config.get('database', 'host'),
        port=config.get('database', 'port')
    )

### ฟังก์ชันสำหรับโหลดข้อมูลจากไฟล์ Excel
def load_excel_data(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
    return df

### ฟังก์ชันสำหรับประมวลผลข้อมูลจาก DataFrame
def process_data(df, column_names):
    if not all(col in df.columns for col in column_names):
        raise ValueError("Not all expected columns are present in the Excel sheet.")
    
    df = df[column_names]
    df = df.dropna()

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df[df['Date'].notna()]

    data = df.values.tolist()
    return data

### ฟังก์ชันสำหรับสร้างตารางในฐานข้อมูล
def create_table(cursor, schema_name, table_name, column_names):
    schema_creation_query = sql.SQL('CREATE SCHEMA IF NOT EXISTS {}').format(sql.Identifier(schema_name))
    cursor.execute(schema_creation_query)

    drop_table_query = sql.SQL('DROP TABLE IF EXISTS {}.{}').format(
        sql.Identifier(schema_name),
        sql.Identifier(table_name)
    )
    cursor.execute(drop_table_query)

    columns_definitions = ', '.join([f'"{name}" TEXT' for name in column_names])
    table_creation_query = sql.SQL("""
        CREATE TABLE {}.{} ({})
    """).format(
        sql.Identifier(schema_name),
        sql.Identifier(table_name),
        sql.SQL(columns_definitions)
    )
    cursor.execute(table_creation_query)

### ฟังก์ชันสำหรับแทรกข้อมูลลงในตาราง
def insert_data(cursor, schema_name, table_name, column_names, data):
    insert_data_query = sql.SQL("""
       INSERT INTO {}.{} ({})
       VALUES ({})
    """).format(
        sql.Identifier(schema_name),
        sql.Identifier(table_name),
        sql.SQL(', ').join(map(sql.Identifier, column_names)),
        sql.SQL(', ').join([sql.Placeholder()] * len(column_names))
    )

    processed_data = [
        [
            item.strftime('%Y-%m-%d %H:%M:%S') if isinstance(item, datetime) else
            round(item, 2) if isinstance(item, float) else
            item
            for item in row
        ]
        for row in data
    ]
    cursor.executemany(insert_data_query, processed_data)

### ฟังก์ชันหลักที่รวมทุกขั้นตอน
def main():
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        connection = connect_to_db(config)
        print("Connected to database:", connection.dsn)

        cursor = connection.cursor()

        file_path = r'C:\Users\DELL\Coraline-Interview-Challenge-Data-Engineer\[For candidate] de_challenge_data.xlsx'
        sheet_name = 'FoodSales'
        
        df = load_excel_data(file_path, sheet_name)

        expected_columns = ['ID', 'Date', 'Region', 'City', 'Category', 'Product', 'Qty', 'UnitPrice', 'TotalPrice']
        actual_columns = df.columns.tolist()
        column_mapping = dict(zip(actual_columns, expected_columns))
        
        print("Actual column names:", actual_columns)
        print("Column mapping:", column_mapping)

        if not all(col in actual_columns for col in expected_columns):
            raise ValueError("Not all expected columns are present in the Excel sheet.")

        data = process_data(df, expected_columns)

        schema_name = 'public'
        table_name = 'food_sales'
        
        create_table(cursor, schema_name, table_name, expected_columns)
        insert_data(cursor, schema_name, table_name, expected_columns, data)

        connection.commit()
        print('Import successfully completed!')

    except Exception as e:
        print(f"An error occurred: {e}")
        if connection:
            connection.rollback()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

### เรียกใช้งานฟังก์ชันหลักเมื่อรันสคริปต์
if __name__ == "__main__":
    main()
