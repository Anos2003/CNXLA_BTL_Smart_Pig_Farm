import pandas as pd
import os

FILE_PATH = "outputs/nhat_ky_chuong_lon.xlsx"

def log_to_excel(time_str, sleeping, eating, moving, temp, gas, status):
    """Hàm lưu lịch sử hoạt động vào file Excel"""
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    new_row = {
        "Thời gian": time_str,
        "Ngủ": sleeping,
        "Ăn": eating,
        "Di chuyển": moving,
        "Nhiệt độ": temp,
        "Khí Gas": gas,
        "Trạng thái": status
    }
    
    if os.path.exists(FILE_PATH):
        df_log = pd.read_excel(FILE_PATH)
    else:
        df_log = pd.DataFrame(columns=list(new_row.keys()))
        
    df_log = pd.concat([df_log, pd.DataFrame([new_row])], ignore_index=True)
    df_log.to_excel(FILE_PATH, index=False)
    
    return df_log