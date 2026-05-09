import random
import time

# =====================================================================
# HƯỚNG DẪN KẾT NỐI LINH KIỆN THẬT (ESP32 / ARDUINO)
# 1. Mở Terminal cài thư viện: pip install pyserial
# 2. Đổi USE_REAL_HARDWARE = True
# 3. Đổi SERIAL_PORT thành cổng USB máy bạn (VD: 'COM3' ở Windows, hoặc '/dev/ttyUSB0' ở Linux/Mac)
# =====================================================================

USE_REAL_HARDWARE = False 
SERIAL_PORT = 'COM3'  
BAUD_RATE = 9600

serial_inst = None

# Khởi tạo kết nối Serial nếu bật chế độ dùng linh kiện thật
if USE_REAL_HARDWARE:
    try:
        import serial
        serial_inst = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2) # Chờ phần cứng khởi động
        print(f"✅ Đã kết nối phần cứng tại cổng {SERIAL_PORT}")
    except ImportError:
        print("⚠️ Chưa cài thư viện. Vui lòng gõ: pip install pyserial")
        USE_REAL_HARDWARE = False
    except Exception as e:
        print(f"⚠️ Không tìm thấy mạch ESP32/Arduino. Tự động chuyển về Giả lập! Lỗi: {e}")
        USE_REAL_HARDWARE = False


def control_relay(device, state):
    """
    Điều khiển rơ-le thiết bị.
    device: 'HEATER' (Sưởi) hoặc 'FAN' (Quạt)
    state: True (BẬT) hoặc False (TẮT)
    """
    action_str = "ON" if state else "OFF"
    
    # 1. CHẠY MÃ LỆNH LINH KIỆN THẬT
    if USE_REAL_HARDWARE and serial_inst:
        try:
            # Gửi chuỗi lệnh xuống Arduino (VD: "HEATER_ON\n")
            command = f"{device}_{action_str}\n"
            serial_inst.write(command.encode('utf-8'))
        except Exception as e:
            print(f"Lỗi gửi lệnh Relay: {e}")
            
    # 2. IN LOG GIẢ LẬP TRÊN TERMINAL
    icon = "🔥" if device == "HEATER" else "🌀"
    print(f"🔌 {icon} [PHẦN CỨNG]: Đã truyền tín hiệu cho {device} -> {action_str}")