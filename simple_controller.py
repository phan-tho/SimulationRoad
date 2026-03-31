import paho.mqtt.client as mqtt
import time
import json

# --- Cấu hình ---
# MQTT_BROKER = "localhost"
# MQTT_PORT = 1883
# MQTT_TOPIC = "traffic/control" 
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "local/simulation/control"

# --- Các trạng thái đèn ---
TRAFFIC_LIGHT_STATES = [
    {"N-S": {"straight": "GREEN", "left": "GREEN"}, "E-W": {"straight": "RED", "left": "RED"}},
    {"N-S": {"straight": "RED", "left": "RED"}, "E-W": {"straight": "GREEN", "left": "GREEN"}},
]

def create_mqtt_client():
    """Tạo và kết nối MQTT client."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "SimpleController")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"Đã kết nối thành công đến MQTT Broker tại {MQTT_BROKER}:{MQTT_PORT}")
        return client
    except ConnectionRefusedError:
        print(f"LỖI: Không thể kết nối đến MQTT Broker. Hãy đảm bảo broker đang chạy.")
        return None
    except Exception as e:
        print(f"Lỗi không xác định khi kết nối MQTT: {e}")
        return None

def main():
    """Vòng lặp chính để gửi lệnh điều khiển."""
    client = create_mqtt_client()
    if not client:
        return

    client.loop_start()

    current_state_index = 0
    try:
        while True:
            # Đảo trạng thái đèn
            current_state_index = 1 - current_state_index
            new_state = TRAFFIC_LIGHT_STATES[current_state_index]
            
            print(f"\n--- Gửi lệnh cập nhật cho TẤT CẢ các ngã tư ---")
            print(f"Trạng thái mới: N-S: {new_state['N-S']['straight']}, E-W: {new_state['E-W']['straight']}")

            # Gửi lệnh cho tất cả 4 ngã tư
            for i in range(4):
                command = {
                    "type": "UPDATE_INTERSECTION_STATE",
                    "intersection_id": i,
                    "state": new_state
                }
                client.publish(MQTT_TOPIC, json.dumps(command))
            
            # Chờ 5 giây
            print("Chờ 15 giây...")
            time.sleep(3)

    except KeyboardInterrupt:
        print("\nĐã nhận tín hiệu dừng. Ngắt kết nối...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("Đã ngắt kết nối MQTT và thoát.")

if __name__ == '__main__':
    main()
