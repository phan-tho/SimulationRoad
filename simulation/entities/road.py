import pygame
from simulation.config import config

def draw_dashed_line(surface, color, start_pos, end_pos, width=1, dash_length=10, space_length=5):
    """Vẽ một đường nét đứt."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    dl = dash_length
    sl = space_length
    
    if x1 == x2: # Vertical line
        for y in range(y1, y2, dl + sl):
            pygame.draw.line(surface, color, (x1, y), (x1, min(y + dl, y2)), width)
    elif y1 == y2: # Horizontal line
        for x in range(x1, x2, dl + sl):
            pygame.draw.line(surface, color, (x, y1), (min(x + dl, x2), y1), width)

class Lane:
    """Đại diện cho một làn đường duy nhất."""
    def __init__(self, start_pos, end_pos, direction, stop_line_positions):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.direction = direction
        self.stop_line_positions = stop_line_positions # Đây giờ là một danh sách

class Road:
    """Đại diện cho một con đường, chứa nhiều làn đường."""
    def __init__(self, screen, road_id, start, end, num_lanes_per_direction=3):
        self.screen = screen
        self.road_id = road_id
        self.start = start
        self.end = end
        self.num_lanes_per_direction = num_lanes_per_direction
        self.total_lanes = num_lanes_per_direction * 2
        self.lane_width = 20
        self.is_horizontal = start[1] == end[1]
        
        self.lanes = self._create_lanes()
        self.divider_offset = 0

    def _create_lanes(self):
        """
        Tạo ra các đối tượng Lane. Mỗi Lane giờ đây có một danh sách các vạch dừng,
        một vạch cho mỗi ngã tư mà nó đi qua. Sửa lỗi vạch dừng cho làn dọc.
        """
        lanes = {'E': [], 'W': [], 'S': [], 'N': []}
        stop_line_margin = 60
        w = config.get('WINDOW_WIDTH')
        h = config.get('WINDOW_HEIGHT')
        all_intersections = [{'x': int(rc['x'] * w), 'y': int(rc['y'] * h)} for rc in config.get('INTERSECTION_COORDS_RELATIVE')]

        if self.is_horizontal:
            center_y = self.start[1]
            relevant_intersections = sorted([ic for ic in all_intersections if ic['y'] == center_y], key=lambda item: item['x'])
            
            # Làn đi về hướng ĐÔNG (E) - từ trái sang phải, dừng TRƯỚC các ngã tư
            stop_positions_e = [(ic['x'] - stop_line_margin, center_y) for ic in relevant_intersections]
            for i in range(self.num_lanes_per_direction):
                y = center_y + (i * self.lane_width) + self.lane_width / 2
                current_lane_stop_positions = [(pos[0], y) for pos in stop_positions_e]
                lanes['E'].append(Lane((self.start[0], y), (self.end[0], y), 'E', current_lane_stop_positions))

            # Làn đi về hướng TÂY (W) - từ phải sang trái, dừng TRƯỚC các ngã tư
            stop_positions_w = [(ic['x'] + stop_line_margin, center_y) for ic in relevant_intersections]
            for i in range(self.num_lanes_per_direction):
                y = center_y - (i * self.lane_width) - self.lane_width / 2
                current_lane_stop_positions = [(pos[0], y) for pos in stop_positions_w]
                lanes['W'].append(Lane((self.end[0], y), (self.start[0], y), 'W', current_lane_stop_positions))
        else: # Vertical
            center_x = self.start[0]
            relevant_intersections = sorted([ic for ic in all_intersections if ic['x'] == center_x], key=lambda item: item['y'])

            # Làn đi về hướng NAM (S) - từ trên xuống dưới, dừng TRƯỚC các ngã tư
            # Các làn này nằm ở BÊN PHẢI của đường (x > center_x)
            stop_positions_s = [(center_x, ic['y'] - stop_line_margin) for ic in relevant_intersections]
            for i in range(self.num_lanes_per_direction):
                x = center_x - (i * self.lane_width) - self.lane_width / 2
                current_lane_stop_positions = [(x, pos[1]) for pos in stop_positions_s]
                lanes['S'].append(Lane((x, self.start[1]), (x, self.end[1]), 'S', current_lane_stop_positions))

            # Làn đi về hướng BẮC (N) - từ dưới lên trên, dừng TRƯỚC các ngã tư
            # Các làn này nằm ở BÊN TRÁI của đường (x < center_x)
            stop_positions_n = [(center_x, ic['y'] + stop_line_margin) for ic in relevant_intersections]
            for i in range(self.num_lanes_per_direction):
                x = center_x + (i * self.lane_width) + self.lane_width / 2
                current_lane_stop_positions = [(x, pos[1]) for pos in stop_positions_n]
                lanes['N'].append(Lane((x, self.end[1]), (x, self.start[1]), 'N', current_lane_stop_positions))
        return lanes

    def draw(self):
        """Vẽ mặt đường, dải phân cách, và các vạch kẻ làn."""
        road_rect_width = self.total_lanes * self.lane_width
        
        # Vẽ mặt đường
        if self.is_horizontal:
            # Mở rộng vùng vẽ để bao phủ toàn bộ chiều rộng màn hình
            road_surface = pygame.Rect(0, self.start[1] - road_rect_width / 2, config.get('WINDOW_WIDTH'), road_rect_width)
        else:
            # Mở rộng vùng vẽ để bao phủ toàn bộ chiều cao màn hình
            road_surface = pygame.Rect(self.start[0] - road_rect_width / 2, 0, road_rect_width, config.get('WINDOW_HEIGHT'))
        pygame.draw.rect(self.screen, config.get('COLORS')['LIGHT_GRAY'], road_surface)

        # Vẽ vạch chia làn và vạch dừng
        self.draw_lane_markings()
        self.draw_stop_lines()

        # Vẽ dải phân cách vàng ở giữa
        if self.is_horizontal:
            divider_y = self.start[1] + self.divider_offset
            pygame.draw.line(self.screen, config.get('COLORS')['YELLOW'], (self.start[0], divider_y), (self.end[0], divider_y), 2)
        else:
            divider_x = self.start[0] + self.divider_offset
            pygame.draw.line(self.screen, config.get('COLORS')['YELLOW'], (divider_x, self.start[1]), (divider_x, self.end[1]), 2)

    def draw_lane_markings(self):
        """Vẽ các vạch trắng đứt để chia làn cùng chiều."""
        for direction_lanes in self.lanes.values():
            # Chỉ vẽ vạch chia giữa các làn, không vẽ vạch ngoài cùng
            for i in range(len(direction_lanes) - 1):
                lane1 = direction_lanes[i]
                lane2 = direction_lanes[i+1]
                if self.is_horizontal:
                    mid_y = (lane1.start_pos[1] + lane2.start_pos[1]) / 2
                    draw_dashed_line(self.screen, config.get('COLORS')['WHITE'], (self.start[0], mid_y), (self.end[0], mid_y))
                else:
                    mid_x = (lane1.start_pos[0] + lane2.start_pos[0]) / 2
                    draw_dashed_line(self.screen, config.get('COLORS')['WHITE'], (mid_x, self.start[1]), (mid_x, self.end[1]))

    def draw_stop_lines(self):
        """Vẽ TẤT CẢ các vạch dừng cho mỗi làn đường."""
        for direction_lanes in self.lanes.values():
            for lane in direction_lanes:
                # Duyệt qua danh sách các vị trí vạch dừng của làn
                for stop_pos in lane.stop_line_positions:
                    if self.is_horizontal:
                        start_pos = (stop_pos[0], lane.start_pos[1] - self.lane_width / 2)
                        end_pos = (stop_pos[0], lane.start_pos[1] + self.lane_width / 2)
                        pygame.draw.line(self.screen, config.get('COLORS')['WHITE'], start_pos, end_pos, 6)
                    else: # Vertical
                        start_pos = (lane.start_pos[0] - self.lane_width / 2, stop_pos[1])
                        end_pos = (lane.start_pos[0] + self.lane_width / 2, stop_pos[1])
                        pygame.draw.line(self.screen, config.get('COLORS')['WHITE'], start_pos, end_pos, 2)

    def get_spawn_lanes(self, direction):
        """Lấy các làn đường phù hợp để sinh xe dựa trên hướng."""
        return self.lanes.get(direction, [])

class DynamicDivider:
    def __init__(self, road_id):
        self.road_id = road_id
        self.ratio = "1:1"

    def shift_divider(self, new_ratio):
        self.ratio = new_ratio
        print(f"Yêu cầu đổi làn cho {self.road_id} thành {self.ratio}. Logic chưa được cài đặt.")
