import paho.mqtt.client as mqtt
import time
import json
import random

# --- Cấu hình ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "local/simulation/control"

# --- Các trạng thái có thể có ---
TRAFFIC_LIGHT_STATES = [
    {"N-S": "GREEN", "E-W": "RED"},
    {"N-S": "RED", "E-W": "GREEN"},
]
LANE_RATIOS = ["1:3", "3:1", "2:2"]
ROAD_IDS = ["road_H1", "road_H2", "road_V1", "road_V2"] # Giả sử các ID đường này tồn tại

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

def build_traffic_light_command():
    """Tạo lệnh đổi đèn ngẫu nhiên."""
    intersection_id = random.randint(0, 3)  # Có 4 ngã tư, từ 0 đến 3
    new_state = random.choice(TRAFFIC_LIGHT_STATES)
    command = {
        "type": "traffic_light",
        "intersection_id": intersection_id,
        "state": new_state
    }
    return command

def build_lane_shift_command():
    """Tạo lệnh đổi làn ngẫu nhiên."""
    road_id = random.choice(ROAD_IDS)
    new_ratio = random.choice(LANE_RATIOS)
    command = {
        "type": "lane_shift",
        "road_id": road_id,
        "ratio": new_ratio
        # "shift_direction" có thể được suy ra từ "ratio" trong Pygame
    }
    return command

def main():
    """Vòng lặp chính để gửi lệnh điều khiển."""
    client = create_mqtt_client()
    if not client:
        return

    client.loop_start() # Bắt đầu một luồng riêng để xử lý mạng

    try:
        while True:
            # Chờ một khoảng thời gian ngẫu nhiên từ 5 đến 15 giây
            sleep_time = random.uniform(5, 15)
            print(f"\nChờ {sleep_time:.1f} giây trước khi gửi lệnh tiếp theo...")
            time.sleep(sleep_time)

            # Ngẫu nhiên chọn một hành động: đổi đèn hoặc đổi làn
            action = random.choice(['traffic_light', 'lane_shift'])

            if action == 'traffic_light':
                command = build_traffic_light_command()
                print(f"Gửi lệnh ĐỔI ĐÈN: Ngã tư {command['intersection_id']} -> {command['state']}")
            else:
                # Hiện tại, logic đổi làn chưa được cài đặt đầy đủ trong Pygame,
                # nhưng chúng ta vẫn gửi lệnh để kiểm tra luồng dữ liệu.
                command = build_lane_shift_command()
                print(f"Gửi lệnh ĐỔI LÀN: Đường {command['road_id']} -> Tỷ lệ {command['ratio']}")

            # Publish lệnh dưới dạng chuỗi JSON
            client.publish(MQTT_TOPIC, json.dumps(command))

    except KeyboardInterrupt:
        print("\nĐã nhận tín hiệu dừng. Ngắt kết nối...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("Đã ngắt kết nối MQTT và thoát.")

if __name__ == '__main__':
    main()
