<h2 align="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
    🎓 Faculty of Information Technology (Dai Nam University)
    </a>
</h2>

<h2 align="center">
   Hệ Thống Giám Sát Hành Vi Của Lợn
</h2>

<div align="center">
    <p align="center">
        <img src="https://github.com/user-attachments/assets/ee72b1c4-04c7-4e4b-8d7a-8cf16932804a" width="170" />
        <img src="https://github.com/user-attachments/assets/1459f5bf-7fc9-4462-996d-eb1ef7633a97" width="180" />
        <img src="https://github.com/user-attachments/assets/f081d02c-b644-4e87-a40c-fcb8383c2985" width="200" />
    </p>

[![AIoTLab](https://img.shields.io/badge/AIoTLab-green?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Faculty of Information Technology](https://img.shields.io/badge/Faculty%20of%20Information%20Technology-blue?style=for-the-badge)](https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-orange?style=for-the-badge)](https://dainam.edu.vn)

</div>

---

## 1. Giới thiệu Dự án

<div align="justify">
Đây là hệ thống Giám sát Nông nghiệp Thông minh (Smart Pig Farm) được phát triển theo triết lý "vibe coding" trong khuôn khổ học phần môn Công nghệ Xử lý ảnh. 

Mục đích chính của dự án là nghiên cứu và ứng dụng mô hình AI (YOLO) vào việc theo dõi hành vi vật nuôi trong thời gian thực, kết hợp với các cảm biến IoT mô phỏng để tự động hóa môi trường chuồng trại. 

Dự án là bước đệm vững chắc để tiến tới xây dựng các giải pháp tự động hóa toàn diện trong mô hình Nông nghiệp công nghệ cao (Smart Agriculture).
</div>

---

## 2. Bối cảnh & Vấn đề thực tiễn

<div align="justify">
Trong chăn nuôi quy mô công nghiệp, việc theo dõi sức khỏe và hành vi của vật nuôi đòi hỏi rất nhiều nhân lực. Môi trường chuồng trại khép kín nếu không được kiểm soát tốt (nhiệt độ quá lạnh, nồng độ khí độc Amoniac tăng cao) sẽ dẫn đến dịch bệnh và giảm năng suất.

Dự án này ra đời nhằm giải quyết bài toán đó. Hệ thống hoạt động như một người quản lý 24/7, có khả năng "nhìn" qua camera để đếm số lượng, phân tích hành vi (ăn, ngủ, di chuyển) và tự động kích hoạt các thiết bị phần cứng (Quạt hút, Đèn sưởi) khi phát hiện môi trường có dấu hiệu bất thường.
</div>

---

## 3. Demo

<img width="100%" src="https://github.com/user-attachments/assets/placeholder_demo1.png">
<img width="100%" src="https://github.com/user-attachments/assets/placeholder_demo2.png">

*Video demo: [Xem video hệ thống hoạt động](https://github.com/user-attachments/assets/placeholder_video.mp4)*

> **Lưu ý:** Đừng quên thay thế các link placeholder ở trên bằng link ảnh/video thật của hệ thống nhé!

---

## 4. Tính năng cốt lõi

Hệ thống kết hợp giữa Computer Vision và IoT Dashboard với các tính năng chính:

- **Phân tích hành vi (AI Tracking)**: Ứng dụng YOLO theo dõi và phân loại chính xác 3 trạng thái của lợn: EAT (Đang ăn), SLEEP (Đang ngủ), MOVE (Đang di chuyển).
- **Thuật toán Custom NMS**: Khắc phục triệt để lỗi phân mảnh Bounding Box (1 vật nuôi bị nhận diện thành 2 ID) do rung lắc camera.
- **Vùng nhận diện (ROI)**: Cấu hình vùng máng cám linh hoạt để tăng độ chính xác khi nhận diện hành vi EAT.
- **Tự động hóa IoT**: Giám sát thông số Nhiệt độ và Khí Gas, tự động ra quyết định bật/tắt thiết bị dựa trên tập tính vật nuôi.
- **Cảnh báo Telegram**: Gửi báo cáo theo thời gian thực về điện thoại người quản lý kèm theo cơ chế chống Spam (Cooldown).
- **Ghi log Database**: Trích xuất toàn bộ lịch sử hoạt động và trạng thái môi trường ra file Excel để phân tích.

---

## 5. Logic điều khiển thiết bị (State Machine)

Hệ thống sử dụng cỗ máy trạng thái để so sánh và ra quyết định chính xác:

| Sự kiện / Điều kiện | Cảnh báo Telegram | Hành động hệ thống |
| :--- | :--- | :--- |
| **Can thiệp thủ công** | Báo cáo chi tiết lệnh Bật/Tắt | Ghi đè tự động, ưu tiên thực thi ngay lập tức |
| **Khí Gas > Ngưỡng** (VD: 300 PPM) | ☠️ Báo động môi trường khí độc | Tự động BẬT Quạt hút |
| **Nhiệt độ > Ngưỡng** (VD: 40°C) | 🔥 Báo động nhiệt độ cao | Tự động BẬT Quạt hút |
| **Nhiệt độ < Ngưỡng** (VD: 20°C) VÀ Lợn tụ tập | ❄️ Báo động tập tính (Tụ tập do lạnh) | Tự động BẬT Đèn sưởi |
| **Các chỉ số trở về bình thường** | 🔴 Thông báo ngắt lệnh tự động | Tự động TẮT các thiết bị |

---

## 6. Công nghệ sử dụng

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=fff)](https://streamlit.io/)
[![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=fff)](https://opencv.org/)
[![YOLO](https://img.shields.io/badge/YOLO-Ultralytics-00FFFF?logo=databricks&logoColor=000)](https://ultralytics.com/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=fff)](https://pandas.pydata.org/)

---

## 7. Cấu trúc project

```text
CNXLA_BTL_Smart_Pig_Farm/
├── dashboard.py         # File chính giao diện Streamlit & Logic hệ thống
├── models/
│   └── best.pt          # File weights mô hình YOLO đã huấn luyện
├── videos/              # Thư mục chứa video đầu vào để test hệ thống
├── outputs/             # Thư mục lưu trữ database xuất ra
│   └── nhat_ky_chuong_lon.xlsx
├── .env.example         # File mẫu chứa cấu hình biến môi trường
├── .gitignore           # Cấu hình bỏ qua file cho Git
├── requirements.txt     # Danh sách thư viện cần thiết
└── README.md            # Tài liệu dự án
