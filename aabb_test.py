"""Physics test is responsible for testing different physical linked classes."""

import unittest
import glm
from .physics import aabb
from .physics import velocity



class AABBTest(unittest.TestCase):
    """Test class for validating AABB."""

    def test_constructing(self):
        """Checking initilization paramters of AABBO."""
        box = aabb.AABBComponent([-1, -2], [4, 3])

        self.assertEqual(aabb.left(box), -1.0)
        self.assertEqual(aabb.right(box), 3.0)
        self.assertEqual(aabb.top(box), -2.0)
        self.assertEqual(aabb.bottom(box), 1.0)
        self.assertEqual(aabb.extent(box), glm.vec2([3.0, 1.0]))

    def test_overlapping(self):
        """Checking overlapping of bounding boxes."""
        box_0 = aabb.AABBComponent([0, 0], [2, 3])
        box_1 = aabb.AABBComponent([2, 5], [2, 2])
        box_2 = aabb.AABBComponent([1, 1], [2, 2])
        self.assertFalse(aabb.check(box_0, box_1))
        self.assertTrue(aabb.check(box_0, box_2))

    def test_broad_box(self):
        """Broad box checking."""
        box = aabb.AABBComponent([-1, -2], [4, 3])
        vel = velocity.VelocityComponent([0.0, 0.0])

        self.assertEqual(box, aabb.broad_box(box, vel))

        vel = velocity.VelocityComponent([1.0, 1.0])
        self.assertEqual(aabb.AABBComponent([-1, -2], [5, 4]), aabb.broad_box(box, vel))

    def test_swept(self):
        """Swept checking."""
        box_0 = aabb.AABBComponent([0, 0], [2, 3])
        box_1 = aabb.AABBComponent([2, 5], [2, 2])
        self.assertFalse(aabb.check(box_0, box_1))
        self.assertTrue(aabb.swept(box_0, box_1, velocity.VelocityComponent([2.0, 2.0])))

if __name__ == '__main__':
    unittest.main()
