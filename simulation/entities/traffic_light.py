import pygame
from simulation.config import config

class TrafficLight(pygame.sprite.Sprite):
    def __init__(self, intersection_id, x, y):
        super().__init__()
        self.intersection_id = intersection_id
        self.state = {"N-S": "RED", "E-W": "RED"}
        self.colors = {
            "RED": config.get('COLORS')['RED'],
            "YELLOW": config.get('COLORS')['YELLOW'],
            "GREEN": config.get('COLORS')['GREEN']
        }
        self.radius = 15
        self.image = pygame.Surface([self.radius * 2, self.radius * 4 + 20])
        self.image.set_colorkey(config.get('COLORS')['BLACK'])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.draw()

    def draw(self, screen=None):
        self.image.fill(config.get('COLORS')['BLACK'])
        # N-S light
        pygame.draw.circle(self.image, self.colors[self.state["N-S"]], (self.radius, self.radius), self.radius)
        # E-W light
        pygame.draw.circle(self.image, self.colors[self.state["E-W"]], (self.radius, self.radius * 3 + 10), self.radius)
        if screen:
            screen.blit(self.image, self.rect)


    def update_state(self, new_state):
        self.state = new_state
        self.draw()
