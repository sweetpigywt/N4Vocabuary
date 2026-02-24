import pdfplumber
import re
import json

def extract_all(pdf_path):
    questions_list = []
    answers_dict = {} # 格式: {(day_num, q_num): answer_index}
    
    current_day_q = 0
    current_day_a = 0

    # 正则表达式
    day_re = re.compile(r'Day\s*(\d+)', re.IGNORECASE)
    q_start_re = re.compile(r'^(\d{1,2})\.\s*(.*)')
    ans_key_re = re.compile(r'Question\s*(\d+):\s*(\d+)', re.IGNORECASE)

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue
            lines = text.split('\n')

            # 检查这一页是否有 Day 标记
            page_day = None
            for line in lines:
                day_match = day_re.search(line)
                if day_match:
                    page_day = int(day_match.group(1))
                    break

            # 判断是题目页还是答案页
            is_answer_page = "Answer Key" in text
            
            if not is_answer_page:
                # --- 题目解析逻辑 ---
                if page_day: current_day_q = page_day
                temp_q = None
                
                for line in lines:
                    line = line.strip()
                    q_match = q_start_re.match(line)
                    if q_match:
                        if temp_q and len(temp_q['options']) >= 4:
                            questions_list.append(temp_q)
                        
                        temp_q = {
                            "day": current_day_q,
                            "id": int(q_match.group(1)),
                            "question": q_match.group(2),
                            "options": [],
                            "answer": None
                        }
                    elif temp_q:
                        if len(temp_q['options']) < 4 and len(line) < 40 and "PAGE" not in line.upper():
                            # 简单的过滤，避免抓到页码
                            if line and not day_re.search(line):
                                temp_q['options'].append(line)
                        else:
                            if len(temp_q['options']) == 0:
                                temp_q['question'] += " " + line
                if temp_q: questions_list.append(temp_q)
                
            else:
                # --- 答案解析逻辑 ---
                if page_day: current_day_a = page_day
                for line in lines:
                    # 更新当前 Day (答案页可能一页有多个 Day 的答案)
                    day_match = day_re.search(line)
                    if day_match: current_day_a = int(day_match.group(1))
                    
                    ans_matches = ans_key_re.findall(line)
                    for q_num, ans_val in ans_matches:
                        # 转换答案：PDF里是1-4，程序里下标是0-3
                        answers_dict[(current_day_a, int(q_num))] = int(ans_val) - 1

    # --- 合并数据 ---
    final_data = []
    for q in questions_list:
        key = (q['day'], q['id'])
        if key in answers_dict:
            q['answer'] = answers_dict[key]
            final_data.append(q)
        else:
            # 如果没找到对应答案，可以选填或者跳过
            q['answer'] = 0 
            final_data.append(q)

    return final_data

# 执行
pdf_name = "JLPT N4 – Vocabulary Exercise 01-31 全.pdf"
data = extract_all(pdf_name)

# 输出为 JS 文件供前端使用
js_content = f"const allQuestions = {json.dumps(data, ensure_ascii=False, indent=2)};"
with open("questions.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"解析成功！已匹配题目和答案，共 {len(data)} 道题。")