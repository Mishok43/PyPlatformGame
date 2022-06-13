"""Module containing AABB ECS component and assosiated logic."""


import copy
from dataclasses import dataclass
from typing import Tuple

import glm

from . import velocity


@dataclass
class AABBComponent:
    """AABB component for ECS."""

    pos: glm.vec2
    dim: glm.vec2

    def __init__(self, pos: Tuple[float, float] | glm.vec2, dim: Tuple[float, float] | glm.vec2):
        """Initialize AABB component."""
        self.pos = glm.vec2(pos)
        self.dim = glm.vec2(dim)


def left(box: AABBComponent):
    """Get left value from AABB."""
    return box.pos.x


def right(box: AABBComponent):
    """Get right value from AABB."""
    return (box.pos + box.dim).x


def top(box: AABBComponent):
    """Get top value from AABB."""
    return box.pos.y


def bottom(box: AABBComponent):
    """Get bottom value from AABB."""
    return (box.pos + box.dim).y


def extent(box: AABBComponent):
    """Get extent value from AABB."""
    return box.pos + box.dim


def check(box1: AABBComponent, box2: AABBComponent):
    """Check if two AABBs overlap."""
    return not (right(box1) < left(box2) or left(box1) > right(box2) or
            bottom(box1) < top(box2) or top(box1) > bottom(box2))


def broad_box(box1: AABBComponent, vel: velocity.VelocityComponent):
    """Get broad box of AABB based on entity's velocity."""
    box2 = copy.deepcopy(box1)
    box2.pos += vel.direction

    pos = glm.min(box1.pos, box2.pos)
    dim = glm.max(box1.pos, box2.pos) + box1.dim - pos

    return AABBComponent(pos=pos, dim=dim)


def swept(box1: AABBComponent, box2: AABBComponent, vel: velocity.VelocityComponent):
    """Calculate swept collision between AABBs."""
    entry_inv = glm.vec2(0.0)
    exit_inv = glm.vec2(0.0)

    if vel.direction.x > 0.0:
        entry_inv.x = left(box2) - extent(box1).x
        exit_inv.x = extent(box2).x - left(box1)
    else:
        entry_inv.x = extent(box2).x - left(box1)
        exit_inv.x = left(box2) - extent(box1).x

    if vel.direction.y > 0.0:
        entry_inv.y = top(box2) - extent(box1).y
        exit_inv.y = extent(box2).y - top(box1)
    else:
        entry_inv.y = extent(box2).y - top(box1)
        exit_inv.y = top(box2) - extent(box1).y

    entry_vec = glm.vec2(0.0)
    exit_vec = glm.vec2(0.0)

    if abs(vel.direction.x) <= 0.0001:
        entry_vec.x = -float('inf')
        exit_vec.x = float('inf')
    else:
        entry_vec.x = entry_inv.x / vel.direction.x
        exit_vec.x = exit_inv.x / vel.direction.x

    if abs(vel.direction.y) <= 0.0001:
        entry_vec.y = -float('inf')
        exit_vec.y = float('inf')
    else:
        entry_vec.y = entry_inv.y / vel.direction.y
        exit_vec.y = exit_inv.y / vel.direction.y

    if entry_vec.y > 1.0:
        entry_vec.y = -float('inf')
    if entry_vec.x > 1.0:
        entry_vec.x = -float('inf')

    entry_time = max(entry_vec.x, entry_vec.y)
    exit_time = min(exit_vec.x, exit_vec.y)

    if entry_time > exit_time or glm.all(glm.lessThan(entry_vec, glm.vec2(0.0))):
        return 1.0, glm.vec2(0.0)

    if entry_vec.x < 0.0:
        if extent(box1).x < left(box2) or left(box1) > extent(box2).x:
            return 1.0, glm.vec2(0.0)

    if entry_vec.y < 0.0:
        if extent(box1).y < top(box2) or top(box1) > extent(box2).y:
            return 1.0, glm.vec2(0.0)

    normal = (entry_inv < glm.vec2(0.0)) * 2 - 1
    normal[int(entry_vec.x > entry_vec.y)] = 0.0

    return entry_time, normal
