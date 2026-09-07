"""문제 5 — 동차변환 inv_T 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 것은 `inv_T` 검증이지만,
점/방향 구분과 벡터화, 최소자승까지 함께 검증해 두면 이후 문제에서 안전하다.

실행: 프로젝트 루트에서  pytest -v
"""

import numpy as np
import pytest

from src.rotation import rot_x, rot_y, rot_z
from src.transform import (
    inv_T,
    least_squares_normal_equation,
    make_T,
    transform_direction,
    transform_point,
    transform_points,
)


@pytest.fixture
def T():
    """테스트에 쓸 대표 동차변환 하나."""
    R = rot_z(0.9) @ rot_y(-0.35) @ rot_x(1.3)
    return make_T(R, [0.35, -0.15, 0.55])


def test_inv_T_gives_identity(T):
    Ti = inv_T(T)
    assert np.allclose(Ti @ T, np.eye(4))
    assert np.allclose(T @ Ti, np.eye(4))


def test_inv_T_matches_generic_inverse(T):
    assert np.allclose(inv_T(T), np.linalg.inv(T))  # 검산용


def test_point_and_direction_differ(T):
    vector = np.array([1.0, 2.0, -0.5])
    point = transform_point(T, vector)
    direction = transform_direction(T, vector)
    assert not np.allclose(point, direction)
    assert np.allclose(point - direction, T[:3, 3])
    assert np.isclose(np.linalg.norm(direction), np.linalg.norm(vector))


def test_transform_points_is_vectorized(T):
    points = np.arange(15, dtype=float).reshape(5, 3)
    expected = np.array([transform_point(T, point) for point in points])
    assert np.allclose(transform_points(T, points), expected)


def test_roundtrip_through_inverse(T):
    points = np.random.default_rng(42).standard_normal((20, 3))
    assert np.allclose(transform_points(inv_T(T), transform_points(T, points)), points)


def test_least_squares_matches_lstsq():
    rng = np.random.default_rng(42)
    A = rng.standard_normal((30, 4))
    expected_x = rng.standard_normal(4)
    b = A @ expected_x + 1e-3 * rng.standard_normal(30)
    x, residual = least_squares_normal_equation(A, b)
    reference = np.linalg.lstsq(A, b, rcond=None)[0]  # 비교 대상
    assert np.allclose(x, reference)
    assert np.allclose(A.T @ residual, 0.0, atol=1e-9)
