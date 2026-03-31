import pygame
from simulation.config import config
from simulation.controller import SimulationController
from simulation.entities.traffic_light import TrafficLight
from simulation.entities.road import Road, DynamicDivider
from simulation.network import NetworkListener

def main():
    pygame.init()

    # Setup
    screen = pygame.display.set_mode((config.get('WINDOW_WIDTH'), config.get('WINDOW_HEIGHT')))
    pygame.display.set_caption("2D Traffic Simulation")
    clock = pygame.time.Clock()
    
    # Create simulation elements
    controller = SimulationController(screen)
    
    intersections_coords = config.get('INTERSECTIONS')
    traffic_lights = [TrafficLight(i, coords['x'], coords['y']) for i, coords in enumerate(intersections_coords)]
    
    # Simplified road setup
    roads = [
        Road(screen, "road_H1", (0, 270), (1920, 270)),
        Road(screen, "road_H2", (0, 810), (1920, 810)),
        Road(screen, "road_V1", (480, 0), (480, 1080)),
        Road(screen, "road_V2", (1440, 0), (1440, 1080)),
    ]
    dynamic_dividers = {
        "road_H1": DynamicDivider("road_H1"),
        "road_H2": DynamicDivider("road_H2"),
        "road_V1": DynamicDivider("road_V1"),
        "road_V2": DynamicDivider("road_V2"),
    }

    # Global state for network thread
    global_state = {
        "traffic_lights": traffic_lights,
        "dynamic_dividers": dynamic_dividers
    }

    # Start network listener
    # Set use_mqtt=False to use UDP sockets instead
    network_listener = NetworkListener(global_state, use_mqtt=True) 
    network_listener.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Game Logic ---
        controller.spawn_vehicles(traffic_lights, dynamic_dividers)
        controller.enforce_rules(traffic_lights, dynamic_dividers)
        controller.update()

        # --- Drawing ---
        screen.fill(config.get('COLORS')['BLACK'])
        
        for road in roads:
            road.draw()
            
        for light in traffic_lights:
            light.draw(screen)
            
        controller.draw()

        pygame.display.flip()
        clock.tick(config.get('FPS'))

    pygame.quit()

if __name__ == '__main__':
    main()
