import pygame
from simulation.config import config

class Road:
    def __init__(self, screen, road_id, start, end, lanes=4):
        self.screen = screen
        self.road_id = road_id
        self.start = start
        self.end = end
        self.lanes = lanes
        self.lane_width = 20
        self.divider_position = (start[0] + end[0]) / 2 if start[1] == end[1] else (start[1] + end[1]) / 2
        self.is_horizontal = start[1] == end[1]

    def draw(self):
        # Draw road surface
        if self.is_horizontal:
            pygame.draw.line(self.screen, config.get('COLORS')['WHITE'], self.start, self.end, self.lanes * self.lane_width * 2)
        else:
            pygame.draw.line(self.screen, config.get('COLORS')['WHITE'], self.start, self.end, self.lanes * self.lane_width * 2)

        # Draw divider
        if self.is_horizontal:
            pygame.draw.line(self.screen, config.get('COLORS')['YELLOW'], (self.start[0], self.divider_position), (self.end[0], self.divider_position), 2)
        else:
            pygame.draw.line(self.screen, config.get('COLORS')['YELLOW'], (self.divider_position, self.start[1]), (self.divider_position, self.end[1]), 2)


class DynamicDivider:
    def __init__(self, road_id, initial_ratio="2:2"):
        self.road_id = road_id
        self.ratio = initial_ratio

    def shift_divider(self, new_ratio):
        self.ratio = new_ratio
        # Logic to update lane access for vehicles will be in the controller
