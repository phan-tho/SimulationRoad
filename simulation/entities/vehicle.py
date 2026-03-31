import pygame
from simulation.config import config
import math

class Vehicle(pygame.sprite.Sprite):
    """
    Lớp Vehicle có khả năng nhận biết và dừng lại trước đèn đỏ.
    """
    def __init__(self, lane, speed=2):
        super().__init__()
        self.lane = lane
        self.direction = lane.direction
        self.default_speed = speed
        self.speed = speed
        self.safe_distance = 10 # Ngưỡng an toàn để dừng trước vạch

        # Thiết lập hình ảnh và rect
        image_size = (15, 30) if self.direction in ['N', 'S'] else (30, 15)
        self.image = pygame.Surface(image_size)
        self.image.fill(config.get('COLORS')['BLUE'])
        self.rect = self.image.get_rect(center=self.lane.start_pos)

    @property
    def front_position(self):
        """Trả về tọa độ của mũi xe."""
        if self.direction == 'E':
            return self.rect.midright
        if self.direction == 'W':
            return self.rect.midleft
        if self.direction == 'S':
            return self.rect.midbottom
        if self.direction == 'N':
            return self.rect.midtop
        return self.rect.center

    def check_stop_conditions(self, intersections):
        """
        Kiểm tra xem có cần dừng lại vì đèn đỏ không.
        Trả về True nếu cần dừng, False nếu không.
        """
        for stop_line_pos in self.lane.stop_line_positions:
            # Tính khoảng cách từ mũi xe đến vạch dừng tiếp theo
            dist_to_stop_line = math.hypot(
                self.front_position[0] - stop_line_pos[0],
                self.front_position[1] - stop_line_pos[1]
            )

            # Chỉ xét vạch dừng ở phía trước xe
            in_front = False
            if self.direction == 'E' and stop_line_pos[0] > self.front_position[0]: in_front = True
            elif self.direction == 'W' and stop_line_pos[0] < self.front_position[0]: in_front = True
            elif self.direction == 'S' and stop_line_pos[1] > self.front_position[1]: in_front = True
            elif self.direction == 'N' and stop_line_pos[1] < self.front_position[1]: in_front = True

            if in_front and dist_to_stop_line < self.safe_distance:
                # Tìm ngã tư tương ứng với vạch dừng này
                for intersection in intersections:
                    if intersection.rect.collidepoint(stop_line_pos):
                        # Lấy đèn cho làn của xe (đèn đi thẳng hoặc rẽ)
                        # Tạm thời lấy đèn đầu tiên cho hướng này
                        light = intersection.get_light_for_direction(self.direction)[0] 
                        if light and light.state == 'RED':
                            return True # Cần dừng lại
        return False # Không cần dừng

    def move(self):
        """Di chuyển xe thẳng theo hướng của nó."""
        if self.direction == 'E':
            self.rect.x += self.speed
        elif self.direction == 'W':
            self.rect.x -= self.speed
        elif self.direction == 'S':
            self.rect.y += self.speed
        elif self.direction == 'N':
            self.rect.y -= self.speed
    
    def update(self, intersections):
        """Cập nhật trạng thái của xe."""
        if self.check_stop_conditions(intersections):
            self.speed = 0
        else:
            self.speed = self.default_speed
        
        self.move()

    def is_out_of_bounds(self, width, height):
        """Kiểm tra xem xe đã ra khỏi màn hình chưa."""
        return not pygame.Rect(0, 0, width, height).colliderect(self.rect)
