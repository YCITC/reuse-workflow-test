import json
import pandas as pd
import requests
import time
import os
import numpy as np

LOKI_URL = "http://localhost:3100/loki/api/v1/push"

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
        return f"[Tool Use]: {content_item.get('name', '')}({json.dumps(content_item.get('input', ''))})"
    elif c_type == "tool_result":
        return f"[Tool Result]: {json.dumps(content_item.get('content', ''))}"
    return json.dumps(content_item)

def interpolate_timestamps(data):
    """使用線性插值填充缺失的時間戳"""
    # 提取所有時間戳並轉為奈秒級別的 unix timestamp
    timestamps = [
        (i, pd.to_datetime(item.get("timestamp")).timestamp() * 1e9)
        for i, item in enumerate(data)
        if item.get("timestamp")
    ]
    
    if not timestamps: # 如果沒有任何時間戳，就退回舊方法
        return None

    # 將索引和時間戳分開
    indices, ts_values = zip(*timestamps)
    
    # 建立一個包含所有索引的陣列
    all_indices = np.arange(len(data))
    
    # 使用 numpy 的線性插值函數
    interpolated_ts_values = np.interp(all_indices, indices, ts_values)
    
    # 將插值後的奈秒時間戳轉回字串格式
    return [str(int(ts)) for ts in interpolated_ts_values]


def import_json_to_loki(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return
            
    headers = {'Content-type': 'application/json'}
    streams = []

    # 進行時間戳插值
    new_timestamps = interpolate_timestamps(data)
    
    if not new_timestamps:
        print("Warning: No valid timestamps found for interpolation. Falling back to simple increment.")
        current_ns = int(time.time() * 1e9)
        new_timestamps = [str(current_ns + i * 1000000) for i in range(len(data))]


    for index, item in enumerate(data):
        log_line = {"type": item.get("type", "unknown")}
        ts_ns = new_timestamps[index]

        # ... (其餘解析邏輯與之前相同)
        message = item.get("message", {})
        usage_data = item.get("usage") or (message if isinstance(message, dict) else {}).get("usage")
        if usage_data:
            log_line.update({
                'usage_input_tokens': usage_data.get('input_tokens'),
                'usage_output_tokens': usage_data.get('output_tokens'),
                'usage_cache_creation_input_tokens': usage_data.get('cache_creation_input_tokens'),
                'usage_cache_read_input_tokens': usage_data.get('cache_read_input_tokens'),
                'usage_total_tokens': usage_data.get('total_tokens'),
                'usage_duration_ms': usage_data.get('duration_ms'),
                'usage_tool_uses': usage_data.get('tool_uses')
            })

        c_type = log_line["type"]
        contents = []
        if c_type == "system":
            log_line["description"] = item.get("description", "")
            log_line["prompt"] = item.get("prompt", "")
            if item.get("summary"): contents.append(f"Summary: {item.get('summary')}")

        elif c_type == "assistant":
            message_content = message.get("content", [])
            if isinstance(message_content, list):
                for c in message_content:
                    contents.append(extract_content(c))
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        tool_input = c.get("input", {})
                        if isinstance(tool_input, dict):
                            if "description" in tool_input: log_line["description"] = tool_input.get("description", "")
                            if "prompt" in tool_input: log_line["prompt"] = tool_input.get("prompt", "")
            elif isinstance(message_content, str):
                contents.append(message_content)

        elif c_type == "user":
            user_content = message.get("content", [])
            if isinstance(user_content, list):
                for c in user_content:
                    contents.append(extract_content(c))
            elif isinstance(user_content, str):
                contents.append(user_content)
            if item.get("tool_use_result"):
                contents.append(f"[Tool Use Result]: {json.dumps(item.get('tool_use_result'))}")
        
        else:
             if message: contents.append(str(message))
        
        log_line["content"] = '\n'.join(contents)
        final_log_line = {k: v for k, v in log_line.items() if v is not None and v != ''}
        
        streams.append({
            "stream": {"source": "claude_logs", "type": log_line["type"]},
            "values": [[ts_ns, json.dumps(final_log_line, ensure_ascii=False)]]
        })

    payload = {"streams": streams}
    try:
        response = requests.post(LOKI_URL, data=json.dumps(payload), headers=headers)
        if response.status_code == 204:
            print(f"Successfully pushed {len(streams)} logs (with interpolated timestamps) to Loki.")
        else:
            print(f"Failed to push logs. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error pushing to Loki: {e}")

if __name__ == "__main__":
    json_file = "../log/claude-execution-output.json"
    import_json_to_loki(json_file)
