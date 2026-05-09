// File: arduino_firmware/relay_controller.ino

// 1. Khai báo chân cắm Relay
const int HEATER_PIN = 26; // Chân điều khiển Đèn sưởi
const int FAN_PIN = 27;    // Chân điều khiển Quạt hút

void setup() {
  // Mở cổng giao tiếp Serial với tốc độ 9600 (Trùng khớp với Python)
  Serial.begin(9600);
  
  pinMode(HEATER_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  
  // Mặc định tắt các thiết bị khi mới khởi động
  digitalWrite(HEATER_PIN, LOW);
  digitalWrite(FAN_PIN, LOW);
}

void loop() {
  // Kiểm tra xem Python có gửi lệnh nào xuống không
  if (Serial.available() > 0) {
    // Đọc lệnh cho đến khi gặp dấu xuống dòng (\n)
    String command = Serial.readStringUntil('\n');
    command.trim(); // Xóa khoảng trắng thừa

    // Xử lý lệnh từ Python
    if (command == "HEATER_ON") {
      digitalWrite(HEATER_PIN, HIGH);
    } 
    else if (command == "HEATER_OFF") {
      digitalWrite(HEATER_PIN, LOW);
    } 
    else if (command == "FAN_ON") {
      digitalWrite(FAN_PIN, HIGH);
    } 
    else if (command == "FAN_OFF") {
      digitalWrite(FAN_PIN, LOW);
    }
  }
}