import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from simulation.entities.road import Lane
from simulation.entities.vehicle import Vehicle
from simulation.entities.traffic_light import Intersection


class TestCarFollowing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_same_lane_no_collision_for_2000_steps(self):
        lane = Lane(
            start_pos=(20, 100),
            end_pos=(1200, 100),
            direction="E",
            stop_line_positions=[],
        )

        vehicles = []
        for index in range(8):
            vehicle = Vehicle(lane, speed=3)
            vehicle.rect.center = (20 - index * 60, 100)
            vehicles.append(vehicle)

        for _ in range(2000):
            snapshot = list(vehicles)
            for vehicle in vehicles:
                vehicle.update([], snapshot)

            for i in range(len(vehicles)):
                for j in range(i + 1, len(vehicles)):
                    self.assertFalse(
                        vehicles[i].rect.colliderect(vehicles[j].rect),
                        "Vehicles collided in same lane",
                    )

    def test_vehicle_stops_for_red_before_crossing_stop_line(self):
        screen = pygame.Surface((1280, 720))
        intersection = Intersection(screen, 0, (320, 200), size=120)
        intersection.update_state(
            {
                "N-S": {"straight": "RED", "left": "RED"},
                "E-W": {"straight": "RED", "left": "RED"},
            }
        )

        lane = Lane(
            start_pos=(20, 200),
            end_pos=(1200, 200),
            direction="E",
            stop_line_positions=[(260, 200)],
        )

        vehicle = Vehicle(lane, speed=3)
        vehicle.rect.midright = (258, 200)  # very close to stop line
        vehicle.update([intersection], [vehicle])

        self.assertEqual(vehicle.speed, 0, "Vehicle should stop for red before crossing")


if __name__ == "__main__":
    unittest.main()
