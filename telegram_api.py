import requests
import config

def send_alert(message):
    if "ĐIỀN" in config.TELEGRAM_TOKEN: return
    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": config.TELEGRAM_CHAT_ID, "text": f"🚨 [SMART FARM]: {message}"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Lỗi Telegram: {e}")