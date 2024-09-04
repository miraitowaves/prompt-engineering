import inspect
import json
import os
import re

import requests
from typing import get_type_hints


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



def get_type_name(t):
    name = str(t)
    if "list" in name or "dict" in name:
        return name
    else:
        return t.__name__


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
        "Read from the text file 'permanent_population.txt' and write as csv file: remove the table header and footer, save as a new CSV file",
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

