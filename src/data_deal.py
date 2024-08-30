import csv

def process_population_data(input_file, output_file):
    data = []  # 存储有效的数据行
    header_processed = False  # 标记表头是否已被处理
    footer_found = False  # 标记表尾是否已找到

    # 读取文件
    with open(input_file, 'r', encoding='utf-8-sig') as file:  # 使用 utf-8-sig 处理带 BOM 的文件
        for line in file:
            stripped_line = line.strip()

            # 跳过表头
            if stripped_line.startswith(("数据库", "指标", "时间")):
                header_processed = True
                continue

            # 如果未找到表头，继续查找
            if not header_processed:
                continue

            # 跳过表尾
            if stripped_line.startswith("注"):
                footer_found = True
                break

            # 添加有效数据行
            data.append(stripped_line.split(','))

    # 写入CSV文件
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:  # 使用 utf-8-sig 以确保 Excel 正确识别
        writer = csv.writer(csvfile)
        writer.writerows(data)

    print(f"文件已成功生成：{output_file}")

# 设置文件路径
input_filename = "../assets/年末常住人口.txt"  # 输入文件路径
output_filename = "../assets/地区数据.csv"  # 输出文件路径

# 调用函数处理数据
process_population_data(input_filename, output_filename)
