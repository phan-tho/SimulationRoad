import pygame
from simulation.config import config
import math


CRUISE = "CRUISE"
BRAKE_FOR_LIGHT = "BRAKE_FOR_LIGHT"
QUEUED = "QUEUED"
ACCELERATE = "ACCELERATE"


class Vehicle(pygame.sprite.Sprite):
    """
    Lớp Vehicle có khả năng nhận biết và dừng lại trước đèn đỏ.
    """
    def __init__(self, lane, speed=2, route_plan="straight"):
        super().__init__()
        self.lane = lane
        self.direction = lane.direction
        self.default_speed = speed
        self.speed = speed
        self.safe_distance = 10 # Backward-compatible default; dynamic gap used below.
        self.state = CRUISE
        self.accel_step = 1
        self.accel_target_speed = self.default_speed
        self.route_plan = route_plan
        self.has_turned = False
        self._normalize_route_for_lane()

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

    @property
    def min_following_gap(self):
        """
        Safe center-to-center gap in same lane.
        Uses vehicle size to avoid tailgating/overlap.
        """
        vehicle_length = max(self.rect.width, self.rect.height)
        return vehicle_length + 1

    def _normalize_route_for_lane(self):
        """
        Step 4: lane validity for turning.
        - left turn only from innermost lane (index 0)
        - right turn only from outermost lane (last index)
        If invalid, fallback to straight.
        """
        lane_index = getattr(self.lane, "lane_index", None)
        lanes_per_direction = getattr(self.lane, "lanes_per_direction", 3)
        if lane_index is None:
            return

        if self.route_plan == "left" and lane_index != 0:
            self.route_plan = "straight"
        elif self.route_plan == "right" and lane_index != (lanes_per_direction - 1):
            self.route_plan = "straight"

    def _distance_to_stop_line_along_direction(self, stop_line_pos):
        """Signed distance to stop line along movement axis."""
        if self.direction == 'E':
            return stop_line_pos[0] - self.front_position[0]
        if self.direction == 'W':
            return self.front_position[0] - stop_line_pos[0]
        if self.direction == 'S':
            return stop_line_pos[1] - self.front_position[1]
        if self.direction == 'N':
            return self.front_position[1] - stop_line_pos[1]
        return float("inf")

    def check_stop_conditions(self, intersections):
        """
        Kiểm tra xem có cần dừng lại vì đèn đỏ không.
        Trả về True nếu cần dừng, False nếu không.
        """
        # Pick nearest stop line ahead on current lane.
        ahead_stop_lines = []
        for stop_line_pos in self.lane.stop_line_positions:
            axis_distance = self._distance_to_stop_line_along_direction(stop_line_pos)
            if axis_distance > 0:
                ahead_stop_lines.append((axis_distance, stop_line_pos))

        if not ahead_stop_lines:
            return False

        dist_to_next_line, next_stop_line = min(ahead_stop_lines, key=lambda item: item[0])

        # Map stop line to nearest intersection center (robust for border positions).
        nearest_intersection = min(
            intersections,
            key=lambda it: math.hypot(it.center[0] - next_stop_line[0], it.center[1] - next_stop_line[1]),
        ) if intersections else None

        if not nearest_intersection:
            return False

        lights = nearest_intersection.get_light_for_direction(self.direction) or []
        light = lights[0] if lights else None
        if not light or light.state not in ('RED', 'YELLOW'):
            return False

        # Stop very close to line, but still before crossing.
        stopping_zone = max(self.default_speed + 2, 4)
        if dist_to_next_line <= stopping_zone:
            return True
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

    def _same_lane(self, other):
        return other is not self and other.lane is self.lane

    def _ahead_on_same_lane(self, other):
        if not self._same_lane(other):
            return False
        if self.direction == 'E':
            return other.rect.centerx > self.rect.centerx
        if self.direction == 'W':
            return other.rect.centerx < self.rect.centerx
        if self.direction == 'S':
            return other.rect.centery > self.rect.centery
        if self.direction == 'N':
            return other.rect.centery < self.rect.centery
        return False

    def _distance_to(self, other):
        return math.hypot(
            other.rect.centerx - self.rect.centerx,
            other.rect.centery - self.rect.centery,
        )

    def adjust_speed_for_lead_vehicle(self, all_vehicles):
        """
        Car-following rule for vehicles in the same lane.
        If lead vehicle is too close, match/stop to avoid collision.
        """
        leaders = [v for v in all_vehicles if self._ahead_on_same_lane(v)]
        if not leaders:
            return self.default_speed

        lead = min(leaders, key=self._distance_to)
        distance = self._distance_to(lead)

        follow_gap = self.min_following_gap
        if distance <= follow_gap:
            return 0
        if distance <= follow_gap * 1.3:
            return min(self.default_speed, lead.speed)
        return self.default_speed

    def _apply_acceleration(self):
        if self.speed < self.accel_target_speed:
            self.speed = min(self.speed + self.accel_step, self.accel_target_speed)
            self.state = ACCELERATE
        else:
            self.speed = self.default_speed
            self.state = CRUISE

    def _next_direction_from_turn(self):
        if self.route_plan == "straight":
            return self.direction

        turn_map = {
            "E": {"left": "N", "right": "S"},
            "W": {"left": "S", "right": "N"},
            "N": {"left": "E", "right": "W"},
            "S": {"left": "W", "right": "E"},
        }
        return turn_map.get(self.direction, {}).get(self.route_plan, self.direction)

    def _apply_direction_geometry(self):
        """Keep vehicle body aligned with current direction."""
        center = self.rect.center
        image_size = (15, 30) if self.direction in ['N', 'S'] else (30, 15)
        self.image = pygame.Surface(image_size)
        self.image.fill(config.get('COLORS')['BLUE'])
        self.rect = self.image.get_rect(center=center)

    def _select_target_lane_after_turn(self, turned_intersection, roads):
        if not roads:
            return None

        candidate_road = None
        if self.direction in ("N", "S"):
            candidate_road = min(
                roads.values(),
                key=lambda road: abs(road.start[0] - turned_intersection.center[0]) if not road.is_horizontal else float("inf"),
            )
        else:
            candidate_road = min(
                roads.values(),
                key=lambda road: abs(road.start[1] - turned_intersection.center[1]) if road.is_horizontal else float("inf"),
            )

        if not candidate_road:
            return None

        lanes = candidate_road.get_spawn_lanes(self.direction) or []
        if not lanes:
            return None

        # Keep lane position consistent: left turn -> inner lane, right turn -> outer lane.
        if self.route_plan == "left":
            return lanes[0]
        if self.route_plan == "right":
            return lanes[-1]
        return lanes[min(1, len(lanes) - 1)]

    def _snap_to_lane_center(self):
        if self.direction in ("E", "W"):
            self.rect.centery = int(self.lane.start_pos[1])
        else:
            self.rect.centerx = int(self.lane.start_pos[0])

    def _try_turn_at_intersection(self, intersections, roads):
        if self.has_turned or self.route_plan == "straight":
            return

        for intersection in intersections:
            if intersection.rect.collidepoint(self.rect.center):
                self.direction = self._next_direction_from_turn()
                target_lane = self._select_target_lane_after_turn(intersection, roads)
                if target_lane is not None:
                    self.lane = target_lane
                self.has_turned = True
                self._apply_direction_geometry()
                self._snap_to_lane_center()
                break
    
    def update(self, intersections, all_vehicles, roads=None):
        """Cập nhật trạng thái của xe."""
        speed_for_car_following = self.adjust_speed_for_lead_vehicle(all_vehicles)
        must_stop_for_light = self.check_stop_conditions(intersections)

        if must_stop_for_light:
            self.speed = 0
            if speed_for_car_following == 0:
                self.state = QUEUED
            else:
                self.state = BRAKE_FOR_LIGHT
        else:
            if speed_for_car_following == 0:
                self.speed = 0
                self.state = QUEUED
            elif self.speed < self.default_speed:
                self._apply_acceleration()
            else:
                self.speed = speed_for_car_following
                if self.speed < self.default_speed:
                    self.state = ACCELERATE
                else:
                    self.state = CRUISE
        
        self.move()
        self._try_turn_at_intersection(intersections, roads)

    def is_out_of_bounds(self, width, height):
        """Kiểm tra xem xe đã ra khỏi màn hình chưa."""
        return not pygame.Rect(0, 0, width, height).colliderect(self.rect)
