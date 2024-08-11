# Coraline-Interview-Challenge-Data-Engineer

**Candidate Name:** Tanakit Gittibahnpachaa (Get)

## Project Structure
```
Coraline-Interview-Challenge-Data-Engineer/
│
├── images/
│   ├── cat_reg_sql_execution_result.jpg
│   ├── python_source_code_execution_result.jpg
│   └── select_all_from_food_sales.jpg
│
├── README.md
│
├── [For Candidate] Challenge - DE.pdf
│
├── [For candidate] de_challenge_data.xlsx
│
├── config.ini
│
├── cat_reg.sql
│
├── clean_code.py
│
└── code_with_explanations.py
```

## Structure and Main Functions of Python Source code
โค้ดนี้ถูกออกแบบมาเพื่อนำเข้าข้อมูลจากไฟล์ Excel ไปยังฐานข้อมูล PostgreSQL โดยแบ่งออกเป็นฟังก์ชันย่อยต่างๆ ได้แก่
### Database Connection
ฟังก์ชัน ```connect_to_db``` ใช้ไลบรารี ```psycopg2``` เพื่อเชื่อมต่อกับฐานข้อมูล PostgreSQL โดยอ่านค่าการตั้งค่าจากไฟล์ config.ini
### Load Data from Excel File
ฟังก์ชัน ```load_excel_data``` ใช้ไลบรารี ```pandas``` เพื่ออ่านข้อมูลจากไฟล์ Excel และแปลงเป็น DataFrame
### Process Data
ฟังก์ชัน ```process_data``` ทำการตรวจสอบข้อมูล เช่น ตรวจสอบชื่อคอลัมน์, กรองข้อมูลที่ขาดหาย, และแปลงชนิดข้อมูลให้เหมาะสมก่อนนำไปใส่ในฐานข้อมูล
### Create Table in Database
ฟังก์ชัน ```create_table``` สร้างตารางในฐานข้อมูล โดยก่อนสร้างจะทำการลบตารางเก่าที่มีชื่อเดียวกันออก เพื่อป้องกัน error ในระหว่างการทดสอบโค้ด
### Insert Data into Table
ฟังก์ชัน ```insert_data``` แทรกข้อมูลจาก DataFrame ลงในตารางที่สร้างขึ้น โดยใช้คำสั่ง SQL เพื่อเพิ่มประสิทธิภาพและความปลอดภัย

## Project Results
### Python Source code Execution Result
![image](https://github.com/getnkit/Coraline-Interview-Challenge-Data-Engineer/blob/cba1e69c0c3b341bf844c02e8950ca6dec1fbf81/images/python_source_code_execution_result.jpg)
### SELECT * FROM food_sales;
![image](https://github.com/getnkit/Coraline-Interview-Challenge-Data-Engineer/blob/cba1e69c0c3b341bf844c02e8950ca6dec1fbf81/images/select_all_from_food_sales.jpg)
### cat_reg.sql Execution Result
![image](https://github.com/getnkit/Coraline-Interview-Challenge-Data-Engineer/blob/ce652096d12dc66762d93cbc779d0dd2f29493a7/images/cat_reg_sql_execution_result.jpg)




