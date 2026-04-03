import unittest

from simulation.state import SimulationState


class TestSimulationState(unittest.TestCase):
    def test_tick_advances_sim_time(self):
        state = SimulationState(lights=[], roads={}, vehicles=[], rng_seed=7)
        state.tick(0.25)
        state.tick(0.75)
        self.assertAlmostEqual(state.sim_time, 1.0)

    def test_seeded_rng_is_deterministic(self):
        state_a = SimulationState(lights=[], roads={}, vehicles=[], rng_seed=123)
        state_b = SimulationState(lights=[], roads={}, vehicles=[], rng_seed=123)

        sequence_a = [state_a.rng.randint(1, 1000) for _ in range(5)]
        sequence_b = [state_b.rng.randint(1, 1000) for _ in range(5)]

        self.assertEqual(sequence_a, sequence_b)


if __name__ == "__main__":
    unittest.main()
