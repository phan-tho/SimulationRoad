import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from simulation.entities.road import Lane
from simulation.entities.road import Road
from simulation.entities.traffic_light import Intersection
from simulation.entities.vehicle import Vehicle


class TestRouteTurning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_invalid_turn_lane_falls_back_to_straight(self):
        lane = Lane(
            start_pos=(20, 200),
            end_pos=(1200, 200),
            direction="E",
            stop_line_positions=[],
            lane_index=2,
            lanes_per_direction=3,
        )
        vehicle = Vehicle(lane, speed=3, route_plan="left")
        self.assertEqual(vehicle.route_plan, "straight")

    def test_vehicle_turns_left_inside_intersection(self):
        screen = pygame.Surface((1280, 720))
        intersection = Intersection(screen, 0, (320, 200), size=120)
        roads = {
            "road_H1": Road(screen, "road_H1", (0, 200), (1280, 200), num_lanes_per_direction=3),
            "road_V1": Road(screen, "road_V1", (320, 0), (320, 720), num_lanes_per_direction=3),
        }
        intersection.update_state(
            {
                "N-S": {"straight": "GREEN", "left": "GREEN"},
                "E-W": {"straight": "GREEN", "left": "GREEN"},
            }
        )

        lane = Lane(
            start_pos=(20, 200),
            end_pos=(1200, 200),
            direction="E",
            stop_line_positions=[(260, 200)],
            lane_index=0,
            lanes_per_direction=3,
        )
        vehicle = Vehicle(lane, speed=3, route_plan="left")
        vehicle.rect.center = (250, 200)

        for _ in range(40):
            vehicle.update([intersection], [vehicle], roads=roads)
            if vehicle.has_turned:
                break

        self.assertTrue(vehicle.has_turned, "Vehicle did not execute planned turn")
        self.assertEqual(vehicle.direction, "N", "Left turn from E must become N")
        self.assertEqual(vehicle.rect.centerx, int(vehicle.lane.start_pos[0]), "Vehicle not snapped to lane center after turn")


if __name__ == "__main__":
    unittest.main()
