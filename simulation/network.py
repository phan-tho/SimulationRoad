import threading
import json
import socket
import paho.mqtt.client as mqtt

class NetworkListener:
    def __init__(self, global_state, use_mqtt=True):
        self.global_state = global_state
        self.use_mqtt = use_mqtt
        if use_mqtt:
            # Sử dụng CallbackAPIVersion.VERSION1 để tương thích với paho-mqtt v2.x.x
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('localhost', 12345))

        self.thread = threading.Thread(target=self.listen, daemon=True)

    def start(self):
        self.thread.start()

    def listen(self):
        if self.use_mqtt:
            try:
                self.client.connect("localhost", 1883, 60)
                self.client.loop_forever()
            except ConnectionRefusedError:
                print("LỖI (Pygame): Không thể kết nối đến MQTT Broker. Bỏ qua network listener.")
            except Exception as e:
                print(f"Lỗi không xác định trong Network Listener: {e}")
        else: # UDP
            while True:
                data, addr = self.sock.recvfrom(1024)
                self.process_message(data.decode())

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT Broker with result code "+str(rc))
        client.subscribe("local/simulation/control")

    def on_message(self, client, userdata, msg):
        self.process_message(msg.payload.decode())

    def process_message(self, payload):
        print("Hello, I am processor")
        try:
            data = json.loads(payload)
            print(f"Received command: {data}")
            if data['type'] == 'UPDATE_INTERSECTION_STATE':
                intersection_id = data['intersection_id']
                new_state = data['state']

                print(f"Updating intersection {intersection_id} with new state: {new_state}")

                # Tìm đúng ngã tư và cập nhật
                if 0 <= intersection_id < len(self.global_state['intersections']):
                    self.global_state['intersections'][intersection_id].update_state(new_state)
            elif data['type'] == 'lane_shift':
                road_id = data['road_id']
                new_ratio = data['ratio']
                if road_id in self.global_state['dynamic_dividers']:
                    self.global_state['dynamic_dividers'][road_id].shift_divider(new_ratio)
        except json.JSONDecodeError:
            print("Error decoding JSON")
        except KeyError as e:
            print(f"Missing key in payload: {e}")

