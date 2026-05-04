import json
import pandas as pd
import os

def extract_content(content_item):
    """提取不同類型的 content 內容"""
    if isinstance(content_item, str):
        return content_item
    
    c_type = content_item.get("type")
    if c_type == "text":
        return content_item.get("text", "")
    elif c_type == "thinking":
        return f"[Thinking]: {content_item.get('thinking', '')}"
    elif c_type == "tool_use":
        return f"[Tool Use]: {content_item.get('name', '')}({content_item.get('input', '')})"
    elif c_type == "tool_result":
        return f"[Tool Result]: {content_item.get('content', '')}"
    return str(content_item)

def parse_log(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    
    rows = []
    for item in data:
        row = {
            "type": item.get("type", ""),
            "timestamp": item.get("timestamp", ""),
            "usage": "",
            "content": "",
            "description": "",
            "prompt": ""
        }
        
        # 處理 usage (優先從 message.usage 拿，或是 top-level usage)
        usage_data = item.get("usage")
        message = item.get("message", {})
        if not usage_data and isinstance(message, dict):
            usage_data = message.get("usage")
        
        if usage_data:
            row["usage"] = json.dumps(usage_data)
            
        c_type = row["type"]
        contents = []

        # 針對不同 type 的處理邏輯
        if c_type == "system":
            row["description"] = item.get("description", "")
            row["prompt"] = item.get("prompt", "")
            
            # fallback: 如果 system 還有其他內容可以放進 content
            if item.get("summary"):
                contents.append(f"Summary: {item.get('summary')}")

        elif c_type == "assistant":
            # 從 message.content 提取
            message_content = message.get("content", [])
            if isinstance(message_content, list):
                for c in message_content:
                    contents.append(extract_content(c))
                    # 從 tool_use 的 input 中提取 description 和 prompt
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        tool_input = c.get("input", {})
                        if isinstance(tool_input, dict):
                            if "description" in tool_input and not row["description"]:
                                row["description"] = tool_input.get("description", "")
                            if "prompt" in tool_input and not row["prompt"]:
                                row["prompt"] = tool_input.get("prompt", "")
            elif isinstance(message_content, str):
                contents.append(message_content)

        elif c_type == "user":
            # 處理 user message 的 content
            user_content = message.get("content", [])
            if isinstance(user_content, list):
                for c in user_content:
                    if isinstance(c, dict) and c.get("type") == "tool_result":
                        contents.append(f"[Tool Result]: {c.get('content', '')}")
                    elif isinstance(c, dict) and c.get("type") == "text":
                        contents.append(c.get("text", ""))
                    elif isinstance(c, str):
                        contents.append(c)
            elif isinstance(user_content, str):
                contents.append(user_content)
                
            # 處理 tool_use_result 備用邏輯
            if item.get("tool_use_result"):
                contents.append(f"[Tool Use Result]: {json.dumps(item.get('tool_use_result'))}")

        # 其他 type 處理
        else:
             message_content = message.get("content")
             if isinstance(message_content, list):
                 for c in message_content:
                     contents.append(extract_content(c))
             elif isinstance(message_content, str):
                 contents.append(message_content)

        row["content"] = "\n".join(contents)
        rows.append(row)
    
    return pd.DataFrame(rows)

if __name__ == "__main__":
    # 路徑指向 log/ 目錄
    input_file = "../log/claude-execution-output.json"
    output_file = "../log/parsed_logs.csv"
    
    df = parse_log(input_file)
    if df is not None:
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"Successfully parsed logs to {output_file}")
        print(f"Total rows: {len(df)}")
