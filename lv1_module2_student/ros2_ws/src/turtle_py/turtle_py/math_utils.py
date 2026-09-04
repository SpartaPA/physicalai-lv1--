"""Pure geometry helpers shared by turtle nodes and unit tests."""

import math


def distance(x1, y1, x2=0.0, y2=0.0):
    """Return Euclidean distance and reject non-finite inputs."""
    values = (x1, y1, x2, y2)
    if not all(math.isfinite(value) for value in values):
        raise ValueError('coordinates must be finite')
    return math.hypot(x2 - x1, y2 - y1)


def normalize_angle(angle):
    """Normalize an angle to the half-open interval [-pi, pi)."""
    if not math.isfinite(angle):
        raise ValueError('angle must be finite')
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def heading_to(x, y, goal_x, goal_y):
    """Return the normalized heading from a point to a goal."""
    if x == goal_x and y == goal_y:
        raise ValueError('heading is undefined at the goal')
    return normalize_angle(math.atan2(goal_y - y, goal_x - x))


def waypoint_reached(x, y, goal_x, goal_y, tolerance):
    """Return whether a point is within the inclusive tolerance boundary."""
    if tolerance < 0.0 or not math.isfinite(tolerance):
        raise ValueError('tolerance must be finite and non-negative')
    return distance(x, y, goal_x, goal_y) <= tolerance
