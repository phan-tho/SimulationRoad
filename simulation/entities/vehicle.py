import pygame
from simulation.config import config

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, x, y, vehicle_type, direction, safe_distance=10):
        super().__init__()
        self.vehicle_type = vehicle_type
        if self.vehicle_type == 'car':
            self.width = 40
            self.height = 20
            self.color = config.get('COLORS')['BLUE']
        else: # motorbike
            self.width = 20
            self.height = 10
            self.color = config.get('COLORS')['RED']

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.velocity = 5
        self.direction = direction
        self.safe_distance = safe_distance
        self.stopped = False

    def move(self):
        if not self.stopped:
            if self.direction == 'N':
                self.rect.y -= self.velocity
            elif self.direction == 'S':
                self.rect.y += self.velocity
            elif self.direction == 'E':
                self.rect.x += self.velocity
            elif self.direction == 'W':
                self.rect.x -= self.velocity

    def stop(self):
        self.stopped = True

    def resume(self):
        self.stopped = False

    def check_collision_ahead(self, others):
        for other in others:
            if other is not self:
                # Simple ahead check based on direction
                if self.direction == 'N' and other.direction == 'N' and self.rect.y > other.rect.y:
                    if self.rect.y - other.rect.y < self.safe_distance:
                        return True
                elif self.direction == 'S' and other.direction == 'S' and self.rect.y < other.rect.y:
                    if other.rect.y - self.rect.y < self.safe_distance:
                        return True
                elif self.direction == 'E' and other.direction == 'E' and self.rect.x < other.rect.x:
                    if other.rect.x - self.rect.x < self.safe_distance:
                        return True
                elif self.direction == 'W' and other.direction == 'W' and self.rect.x > other.rect.x:
                    if self.rect.x - other.rect.x < self.safe_distance:
                        return True
        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
