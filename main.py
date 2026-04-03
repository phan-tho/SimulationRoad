import pygame
from simulation.config import config
from simulation.controller import SimulationController
from simulation.entities.traffic_light import Intersection
from simulation.entities.road import Road, DynamicDivider
from simulation.network import NetworkListener
from simulation.state import SimulationState

def main():
    pygame.init()

    # --- Setup cơ bản ---
    w = config.get('WINDOW_WIDTH')
    h = config.get('WINDOW_HEIGHT')
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("2D Traffic Simulation (Static Map)")
    clock = pygame.time.Clock()
    
    # --- Tạo các thành phần mô phỏng ---
    
    # 1. Tính toán tọa độ tuyệt đối từ tọa độ tương đối trong config
    relative_coords = config.get('INTERSECTION_COORDS_RELATIVE')
    intersection_coords = [{'x': int(rc['x'] * w), 'y': int(rc['y'] * h)} for rc in relative_coords]

    # 2. Tạo các con đường (Roads)
    # 0 1
    # 2 3
    roads = {
        "road_H1": Road(screen, "road_H1", (0, intersection_coords[0]['y']), (w, intersection_coords[0]['y']), num_lanes_per_direction=3),
        "road_H2": Road(screen, "road_H2", (0, intersection_coords[2]['y']), (w, intersection_coords[2]['y']), num_lanes_per_direction=3),
        "road_V1": Road(screen, "road_V1", (intersection_coords[0]['x'], 0), (intersection_coords[0]['x'], h), num_lanes_per_direction=3),
        "road_V2": Road(screen, "road_V2", (intersection_coords[1]['x'], 0), (intersection_coords[1]['x'], h), num_lanes_per_direction=3),
    }

    # 3. Tạo các ngã tư (Intersections)
    intersections = [Intersection(screen, i, (coords['x'], coords['y'])) for i, coords in enumerate(intersection_coords)]
    
    # 4. Tạo các dải phân cách động (hiện tại chỉ để nhận lệnh)
    dynamic_dividers = {road_id: DynamicDivider(road_id) for road_id in roads.keys()}

    sim_state = SimulationState(
        lights=intersections,
        roads=roads,
        vehicles=None,
        rng_seed=config.get("SIMULATION_SEED", 42),
    )

    # 5. Tạo bộ điều khiển (đã được vô hiệu hóa logic xe)
    controller = SimulationController(screen, roads, intersections, state=sim_state)
    
    # --- Thiết lập Global State và Network ---
    global_state = {
        "intersections": intersections,
        "dynamic_dividers": dynamic_dividers
    }
    network_listener = NetworkListener(global_state, use_mqtt=True) 
    network_listener.start()

    # --- Vòng lặp chính ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Logic ---
        # controller.spawn_vehicles() # Vô hiệu hóa
        dt_seconds = clock.get_time() / 1000.0
        controller.update(dt_seconds) # Cập nhật theo pipeline 4 pha

        # --- Chỉ vẽ các thành phần tĩnh ---
        screen.fill(config.get('COLORS')['BLACK'])
        
        for road in roads.values():
            road.draw()
        
        for intersection in intersections:
            intersection.draw()
            
        controller.draw() # Vẽ xe

        pygame.display.flip()
        clock.tick(config.get('FPS'))

    pygame.quit()

if __name__ == '__main__':
    main()
