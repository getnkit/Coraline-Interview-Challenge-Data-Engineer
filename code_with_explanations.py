### Import to PostgreSQL ###

import psycopg2  # ใช้เชื่อมต่อกับฐานข้อมูล PostgreSQL
import pandas as pd  # ใช้สำหรับจัดการข้อมูลในไฟล์ Excel
import configparser  # ใช้อ่านไฟล์ config
from psycopg2 import sql  # ใช้จัดการคำสั่ง SQL
from datetime import datetime  # ใช้จัดการวันและเวลา

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
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)  # ใช้แถวที่สองเป็นหัวตาราง
    return df

### ฟังก์ชันสำหรับประมวลผลข้อมูลจาก DataFrame
def process_data(df, column_names):
    # ตรวจสอบว่ามีคอลัมน์ที่คาดหวังทั้งหมดอยู่ใน DataFrame ไหม
    if not all(col in df.columns for col in column_names):
        raise ValueError("Not all expected columns are present in the Excel sheet.")

    # เลือกเฉพาะคอลัมน์ที่ต้องการ
    df = df[column_names]

    # กรองแถวที่มีค่า NaN ออก
    df = df.dropna()

    # ตรวจสอบคอลัมน์ 'Date' ว่ามีข้อมูลชนิด datetime
    if 'Date' in df.columns:
        # แปลงคอลัมน์ 'Date' เป็นชนิด datetime ถ้ายังไม่เป็น
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # กรองเฉพาะแถวที่มีค่า 'Date' เป็นชนิด datetime
        df = df[df['Date'].notna()]

    # แปลงข้อมูลเป็นลิสต์
    data = df.values.tolist()

    return data

### ฟังก์ชันสำหรับสร้างตารางในฐานข้อมูล
def create_table(cursor, schema_name, table_name, column_names):
    # ใช้คำสั่ง SQL สร้าง schema ใหม่ (ถ้าไม่มี)
    schema_creation_query = sql.SQL('CREATE SCHEMA IF NOT EXISTS {}').format(sql.Identifier(schema_name))
    # ใช้ cursor.execute เพื่อ execute คำสั่ง SQL
    cursor.execute(schema_creation_query)

    # ใช้คำสั่ง SQL ลบตารางที่มีอยู่ (ถ้ามี) เพื่อป้องกัน error ในระหว่างการทดสอบโค้ด
    drop_table_query = sql.SQL('DROP TABLE IF EXISTS {}.{}').format(
        sql.Identifier(schema_name),  # แทนที่ {} ด้วยชื่อ schema
        sql.Identifier(table_name)    # แทนที่ {} ด้วยชื่อของตาราง
    )
    cursor.execute(drop_table_query)

    # กำหนด definitions ของคอลัมน์ในตารางโดยใช้ข้อมูลที่ระบุใน column_names
    columns_definitions = ', '.join([f'"{name}" TEXT' for name in column_names])
    # ใช้คำสั่ง SQL สร้างตารางโดยใช้ schema, table_name และ columns_definitions
    table_creation_query = sql.SQL("""
        CREATE TABLE {}.{} ({})
    """).format(
        sql.Identifier(schema_name),  # แทนที่ {} ด้วยชื่อ schema 
        sql.Identifier(table_name),   # แทนที่ {} ด้วยชื่อของตาราง
        sql.SQL(columns_definitions)  # แทนที่ {} ด้วย definitions ของคอลัมน์
    )
    cursor.execute(table_creation_query)

