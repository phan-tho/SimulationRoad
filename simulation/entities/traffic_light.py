import pygame
from simulation.config import config

class TrafficLight:
    """Đại diện cho một cột đèn tín hiệu cho một làn hoặc một hành động cụ thể."""
    def __init__(self, screen, position, light_type='straight'):
        self.screen = screen
        self.position = position
        self.light_type = light_type # 'straight', 'left'
        self.state = 'RED'
        self.colors = {
            "RED": config.get('COLORS')['RED'],
            "YELLOW": config.get('COLORS')['YELLOW'],
            "GREEN": config.get('COLORS')['GREEN']
        }
        self.radius = 7

    def draw(self):
        # Tạm thời vẫn vẽ hình tròn, sau này có thể đổi thành mũi tên
        pygame.draw.circle(self.screen, self.colors[self.state], self.position, self.radius)

    def update_state(self, new_state):
        self.state = new_state

class Intersection:
    """Quản lý các cụm đèn và logic tại một ngã tư."""
    def __init__(self, screen, intersection_id, center_pos, size=120):
        self.screen = screen
        self.id = intersection_id
        self.center = center_pos
        self.size = size
        self.rect = pygame.Rect(center_pos[0] - size / 2, center_pos[1] - size / 2, size, size)
        
        self.traffic_lights = self._create_lights()

    def _create_lights(self):
        """Tạo các đèn cho mỗi hướng, bao gồm đèn đi thẳng và rẽ trái."""
        lights = {'N': [], 'S': [], 'E': [], 'W': []}
        lane_width = 20
        num_lanes = 3 # Hardcode to match road
        
        # Đèn cho hướng Nam (đi từ trên xuống)
        base_x_s = self.center[0] + lane_width * 0.5
        base_y_s = self.center[1] - self.size / 2 - 15
        lights['S'].append(TrafficLight(self.screen, (base_x_s, base_y_s), 'left'))
        lights['S'].append(TrafficLight(self.screen, (base_x_s + lane_width, base_y_s), 'straight'))
        lights['S'].append(TrafficLight(self.screen, (base_x_s + lane_width*2, base_y_s), 'straight'))

        # Đèn cho hướng Bắc (đi từ dưới lên)
        base_x_n = self.center[0] - lane_width * 2.5
        base_y_n = self.center[1] + self.size / 2 + 15
        lights['N'].append(TrafficLight(self.screen, (base_x_n, base_y_n), 'straight'))
        lights['N'].append(TrafficLight(self.screen, (base_x_n + lane_width, base_y_n), 'straight'))
        lights['N'].append(TrafficLight(self.screen, (base_x_n + lane_width*2, base_y_n), 'left'))

        # Đèn cho hướng Tây (đi từ phải sang trái)
        base_x_w = self.center[0] + self.size / 2 + 15
        base_y_w = self.center[1] + lane_width * 0.5
        lights['W'].append(TrafficLight(self.screen, (base_x_w, base_y_w), 'left'))
        lights['W'].append(TrafficLight(self.screen, (base_x_w, base_y_w + lane_width), 'straight'))
        lights['W'].append(TrafficLight(self.screen, (base_x_w, base_y_w + lane_width*2), 'straight'))

        # Đèn cho hướng Đông (đi từ trái sang phải)
        base_x_e = self.center[0] - self.size / 2 - 15
        base_y_e = self.center[1] - lane_width * 2.5
        lights['E'].append(TrafficLight(self.screen, (base_x_e, base_y_e), 'straight'))
        lights['E'].append(TrafficLight(self.screen, (base_x_e, base_y_e + lane_width), 'straight'))
        lights['E'].append(TrafficLight(self.screen, (base_x_e, base_y_e + lane_width*2), 'left'))

        return lights

    def draw(self):
        for direction_lights in self.traffic_lights.values():
            for light in direction_lights:
                light.draw()

    def update_state(self, new_state_map):
        """
        Cập nhật trạng thái các đèn.
        Ví dụ: new_state_map = {"N-S": {"straight": "GREEN", "left": "RED"}, "E-W": ...}
        """
        state_ns = new_state_map.get("N-S", {"straight": "RED", "left": "RED"})
        state_ew = new_state_map.get("E-W", {"straight": "RED", "left": "RED"})

        for light in self.traffic_lights['N'] + self.traffic_lights['S']:
            light.update_state(state_ns.get(light.light_type, "RED"))
        
        for light in self.traffic_lights['E'] + self.traffic_lights['W']:
            light.update_state(state_ew.get(light.light_type, "RED"))

    def get_light_for_direction(self, direction):
        return self.traffic_lights.get(direction)
