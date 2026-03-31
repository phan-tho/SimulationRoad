import pygame
import random
from simulation.config import config
from simulation.entities.vehicle import Vehicle 

class SimulationController:
    def __init__(self, screen, roads, intersections):
        self.screen = screen
        self.roads = roads
        self.intersections = intersections
        self.vehicles = pygame.sprite.Group()
        self.width = config.get('WINDOW_WIDTH')
        self.height = config.get('WINDOW_HEIGHT')

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

    def spawn_vehicles(self):
        """Chức năng này đã bị vô hiệu hóa."""
        pass

    def enforce_rules(self):
        """Kiểm tra các quy tắc cho xe."""
        for vehicle in self.vehicles:
            # 1. Xóa xe khi ra khỏi màn hình
            if vehicle.is_out_of_bounds(self.width, self.height):
                vehicle.kill() 
            
            # 2. Logic dừng đèn đỏ được chuyển vào trong `vehicle.update`
            # nên không cần gọi ở đây nữa.

    def update(self):
        """Cập nhật trạng thái của tất cả các xe."""
        # Cung cấp danh sách ngã tư cho mỗi xe để kiểm tra đèn
        self.vehicles.update(self.intersections)


    def draw(self):
        """Vẽ tất cả các xe lên màn hình."""
        self.vehicles.draw(self.screen)
