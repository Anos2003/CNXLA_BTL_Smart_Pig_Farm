import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_alert(message):
    """Hàm gửi tin nhắn cảnh báo qua Telegram"""
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Cảnh báo: Chưa cấu hình TELEGRAM_TOKEN hoặc CHAT_ID trong file .env")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, json=payload, timeout=2) 
        if response.status_code != 200:
            print(f"Lỗi API: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")
        return False