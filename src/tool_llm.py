import inspect
import json
import os
import re

import pandas as pd
import requests
from typing import get_type_hints
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用SimHei显示中文
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示为方块的问题

def generate_full_completion(model: str, prompt: str) -> dict[str, str]:
    params = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(
        "http://localhost:11434/api/generate",
        headers={"Content-Type": "application/json"},
        data=json.dumps(params),
        timeout=1800, # 调整设置为1800，300限制过低
    )
    return json.loads(response.text)

def write_csv_from_text(file_name: str) -> None:
    """
    Read the specified text file given the file name.
    remove the table header and footer, and save it as a new CSV file.
    """

    # 获取当前文件所在目录的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 确定文件的完整路径（assets 文件夹中）
    input_file_path = os.path.join(current_dir, '..', 'assets', file_name)

    print(f"Reading the text file {input_file_path}...")

    # 读取文件内容
    try:
        with open(input_file_path, 'r', encoding='utf-8-sig') as file:
            lines = file.readlines()

        # 定义正则表达式来匹配行的开头是“地区”或具体地区名称（中文的省、市、自治区）
        region_pattern = re.compile(r'^(地区|北京|上海|天津|重庆|黑龙江|吉林|辽宁|内蒙古|新疆|西藏|宁夏|青海|甘肃|陕西|四川|云南|贵州|广西|海南|广东|福建|江西|湖南|湖北|安徽|浙江|江苏|山东|河南|河北|山西|四川|广东|广西|云南|福建|山东|河南|陕西|甘肃|新疆|青海|西藏)')

        # 去除表头和表尾
        filtered_lines = []
        for line in lines:
            # 去掉表头（不以 "地区" 或具体地区名称开头的行）
            if not filtered_lines and not region_pattern.match(line.strip()):
                continue
            # 去掉表尾（以 "注" 开头的行）
            if line.strip().startswith('注'):
                break
            filtered_lines.append(line)

        if not filtered_lines:
            print("No valid data found after removing headers and footers.")
            return

        # 生成新的 CSV 文件路径
        output_file_path = os.path.join(current_dir, '..', 'assets', file_name.replace('.txt', '_cleaned.csv'))

        # 保存去除表头和表尾的内容到新的 CSV 文件
        with open(output_file_path, 'w', encoding='utf-8-sig') as new_file:
            new_file.writelines(filtered_lines)

        print(f"Cleaned data saved to {output_file_path}.")

    except FileNotFoundError:
        print(f"Error: File {input_file_path} not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")


def calculate_population_statistics(file_path: str) -> None:
    """
    Calculate the mean, maximum, and minimum population values for each region in the given CSV file.
    """

    # 获取当前文件所在目录的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 确定文件的完整路径（assets 文件夹中）
    input_file_path = os.path.join(current_dir, '..', 'assets', file_path)

    print(f"Reading the text file {input_file_path}...")
    # 加载CSV文件
    df = pd.read_csv(input_file_path)
    
    # 计算均值、最大值、最小值
    df['均值'] = df.iloc[:, 1:].mean(axis=1)
    df['最大值'] = df.iloc[:, 1:].max(axis=1)
    df['最小值'] = df.iloc[:, 1:].min(axis=1)
    
    # 保存到新文件
    new_file_path = input_file_path.replace('.csv', '_stats.csv')
    df.to_csv(new_file_path, index=False, encoding='utf_8_sig')
    
    print(f"计算完成，结果已保存至 {new_file_path}")


def get_type_name(t):
    name = str(t)
    if "list" in name or "dict" in name:
        return name
    else:
        return t.__name__

def visualize_population_distribution(file_path: str) -> None:
    """
    Visualize the population distribution for the last 10 years as a pie chart for each region.
    """
    
    # 获取当前文件所在目录的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 确定文件的完整路径（assets 文件夹中）
    input_file_path = os.path.join(current_dir, '..', 'assets', file_path)

    print(f"Reading the text file {input_file_path}...")
    # 加载CSV文件
    df = pd.read_csv(input_file_path)
    
    # 假设CSV文件的列是年份，第1列是地区名称，其余列是各年份的人口数据
    years = df.columns[-10:]  # 取最后10列年份数据
    df['平均人口'] = df[years].mean(axis=1)  # 计算近10年的平均人口
    
    # 可视化
    plt.figure(figsize=(10, 7))
    plt.pie(df['平均人口'], labels=df.iloc[:, 0], autopct='%1.1f%%', startangle=140)
    plt.title('近10年各地区平均人口比例')
    plt.axis('equal')  # 确保饼状图为圆形
    plt.show()

    print("可视化完成。")

