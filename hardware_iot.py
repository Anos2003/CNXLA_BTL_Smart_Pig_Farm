import random

def read_sensors():
    """Khi có ESP32 thật, code Serial sẽ nằm ở đây"""
    # Giả lập số liệu: Nhiệt độ thấp (18 độ) và Khí gas tăng dần
    temp = 18.5 
    gas = random.uniform(100.0, 350.0)
    return temp, gas

def control_relay(device, state):
    """Gửi lệnh xuống ESP32 để bật/tắt thiết bị"""
    if state == "ON":
        print(f"🔌 [PHẦN CỨNG]: ĐÃ KÍCH RELAY BẬT {device}!")
    else:
        print(f"🔌 [PHẦN CỨNG]: ĐÃ TẮT {device}.")