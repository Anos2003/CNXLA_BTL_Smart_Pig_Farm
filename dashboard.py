import streamlit as st
import cv2
import time
import os
import pandas as pd
import math
from ultralytics import YOLO

# Import các module đã được tách nhỏ (Micro-Architecture)
from telegram_api import send_alert
from excel_logger import log_to_excel, FILE_PATH
from hardware_iot import control_relay

# ==========================================
# 1. CSS INJECTION - BIẾN HÌNH UI/UX
# ==========================================
def inject_custom_css():
    st.markdown("""
        <style>
        .stApp { background-color: #0A192F; color: #dde4e0; font-family: 'Space Grotesk', sans-serif; }
        h1, h2, h3 { color: #64FFDA !important; text-shadow: 0 0 10px rgba(100,255,218,0.3); }
        div[data-testid="stMetricValue"] { color: #5ffbd6 !important; font-size: 28px !important; font-weight: bold;}
        div[data-testid="stMetricLabel"] { color: #85948e !important; text-transform: uppercase; letter-spacing: 1px;}
        div[data-testid="stContainer"] { border: 1px solid rgba(100,255,218,0.2); box-shadow: 0 0 15px rgba(95,251,214,0.05); border-radius: 8px;}
        </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="VIGILANT OPS - AGRI", page_icon="🛰️", layout="wide")
inject_custom_css()

# ==========================================
# 2. OPENCV HUD DRAWING
# ==========================================
def draw_hud_box(img, x1, y1, x2, y2, color, thickness=2, line_len=20):
    cv2.line(img, (x1, y1), (x1 + line_len, y1), color, thickness)
    cv2.line(img, (x1, y1), (x1, y1 + line_len), color, thickness)
    cv2.line(img, (x2, y1), (x2 - line_len, y1), color, thickness)
    cv2.line(img, (x2, y1), (x2, y1 + line_len), color, thickness)
    cv2.line(img, (x1, y2), (x1 + line_len, y2), color, thickness)
    cv2.line(img, (x1, y2), (x1, y2 - line_len), color, thickness)
    cv2.line(img, (x2, y2), (x2 - line_len, y2), color, thickness)
    cv2.line(img, (x2, y2), (x2, y2 - line_len), color, thickness)
    
    overlay = img.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(overlay, 0.1, img, 0.9, 0, img)

# ==========================================
# KHỞI TẠO STATE & CẤU HÌNH CHUNG
# ==========================================
LOG_INTERVAL = 5 

if 'is_running' not in st.session_state: st.session_state.is_running = False
if 'chart_data' not in st.session_state: st.session_state.chart_data = pd.DataFrame(columns=["Time", "Temp", "Gas"])
if 'actual_heater' not in st.session_state: st.session_state.actual_heater = False
if 'actual_fan' not in st.session_state: st.session_state.actual_fan = False

@st.cache_resource
def load_model(): return YOLO('models/best.pt') 
model = load_model()

CLASS_MAP = {
    0: {"label": "SLEEP", "color": (218, 255, 100)},    
    1: {"label": "EAT", "color": (131, 225, 74)},       
    2: {"label": "MOVE", "color": (10, 0, 255)}         
}

def get_video_files():
    if not os.path.exists("videos"): os.makedirs("videos")
    files = [f for f in os.listdir("videos") if f.endswith('.mp4')]
    return files if files else ["Trống"]

# ==========================================
# SIDEBAR: CONTROL & CONFIGURATION PANEL
# ==========================================
with st.sidebar:
    st.markdown("### 🛰️ VIGILANT OPS")
    col_start, col_stop = st.columns(2)
    if col_start.button("▶️ ACTIVATE", width="stretch", type="primary"): st.session_state.is_running = True
    if col_stop.button("🛑 STANDBY", width="stretch"): st.session_state.is_running = False

    st.markdown("---")
    st.markdown("### ⚙️ CẤU HÌNH NGƯỠNG IOT")
    temp_min_threshold = st.number_input("Ngưỡng bật Sưởi (Nhiệt độ < °C)", value=20.0, step=0.5)
    temp_max_threshold = st.number_input("Ngưỡng bật Quạt (Nhiệt độ > °C)", value=40.0, step=0.5) 
    gas_max_threshold = st.number_input("Ngưỡng bật Quạt (Khí Gas > ppm)", value=300.0, step=10.0)
    alert_sleeping_limit = st.number_input("Báo động khi lợn tụ tập > (con)", value=5, step=1)
    tele_cooldown = st.number_input("Khoảng cách gửi tin (giây)", value=60, step=10)

    st.markdown("---")
    st.markdown("### 🕹️ ĐIỀU KHIỂN THỦ CÔNG")
    manual_heater = st.toggle("🔥 Bật Đèn Sưởi")
    manual_fan = st.toggle("🌀 Bật Quạt Hút")

    st.markdown("---")
    st.markdown("### 🎛️ TEST DỮ LIỆU ĐẦU VÀO")
    selected_video = st.selectbox("📹 Chọn Camera/Video", get_video_files())
    mock_temp = st.slider("🌡️ Cảm biến Nhiệt độ (°C)", 10.0, 50.0, 25.0) 
    mock_gas = st.slider("☁️ Cảm biến Khí Gas (PPM)", 0.0, 500.0, 50.0)

# ==========================================
# MAIN UI
# ==========================================
st.title("AGRI-SURVEILLANCE HUD")

# Hàng 1: Hiển thị Thông số
k1, k2, k3, k4, k5 = st.columns(5)
m_sleep, m_eat, m_move, m_temp, m_gas = k1.empty(), k2.empty(), k3.empty(), k4.empty(), k5.empty()
m_sleep.metric("💤 ZZZ", "0"); m_eat.metric("🌾 FEEDING", "0"); m_move.metric("🏃 ACTIVE", "0")
m_temp.metric("🌡️ TEMP", f"{mock_temp}°C"); m_gas.metric("☁️ GAS", f"{mock_gas} PPM")

# Hàng 2: ĐÈN BÁO TRẠNG THÁI THIẾT BỊ
st.markdown("<br>", unsafe_allow_html=True)
col_ind1, col_ind2, col_ind3 = st.columns(3)
ui_heater = col_ind1.empty()
ui_fan = col_ind2.empty()

if not st.session_state.is_running:
    ui_heater.info("⚪ SƯỞI: ĐANG TẮT (Standby)")
    ui_fan.info("⚪ QUẠT: ĐANG TẮT (Standby)")

st.markdown("---")
tab_monitor, tab_setup = st.tabs(["👁️‍🗨️ LIVE FEED", "📐 CALIBRATION (CĂN CHỈNH)"])

with tab_setup:
    col_v, col_guide = st.columns([2, 1])
    with col_v:
        preview_frame = st.empty()
    with col_guide:
        st.markdown("#### 🎯 Kích hoạt Zone")
        use_roi = st.toggle("Bật phân tích theo Vùng máng cám (ROI)", value=True)
        if use_roi:
            alpha_roi = st.slider("Độ mờ ROI (Alpha)", 0.1, 1.0, 0.2)
            r_x = st.number_input("Tọa độ X", value=20, step=10)
            r_y = st.number_input("Tọa độ Y", value=80, step=10)
            r_w = st.number_input("Độ rộng W", value=1220, step=10)
            r_h = st.number_input("Độ cao H", value=150, step=10)
        else:
            st.info("Hệ thống sẽ quét toàn bộ khung hình camera.")
    
    if selected_video != "Trống":
        cap_prev = cv2.VideoCapture(os.path.join("videos", selected_video))
        ret, frm = cap_prev.read()
        cap_prev.release()
        if ret:
            if use_roi:
                ov = frm.copy()
                cv2.rectangle(ov, (r_x, r_y), (r_x+r_w, r_y+r_h), (218, 255, 100), -1)
                cv2.addWeighted(ov, alpha_roi, frm, 1 - alpha_roi, 0, frm)
                draw_hud_box(frm, r_x, r_y, r_x+r_w, r_y+r_h, (218, 255, 100), 2, 40)
                cv2.putText(frm, "ZONE: FEEDING", (r_x, r_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (218, 255, 100), 2)
            preview_frame.image(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB), width="stretch")

with tab_monitor:
    c_vid, c_data = st.columns([7, 3])
    with c_vid: 
        vid_frame = st.empty()
    with c_data: 
        st.markdown("#### 📊 TELEMETRY")
        chart_frame = st.empty()
        st.markdown("#### 🚨 SYS LOG")
        log_frame = st.empty()
        st.markdown("#### 💾 DATABASE")
        excel_frame = st.empty()

    if not os.path.exists("outputs"): os.makedirs("outputs")
    if os.path.exists(FILE_PATH) and not st.session_state.is_running:
        excel_frame.dataframe(pd.read_excel(FILE_PATH).tail(3), width="stretch")

    # ==========================================
    # CORE PIPELINE
    # ==========================================
    if st.session_state.is_running and selected_video != "Trống":
        video_path = os.path.join("videos", selected_video)
        cap = cv2.VideoCapture(video_path)
        prev_time = time.time()
        last_log = 0
        last_telegram_time = 0

        try:
            enable_roi = use_roi
        except NameError:
            enable_roi = True

        track_history = {} 
        MOVEMENT_THRESHOLD = 60 
        HISTORY_FRAMES = 30     

        while cap.isOpened() and st.session_state.is_running:
            ret, frame = cap.read()
            if not ret: break

            if enable_roi:
                ov = frame.copy()
                cv2.rectangle(ov, (r_x, r_y), (r_x+r_w, r_y+r_h), (218, 255, 100), -1)
                cv2.addWeighted(ov, alpha_roi, frame, 1 - alpha_roi, 0, frame)
                draw_hud_box(frame, r_x, r_y, r_x+r_w, r_y+r_h, (218, 255, 100), 2, 30)

            results = model.track(frame, persist=True, tracker="bytetrack.yaml", conf=0.6, iou=0.25, verbose=False)
            c_s, c_e, c_m = 0, 0, 0

            if results[0].boxes is not None and results[0].boxes.id is not None:
                raw_detections = []
                for box, track_id in zip(results[0].boxes.xyxy.int().cpu().tolist(), results[0].boxes.id.int().cpu().tolist()):
                    x1, y1, x2, y2 = box
                    area = (x2 - x1) * (y2 - y1)
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    raw_detections.append({
                        "id": track_id, "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                        "cx": cx, "cy": cy, "area": area
                    })

                raw_detections = sorted(raw_detections, key=lambda k: k['area'], reverse=True)
                filtered_detections = []
                
                for det in raw_detections:
                    is_fragment = False
                    for kept_det in filtered_detections:
                        if (kept_det['x1'] < det['cx'] < kept_det['x2']) and (kept_det['y1'] < det['cy'] < kept_det['y2']):
                            is_fragment = True 
                            break
                    if not is_fragment:
                        filtered_detections.append(det)

                for det in filtered_detections:
                    x1, y1, x2, y2 = det['x1'], det['y1'], det['x2'], det['y2']
                    cx, cy = det['cx'], det['cy']
                    track_id = det['id']
                    box_height = y2 - y1

                    if box_height < 120: continue
                    current_class = 0 
                    
                    is_eating = False
                    if enable_roi:
                        TOLERANCE = 80
                        if (r_x < cx < r_x+r_w) and (r_y - 30 < y1 < r_y + r_h + TOLERANCE):
                            is_eating = True

                    if is_eating:
                        current_class = 1 
                    else:
                        if track_id not in track_history: track_history[track_id] = []
                        track_history[track_id].append((cx, cy))
                        if len(track_history[track_id]) > HISTORY_FRAMES: track_history[track_id].pop(0)

                        if len(track_history[track_id]) >= 2:
                            start_x, start_y = track_history[track_id][0]
                            distance = math.hypot(cx - start_x, cy - start_y)
                            if distance > MOVEMENT_THRESHOLD: current_class = 2 

                    if current_class == 0: c_s += 1
                    elif current_class == 1: c_e += 1
                    else: c_m += 1
                    
                    info = CLASS_MAP[current_class]
                    draw_hud_box(frame, x1, y1, x2, y2, info["color"], 2, 15)
                    cv2.rectangle(frame, (x1, y1-20), (x1 + 100, y1), info["color"], -1)
                    cv2.putText(frame, f"ID:{track_id} {info['label']}", (x1+5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1)

            curr_time = time.time()
            fps = 1 / (curr_time - prev_time)
            prev_time = curr_time
            cv2.putText(frame, f"FPS: {fps:.1f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (218, 255, 100), 2)
            vid_frame.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), width="stretch")

            m_sleep.metric("💤 ZZZ", f"{c_s}")
            m_eat.metric("🌾 FEEDING", f"{c_e}")
            m_move.metric("🏃 ACTIVE", f"{c_m}")
            m_temp.metric("🌡️ TEMP", f"{mock_temp}°C")
            m_gas.metric("☁️ GAS", f"{mock_gas} PPM")

            if curr_time - last_log > 1.0:
                t_str = time.strftime("%H:%M:%S")
                new_pt = pd.DataFrame([{"Time": t_str, "Temp": mock_temp, "Gas": mock_gas}])
                st.session_state.chart_data = pd.concat([st.session_state.chart_data, new_pt]).tail(20)
                chart_frame.line_chart(st.session_state.chart_data.set_index("Time"), color=["#5ffbd6", "#ffb4ab"])
                
                target_heater = False
                target_fan = False
                reason_heater = ""
                reason_fan = ""

                # Xác định trạng thái của SƯỞI
                if manual_heater:
                    target_heater = True
                    reason_heater = "Lệnh BẬT thủ công"
                elif c_s > alert_sleeping_limit and mock_temp < temp_min_threshold:
                    target_heater = True
                    reason_heater = f"Tự động (Lợn tụ tập do lạnh {mock_temp}°C)"

                # Xác định trạng thái của QUẠT 
                if manual_fan:
                    target_fan = True
                    reason_fan = "Lệnh BẬT thủ công"
                elif mock_gas > gas_max_threshold:
                    target_fan = True
                    reason_fan = f"Tự động (Khí Gas {mock_gas} PPM vượt ngưỡng)"
                elif mock_temp > temp_max_threshold:
                    target_fan = True
                    reason_fan = f"Tự động (Nhiệt độ quá cao {mock_temp}°C)"

                if target_heater: ui_heater.error("🔥 SƯỞI: ĐANG BẬT")
                else: ui_heater.info("⚪ SƯỞI: ĐANG TẮT")
                if target_fan: ui_fan.warning("🌀 QUẠT: ĐANG BẬT")
                else: ui_fan.info("⚪ QUẠT: ĐANG TẮT")

                # ==========================================================
                # KIỂM TRA SỰ THAY ĐỔI & GỌI MODULE PHẦN CỨNG + TELEGRAM
                # ==========================================================
                changes_msg = []
                
                if target_heater and not st.session_state.actual_heater:
                    control_relay("HEATER", True) 
                    changes_msg.append(f"🟢 BẬT ĐÈN SƯỞI\nLý do: {reason_heater}")
                elif not target_heater and st.session_state.actual_heater:
                    control_relay("HEATER", False) 
                    if not manual_heater: changes_msg.append("🔴 TẮT ĐÈN SƯỞI\nLý do: Đã đủ ấm.")
                    else: changes_msg.append("🔴 TẮT ĐÈN SƯỞI\nLý do: Lệnh TẮT thủ công.")

                if target_fan and not st.session_state.actual_fan:
                    control_relay("FAN", True) 
                    changes_msg.append(f"🟢 BẬT QUẠT HÚT\nLý do: {reason_fan}")
                elif not target_fan and st.session_state.actual_fan:
                    control_relay("FAN", False) 
                    if not manual_fan: changes_msg.append("🔴 TẮT QUẠT HÚT\nLý do: Môi trường an toàn.")
                    else: changes_msg.append("🔴 TẮT QUẠT HÚT\nLý do: Lệnh TẮT thủ công.")

                st.session_state.actual_heater = target_heater
                st.session_state.actual_fan = target_fan

                sys_status = "Bình thường"
                if target_heater or target_fan:
                    active = []
                    if target_heater: active.append("SƯỞI")
                    if target_fan: active.append("QUẠT")
                    sys_status = f"Hệ thống đang kích hoạt: {' & '.join(active)}"
                    log_frame.warning(f"[{t_str}] SYS: {sys_status}")
                else:
                    log_frame.success(f"[{t_str}] SYS_OP: NOMINAL")

                if len(changes_msg) > 0:
                    alert_msg = "🔄 *CẬP NHẬT TRẠNG THÁI THIẾT BỊ*\n➖➖➖➖➖➖➖➖➖➖\n"
                    for msg in changes_msg: alert_msg += f"- {msg}\n"
                    alert_msg += f"\n⏰ *Thời gian:* {t_str}"
                    
                    # Gọi hàm từ module telegram_api.py
                    success = send_alert(alert_msg) 
                    if success: st.toast('Đã cập nhật trạng thái qua Telegram!', icon='📨')

                # Gọi hàm từ module excel_logger.py
                if curr_time - last_log > LOG_INTERVAL:
                    df_log = log_to_excel(t_str, c_s, c_e, c_m, mock_temp, mock_gas, sys_status)
                    excel_frame.dataframe(df_log.tail(3), width="stretch")
                    last_log = curr_time

        cap.release()