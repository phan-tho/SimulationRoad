import pygame
from simulation.config import config
from simulation.entities.vehicle import Vehicle 
from simulation.state import SimulationState

class SimulationController:
    def __init__(self, screen, roads, intersections, state: SimulationState):
        self.screen = screen
        self.roads = roads
        self.intersections = intersections
        self.vehicles = pygame.sprite.Group()
        self.width = config.get('WINDOW_WIDTH')
        self.height = config.get('WINDOW_HEIGHT')
        self.state = state
        self.spawn_timer_seconds = 0.0
        self.spawn_interval_seconds = config.get("SPAWN_INTERVAL_SECONDS", 0.8)
        self.max_vehicles = config.get("MAX_VEHICLES", 40)
        self.spawn_min_gap = config.get("SPAWN_MIN_GAP", 24)
        self.route_probabilities = config.get(
            "ROUTE_PROBABILITIES",
            {"straight": 0.6, "left": 0.2, "right": 0.2},
        )

        self._create_one_vehicle()

    def _create_one_vehicle(self):
        """Hardcode tạo ra một chiếc xe duy nhất để thử nghiệm."""
        # Lấy làn đầu tiên của đường H1 đi hướng Đông
        target_road = self.roads.get("road_H1")
        if target_road:
            lanes_east = target_road.get_spawn_lanes('E')
            if lanes_east:
                first_lane_east = lanes_east[0]
                vehicle = Vehicle(first_lane_east, speed=3)
                self.vehicles.add(vehicle)

    def _distance_from_spawn(self, vehicle, lane):
        spawn_x, spawn_y = lane.start_pos
        return ((vehicle.rect.centerx - spawn_x) ** 2 + (vehicle.rect.centery - spawn_y) ** 2) ** 0.5

    def _can_spawn_in_lane(self, lane):
        lane_vehicles = [v for v in self.vehicles if v.lane is lane]
        if not lane_vehicles:
            return True
        closest = min(lane_vehicles, key=lambda v: self._distance_from_spawn(v, lane))
        return self._distance_from_spawn(closest, lane) >= self.spawn_min_gap

    def _spawn_vehicle_in_random_lane(self):
        all_lanes = []
        for road in self.roads.values():
            all_lanes.extend(road.get_spawn_lanes('E'))
            all_lanes.extend(road.get_spawn_lanes('W'))
            all_lanes.extend(road.get_spawn_lanes('S'))
            all_lanes.extend(road.get_spawn_lanes('N'))

        if not all_lanes:
            return

        lane = self.state.rng.choice(all_lanes)
        if not self._can_spawn_in_lane(lane):
            return

        speed = self.state.rng.choice([2, 3])
        route_plan = self._choose_route_for_lane(lane)
        self.vehicles.add(Vehicle(lane, speed=speed, route_plan=route_plan))

    def _choose_route_for_lane(self, lane):
        lane_index = getattr(lane, "lane_index", 1)
        lanes_per_direction = getattr(lane, "lanes_per_direction", 3)

        if lane_index == 0:
            options = [("left", self.route_probabilities.get("left", 0.2)), ("straight", self.route_probabilities.get("straight", 0.6))]
        elif lane_index == lanes_per_direction - 1:
            options = [("right", self.route_probabilities.get("right", 0.2)), ("straight", self.route_probabilities.get("straight", 0.6))]
        else:
            options = [("straight", 1.0)]

        total = sum(weight for _, weight in options)
        if total <= 0:
            return "straight"

        pick = self.state.rng.random() * total
        cumulative = 0.0
        for route, weight in options:
            cumulative += weight
            if pick <= cumulative:
                return route
        return options[-1][0]

    def spawn_vehicles(self, dt_seconds):
        """Spawn multiple vehicles with minimum lane headway."""
        if len(self.vehicles) >= self.max_vehicles:
            return

        self.spawn_timer_seconds += dt_seconds
        if self.spawn_timer_seconds < self.spawn_interval_seconds:
            return
        self.spawn_timer_seconds = 0.0
        self._spawn_vehicle_in_random_lane()

    def enforce_rules(self):
        """Kiểm tra các quy tắc cho xe."""
        for vehicle in self.vehicles:
            # 1. Xóa xe khi ra khỏi màn hình
            if vehicle.is_out_of_bounds(self.width, self.height):
                vehicle.kill() 
            
            # 2. Logic dừng đèn đỏ được chuyển vào trong `vehicle.update`
            # nên không cần gọi ở đây nữa.

    def _sense(self):
        """Gather runtime information for this frame."""
        return None

    def _decide(self, dt_seconds):
        """Compute frame decisions (kept as no-op for now)."""
        self.spawn_vehicles(dt_seconds)
        self.enforce_rules()

    def _act(self):
        """Apply movement updates to all vehicles."""
        # Cung cấp ngã tư và snapshot xe để car-following cùng làn.
        vehicles_snapshot = list(self.vehicles)
        for vehicle in vehicles_snapshot:
            vehicle.update(self.intersections, vehicles_snapshot, roads=self.roads)

    def _cleanup(self):
        """Sync frame outputs into state."""
        self.state.vehicles = self.vehicles

    def update(self, dt_seconds):
        """Frame pipeline: sense -> decide -> act -> cleanup."""
        self.state.tick(dt_seconds)
        self._sense()
        self._decide(dt_seconds)
        self._act()
        self._cleanup()

    def draw(self):
        """Vẽ tất cả các xe lên màn hình."""
        self.vehicles.draw(self.screen)
