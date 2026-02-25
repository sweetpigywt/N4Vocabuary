import pdfplumber
import json
import os
import re

def start_conversion():
    input_pdf = "N4.pdf"  # 匹配你改名后的文件
    output_js = "questions_n4.js"

    print(f"--- 脚本启动 ---")
    
    # 1. 检查文件是否存在
    if not os.path.exists(input_pdf):
        print(f"❌ 错误：在当前文件夹下找不到 {input_pdf}！")
        print(f"请检查文件名是否真的是 N4.pdf (注意大小写)")
        return

    questions = []

    try:
        print(f"📂 正在打开 {input_pdf}...")
        with pdfplumber.open(input_pdf) as pdf:
            full_text = ""
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
                print(f"已读取第 {i+1}/{len(pdf.pages)} 页...")

            print("🔍 正在提取题目和选项...")
            
            # 使用正则匹配题目逻辑 (匹配 "1. ", "2. " 等开头的行)
            # 这个正则会寻找数字开头，后面跟着题目描述，直到遇到选项或下一个数字
            pattern = r'(?:\n|^)(?:\d+)\.\s+(.*?)(?=\n\d+\.|\nAnswer Key|$)'
            raw_blocks = re.findall(r'(?:\n|^)(\d+)\.\s+(.*?)(?=\n\d+\.|\nDay\d+|$)', full_text, re.DOTALL)

            for item in raw_blocks:
                q_id = item[0]
                q_content = item[1].strip().split('\n')
                
                if len(q_content) >= 2:
                    # 第一行通常是题目
                    text = q_content[0]
                    # 尝试寻找看起来像选项的行（通常在题目后面）
                    opts = [line.strip() for line in q_content[1:] if line.strip()][:4]
                    
                    if len(opts) == 4:
                        questions.append({
                            "id": int(q_id),
                            "text": text,
                            "options": opts,
                            "ans": 0  # 默认设为0，PDF答案在末尾建议手动校对
                        })

            # 2. 导出为 JS 文件
            print(f"💾 正在生成 {output_js}...")
            js_str = f"const QUESTIONS_N4 = {json.dumps(questions, ensure_ascii=False, indent=4)};"
            
            with open(output_js, 'w', encoding='utf-8') as f:
                f.write(js_str)

        print(f"✅ 成功完成！")
        print(f"共提取题目: {len(questions)} 道")
        print(f"生成的数据库文件路径: {os.path.abspath(output_js)}")

    except Exception as e:
        print(f"❌ 发生意外错误: {str(e)}")

if __name__ == "__main__":
    start_conversion()
    input("\n处理结束。请按【回车键】关闭窗口...")