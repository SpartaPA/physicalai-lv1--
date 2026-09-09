"""Tests for geometry helpers, including boundaries and invalid inputs."""

import math
import pytest
from turtle_py.math_utils import distance, heading_to, normalize_angle, waypoint_reached


def test_distance_normal_and_invalid():
    assert distance(0.0, 0.0, 3.0, 4.0) == pytest.approx(5.0)
    assert distance(1.0, 1.0, 1.0, 1.0) == 0.0
    with pytest.raises(ValueError):
        distance(math.nan, 0.0)


def test_heading_and_normalization():
    assert heading_to(0.0, 0.0, 0.0, 1.0) == pytest.approx(math.pi / 2.0)
    assert normalize_angle(3.0 * math.pi) == pytest.approx(-math.pi)
    with pytest.raises(ValueError):
        heading_to(1.0, 1.0, 1.0, 1.0)


def test_waypoint_tolerance_is_inclusive():
    assert waypoint_reached(0.0, 0.0, 0.3, 0.4, 0.5)
    assert not waypoint_reached(0.0, 0.0, 0.3, 0.4, 0.499)
    with pytest.raises(ValueError):
        waypoint_reached(0.0, 0.0, 1.0, 1.0, -0.1)