### ฟังก์ชันสำหรับแทรกข้อมูลลงในตาราง
def insert_data(cursor, schema_name, table_name, column_names, data):
    # ใช้คำสั่ง SQL เพื่อแทรกข้อมูล
    insert_data_query = sql.SQL("""
       INSERT INTO {}.{} ({})
       VALUES ({})
    """).format(
        # ใช้ schema_name และ table_name เพื่อระบุฐานข้อมูลและตารางที่ต้องการแทรกข้อมูล
        sql.Identifier(schema_name),
        sql.Identifier(table_name),
        # กำหนดชื่อคอลัมน์ที่ต้องการแทรกข้อมูลให้กับคำสั่ง SQL
        sql.SQL(', ').join(map(sql.Identifier, column_names)),
        # สร้างตัวแทน (placeholders) ที่จะถูกแทนที่ด้วยค่าจริงในระหว่างการ execute คำสั่ง SQL ให้เท่ากับจำนวนคอลัมน์ในตาราง
        # การสร้างตัวแทน (placeholders) นั้น เพื่อเพิ่มความปลอดภัย และยังสามารถป้องกัน SQL Injection ได้อีกด้วย
        sql.SQL(', ').join([sql.Placeholder()] * len(column_names))
    )

    # ประมวลผลข้อมูลเพื่อแปลงวัน เวลา และตัวเลข
    processed_data = [
        [
            # เช็คว่า item เป็นชนิดข้อมูล datetime ไหม ถ้าเป็น ให้แปลงเป็นสตริงในรูปแบบ 'YYYY-MM-DD HH:MM:SS' โดยใช้ฟังก์ชัน strftime
            item.strftime('%Y-%m-%d %H:%M:%S') if isinstance(item, datetime) else
            # เช็คว่า item เป็นชนิดข้อมูล float ไหม ถ้าเป็น ให้ทำการปัดเศษทศนิยมเป็น 2 ตำแหน่ง (เพื่อความเข้ากันได้กับฐานข้อมูล)
            round(item, 2) if isinstance(item, float) else
            # ถ้า item ไม่ใช่ datetime หรือ float ให้ใช้ค่า item แบบเดิม
            item
            for item in row
        ]
        for row in data
    ]
    cursor.executemany(insert_data_query, processed_data)  # แทรกข้อมูลทั้งหมดพร้อมกัน

### ฟังก์ชันหลักที่รวมทุกขั้นตอน
def main():
    try:
        # การตั้งค่าและการเชื่อมต่อ
        config = configparser.ConfigParser()  # สร้างอ็อบเจ็กต์ ConfigParser
        config.read('config.ini')  # อ่านไฟล์ config
        connection = connect_to_db(config)  # เชื่อมต่อกับฐานข้อมูลโดยใช้การตั้งค่าจากไฟล์ config
        print("Connected to database:", connection.dsn)

        cursor = connection.cursor()  # สร้าง cursor สำหรับทำงานกับฐานข้อมูล
        file_path = r'C:\Users\DELL\Coraline-Interview-Challenge-Data-Engineer\[For candidate] de_challenge_data.xlsx'
        sheet_name = 'FoodSales'
        
        # โหลดข้อมูลจากชีทในไฟล์ Excel ไปเก็บไว้ใน DataFrame
        df = load_excel_data(file_path, sheet_name)

        expected_columns = ['ID', 'Date', 'Region', 'City', 'Category', 'Product', 'Qty', 'UnitPrice', 'TotalPrice']
        # ดึงชื่อคอลัมน์จาก DataFrame
        actual_columns = df.columns.tolist()
        # Mapping ชื่อคอลัมน์ทั้งสอง ถ้าค่าไม่ตรงกัน ค่าเหล่านั้นจะไม่ถูกใช้ในการประมวลผลหรือแทรกข้อมูลลงในฐานข้อมูล
        column_mapping = dict(zip(actual_columns, expected_columns))
        print("Actual column names:", actual_columns)
        print("Column mapping:", column_mapping)

        # ตรวจสอบว่ามีชื่อคอลัมน์ไหม ถ้าไม่ ให้แสดงข้อความ error
        if not all(col in actual_columns for col in expected_columns):
            raise ValueError("Not all expected columns are present in the Excel sheet.")

        # ประมวลผลข้อมูลจาก DataFrame เพื่อเตรียมแทรกลงฐานข้อมูล
        data = process_data(df, expected_columns)

        # สร้างตารางและแทรกข้อมูล
        schema_name = 'public'
        table_name = 'food_sales'
        create_table(cursor, schema_name, table_name, expected_columns)
        insert_data(cursor, schema_name, table_name, expected_columns, data)

        # commit การเปลี่ยนแปลงในฐานข้อมูล เพื่อให้ข้อมูลถูกบันทึก
        connection.commit()
        print('Import successfully completed!')

    except Exception as e:
        print(f"An error occurred: {e}")  # แสดงข้อความ error (ถ้ามี)
        if connection:
            connection.rollback()  # ยกเลิกการเปลี่ยนแปลงทั้งหมดในกรณีที่เกิด error

    finally:
        if cursor:
            cursor.close()  # ปิด cursor
        if connection:
            connection.close()  # ปิดการเชื่อมต่อฐานข้อมูล

### เรียกใช้งานฟังก์ชันหลักเมื่อรันสคริปต์
if __name__ == "__main__":
    main()
