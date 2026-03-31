import pygame
import random
from simulation.config import config
from simulation.entities.vehicle import Vehicle

class SimulationController:
    def __init__(self, screen):
        self.screen = screen
        self.vehicles = pygame.sprite.Group()
        self.spawn_timers = { 'N': 0, 'S': 0, 'E': 0, 'W': 0 }
        self.spawn_rate = config.get('SPAWN_RATE')
        self.width = config.get('WINDOW_WIDTH')
        self.height = config.get('WINDOW_HEIGHT')

    def spawn_vehicles(self, traffic_lights, dynamic_dividers):
        current_time = pygame.time.get_ticks()
        for direction, rate in self.spawn_rate.items():
            if current_time - self.spawn_timers[direction] > 1000 / rate:
                self.spawn_timers[direction] = current_time
                self._create_vehicle(direction, traffic_lights, dynamic_dividers)

    def _create_vehicle(self, direction, traffic_lights, dynamic_dividers):
        # This is a simplified spawning logic. A real implementation would be more complex.
        v_type = random.choice(['car', 'motorbike'])
        if direction == 'N':
            x, y = self.width / 2, self.height
        elif direction == 'S':
            x, y = self.width / 2, 0
        elif direction == 'E':
            x, y = 0, self.height / 2
        else: # W
            x, y = self.width, self.height / 2
        
        vehicle = Vehicle(x, y, v_type, direction)
        self.vehicles.add(vehicle)


    def enforce_rules(self, traffic_lights, dynamic_dividers):
        for vehicle in self.vehicles:
            # Rule 1: Traffic Light Compliance
            for light in traffic_lights:
                # Simplified logic: check if vehicle is near any intersection
                if vehicle.rect.colliderect(light.rect.inflate(100, 100)):
                    state_key = "N-S" if vehicle.direction in ['N', 'S'] else "E-W"
                    if light.state[state_key] == "RED":
                        # Simple stop line logic
                        if (vehicle.direction == 'S' and vehicle.rect.bottom > light.rect.top - 20) or \
                           (vehicle.direction == 'N' and vehicle.rect.top < light.rect.bottom + 20) or \
                           (vehicle.direction == 'W' and vehicle.rect.left < light.rect.right + 20) or \
                           (vehicle.direction == 'E' and vehicle.rect.right > light.rect.left - 20):
                           vehicle.stop()
                    else:
                        vehicle.resume()

            # Rule 2: Collision Avoidance
            collided = vehicle.check_collision_ahead(self.vehicles)
            if collided:
                vehicle.stop()
            elif not vehicle.stopped: # Do not resume if stopped by light
                vehicle.resume()


    def update(self):
        self.vehicles.update()
        for v in self.vehicles:
            v.move()

    def draw(self):
        self.vehicles.draw(self.screen)
