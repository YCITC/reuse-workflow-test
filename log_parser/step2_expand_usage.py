import pandas as pd
import json
import os

def expand_usage(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        return None

    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

    # 初始化要展開的欄位
    expanded_columns = {
        'usage_input_tokens': [],
        'usage_output_tokens': [],
        'usage_cache_creation_input_tokens': [],
        'usage_cache_read_input_tokens': [],
        'usage_total_tokens': [],
        'usage_duration_ms': [],
        'usage_tool_uses': []
    }

    for usage_str in df['usage']:
        if pd.isna(usage_str) or usage_str.strip() == "":
            for key in expanded_columns:
                expanded_columns[key].append(None)
            continue

        try:
            usage_data = json.loads(usage_str)
            # 一般 message 的 usage
            expanded_columns['usage_input_tokens'].append(usage_data.get('input_tokens'))
            expanded_columns['usage_output_tokens'].append(usage_data.get('output_tokens'))
            expanded_columns['usage_cache_creation_input_tokens'].append(usage_data.get('cache_creation_input_tokens'))
            expanded_columns['usage_cache_read_input_tokens'].append(usage_data.get('cache_read_input_tokens'))
            
            # system task_progress / task_notification 的 usage 
            expanded_columns['usage_total_tokens'].append(usage_data.get('total_tokens'))
            expanded_columns['usage_duration_ms'].append(usage_data.get('duration_ms'))
            expanded_columns['usage_tool_uses'].append(usage_data.get('tool_uses'))
        except json.JSONDecodeError:
            for key in expanded_columns:
                expanded_columns[key].append(None)

    # 將展開的欄位加入 DataFrame
    for key, values in expanded_columns.items():
        df[key] = values

    # 移除原始的 usage 欄位
    df = df.drop(columns=['usage'])

    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Successfully expanded usage and saved to {output_file}")
    print(f"Total rows processed: {len(df)}")
    return df

if __name__ == "__main__":
    input_csv = "../log/parsed_logs.csv"
    output_csv = "../log/parsed_logs_expanded.csv"
    
    expand_usage(input_csv, output_csv)
