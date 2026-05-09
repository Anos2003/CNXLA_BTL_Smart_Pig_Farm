import pandas as pd
import os
from datetime import datetime

FILE_PATH = "outputs/nhat_ky_chuong_lon.xlsx"

def log_to_excel(sleeping, eating, moving, temp, gas, action):
    now = datetime.now()
    new_data = {
        "Ngày": [now.strftime("%Y-%m-%d")],
        "Giờ": [now.strftime("%H:%M:%S")],
        "Ngủ": [sleeping], "Ăn": [eating], "Đi lại": [moving],
        "Nhiệt độ": [temp], "Khí Gas": [gas], "Hành động": [action]
    }
    df_new = pd.DataFrame(new_data)
    if os.path.exists(FILE_PATH):
        df_old = pd.read_excel(FILE_PATH)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new
    df_final.to_excel(FILE_PATH, index=False)