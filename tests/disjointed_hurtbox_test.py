"""Module which contains disjointed hurtbox test."""

import unittest
import esper
import glm

from PyPlatformGame import player
from PyPlatformGame.physics import aabb

class DisjointedHurtboxTest(unittest.TestCase):
    """Test class for validating disjointed hurtbox."""

    def setUp(self):
        """Setuping world with player entity."""
        self.world = esper.World()
        self.world.add_processor(player.DisjointedController())
        self.player_entity = self.world.create_entity(
                aabb.AABBComponent([0.0, 0.0], [1.0, 1.0]),
                player.StateComponent())

    def test_destruction(self):
        """Testing destruction."""
        hurtbox_entity = self.world.create_entity(
                aabb.AABBComponent([0.0, 0.0], [1.0, 1.0]),
                player.DisjointedParamsComponent(1.0, self.player_entity))

        self.world.process(1.01)
        self.assertFalse(self.world.entity_exists(hurtbox_entity))

    def test_player_death(self):
        """Testing player death."""
        hurtbox_entity = self.world.create_entity(
                aabb.AABBComponent([0.0, 0.0], [1.0, 1.0]),
                player.DisjointedParamsComponent(1.0, self.player_entity))

        self.world.delete_entity(self.player_entity)

        self.world.process(0.0)
        self.assertFalse(self.world.entity_exists(hurtbox_entity))

    def test_box(self):
        """Testing box."""
        hurtbox_entity = self.world.create_entity(
                aabb.AABBComponent([0.0, 0.0], [1.0, 1.0]),
                player.DisjointedParamsComponent(1.0, self.player_entity))

        self.world.process(0.0)
        aabb_comp = self.world.component_for_entity(hurtbox_entity, aabb.AABBComponent)
        self.assertEqual(aabb_comp.pos, glm.vec2([1, 0]))
        self.assertEqual(aabb_comp.dim, glm.vec2([1, 1]))

if __name__ == '__main__':
    unittest.main()
