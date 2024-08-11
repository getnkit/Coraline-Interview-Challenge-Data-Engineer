SELECT
    "Category",
    ROUND(SUM(CASE WHEN "Region" = 'East' THEN CAST("Qty" AS NUMERIC) * CAST("UnitPrice" AS NUMERIC) ELSE 0 END)) AS East,
    ROUND(SUM(CASE WHEN "Region" = 'West' THEN CAST("Qty" AS NUMERIC) * CAST("UnitPrice" AS NUMERIC) ELSE 0 END)) AS West,
    ROUND(SUM(CAST("Qty" AS NUMERIC) * CAST("UnitPrice" AS NUMERIC))) AS Grand_Total
FROM
    public.food_sales
GROUP BY
    "Category";

"""

ขั้นตอนการทำงานของโค้ดนี้:

1. เลือกข้อมูลจากตาราง public.food_sales
2. จัดกลุ่มข้อมูลตามคอลัมน์ Category
3. คำนวณยอดขายแยกตามภูมิภาค (East และ West) และยอดรวมทั้งหมด
4. ใช้ CASE WHEN เพื่อแยกการคำนวณสำหรับแต่ละภูมิภาค
5. ใช้ CAST เพื่อแปลงข้อมูลเป็นตัวเลข (NUMERIC)
6. ปัดเศษผลลัพธ์ด้วยฟังก์ชัน ROUND

ผลลัพธ์ที่ได้:

1. ยอดขายรวมของแต่ละหมวดหมู่ (Category) แยกตามภูมิภาค (East และ West)
2. ยอดขายรวมจากทั้ง 2 ภูมิภาค (East และ West)

"""