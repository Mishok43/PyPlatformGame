"""Module which contains gravity unit testing."""

import math
import unittest
import esper
import glm


from .physics import velocity
from .physics import gravity


class GravityTest(unittest.TestCase):
    """Test class for validating velocity."""

    def setup_world(self):
        """Setuping world before testing."""
        world = esper.World()
        world.add_processor(gravity.GravityProcessor())

        test_entity = world.create_entity(
                velocity.VelocityComponent(direction=(0, 0)),
                gravity.SusceptibleToGravityComponent())
        return test_entity, world


    def test_stationarity(self):
        """Testing stationarity with 0 delta."""
        test_entity, world = self.setup_world()
        world.process(0.0)

        velocity_comp = world.component_for_entity(test_entity, velocity.VelocityComponent)
        self.assertEqual(velocity_comp.direction, glm.vec2([0.0, 0.0]))

    def test_dynamics(self):
        """Testing dynamics."""
        test_entity, world = self.setup_world()
        world.process(0.1)

        velocity_comp = world.component_for_entity(test_entity, velocity.VelocityComponent)
        diff = velocity_comp.direction-glm.vec2([0.0, 0.0326673])
        self.assertTrue(math.sqrt(glm.dot(diff, diff)) < 0.001)

        world.process(0.2)

        velocity_comp = world.component_for_entity(test_entity, velocity.VelocityComponent)
        diff = velocity_comp.direction-glm.vec2([0.0, 0.04905])
        self.assertTrue(math.sqrt(glm.dot(diff, diff)) < 0.001)

if __name__ == '__main__':
    unittest.main()