def visualize_population_trend(file_path: str, province_name: str) -> None:
    """
    Visualize the population trend for the last 10 years of a specific province as a line chart.
    

    Parameters:
    - file_path: CSV文件的路径
    - province_name: 省份的名称
    """
    
    # 获取当前文件所在目录的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 确定文件的完整路径（assets 文件夹中）
    input_file_path = os.path.join(current_dir, '..', 'assets', file_path)

    print(f"Reading the text file {input_file_path}...")
    # 加载CSV文件
    df = pd.read_csv(input_file_path)
    
    # 查找对应省份的数据
    province_data = df[df.iloc[:, 0] == province_name]
    if province_data.empty:
        print(f"未找到省份 {province_name} 的数据。")
        return
    
    # 假设CSV文件的列是年份，第1列是地区名称，后面的列是各年份的人口数据
    years = df.columns[-10:]  # 取最后10列年份数据
    population_values = province_data[years].values.flatten()  # 获取该省份的近10年人口数据
    
    # 可视化 - 折线图
    plt.figure(figsize=(10, 6))
    plt.plot(years, population_values, marker='o', linestyle='-', color='b', label=province_name)
    
    plt.title(f'{province_name} 近10年人口变化趋势')
    plt.xlabel('年份')
    plt.ylabel('人口数量')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()

    # 显示图表
    plt.tight_layout()
    plt.show()

    print(f"省份 {province_name} 的人口变化趋势图已完成。")

def function_to_json(func):
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)

    function_info = {
        "name": func.__name__,
        "description": func.__doc__,
        "parameters": {"type": "object", "properties": {}},
        "returns": type_hints.get("return", "void").__name__,
    }

    for name, _ in signature.parameters.items():
        param_type = get_type_name(type_hints.get(name, type(None)))
        function_info["parameters"]["properties"][name] = {"type": param_type}

    return json.dumps(function_info, indent=2)


def main():
    functions_prompt = f"""
You have access to the following tools:
{function_to_json(write_csv_from_text)}
{function_to_json(calculate_population_statistics)}
{function_to_json(visualize_population_distribution)}
{function_to_json(visualize_population_trend)}
You must follow these instructions:
Always select one or more of the above tools based on the user query
If a tool is found, you must respond in the JSON format matching the following schema:
{{
   "tools": {{
        "tool": "<name of the selected tool>",
        "tool_input": <parameters for the selected tool, matching the tool's JSON schema
   }}
}}
If there are multiple tools required, make sure a list of tools are returned in a JSON array.
If there is no tool that match the user request, you must respond empty JSON {{}}.

User Query:
    """

    GPT_MODEL = "mistral:latest"

    prompts = [
        # "Read from the text file 'permanent_population.txt' and write as csv file: remove the table header and footer, save as a new CSV file",
        # "Calculate the mean, maximum, and minimum population values for each region in the given CSV file 'permanent_population_cleaned.csv'",
        "Visualize the population distribution for the last 10 years in the given CSV file 'permanent_population_cleaned_stats.csv' as a pie chart",
        # "Visualize the population trend for the last 10 years of '浙江省' in the given CSV file 'permanent_population_cleaned.csv' as a line chart",
    ]

    for prompt in prompts:

        print(f"🤔{prompt}")
        question = functions_prompt + prompt
        response = generate_full_completion(GPT_MODEL, question)
        try:
            data = json.loads(response.get("response", response))
            # print(data)
            for tool_data in data["tools"]:
                execute_fuc(tool_data)
        except Exception:
            print('No tools found.')
        print(f"Total duration: {int(response.get('total_duration')) / 1e9} seconds")


def execute_fuc(tool_data):
    func_name = tool_data["tool"]
    func_input = tool_data["tool_input"]

    # 获取全局命名空间中的函数对象
    func = globals().get(func_name)

    if func is not None and callable(func):
        # 如果找到了函数并且是可调用的，调用它
        func(**func_input)
    else:
        print(f"Unknown function: {func_name}")


if __name__ == "__main__":
    main()