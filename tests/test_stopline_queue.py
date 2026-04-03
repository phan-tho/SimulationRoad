import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from simulation.entities.road import Lane
from simulation.entities.traffic_light import Intersection
from simulation.entities.vehicle import Vehicle, QUEUED


class TestStoplineQueue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_queue_forms_on_red_and_releases_on_green(self):
        screen = pygame.Surface((1280, 720))
        intersection = Intersection(screen, 0, (320, 200), size=120)
        lane = Lane(
            start_pos=(20, 200),
            end_pos=(1200, 200),
            direction="E",
            stop_line_positions=[(260, 200)],
        )

        vehicles = []
        for index in range(5):
            vehicle = Vehicle(lane, speed=3)
            vehicle.rect.center = (130 - index * 35, 200)
            vehicles.append(vehicle)

        intersection.update_state(
            {
                "N-S": {"straight": "RED", "left": "RED"},
                "E-W": {"straight": "RED", "left": "RED"},
            }
        )

        for _ in range(120):
            snapshot = list(vehicles)
            for vehicle in vehicles:
                vehicle.update([intersection], snapshot)

        lead = max(vehicles, key=lambda v: v.rect.centerx)
        self.assertLessEqual(lead.front_position[0], 260, "Lead car crossed stop line on red")
        self.assertTrue(any(v.state == QUEUED for v in vehicles), "Queue did not form on red")

        intersection.update_state(
            {
                "N-S": {"straight": "RED", "left": "RED"},
                "E-W": {"straight": "GREEN", "left": "GREEN"},
            }
        )

        saw_accelerate = False
        for _ in range(140):
            snapshot = list(vehicles)
            for vehicle in vehicles:
                vehicle.update([intersection], snapshot)
                if vehicle.state == "ACCELERATE":
                    saw_accelerate = True

        lead_after_green = max(vehicles, key=lambda v: v.rect.centerx)
        self.assertGreater(lead_after_green.front_position[0], 260, "Queue did not release on green")
        self.assertTrue(saw_accelerate, "No vehicle entered ACCELERATE state after green")


if __name__ == "__main__":
    unittest.main()
