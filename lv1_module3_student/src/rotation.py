"""문제 2·3 — 회전 행렬 모듈. (학생 작성용 템플릿)

축별 회전 행렬, 로드리게스 공식(임의 축 회전), Gram-Schmidt 재직교화,
회전행렬 판정과 고유값 분해 기반 축·각 복원을 직접 구현한다.

문제 1 에서 만든 `src/vectors.py` 를 그대로 재사용한다.
"""

from __future__ import annotations

import numpy as np

from .vectors import det, normalize, skew

__all__ = [
    "rot_x",
    "rot_y",
    "rot_z",
    "rodrigues",
    "gram_schmidt",
    "orthogonality_error",
    "is_rotation",
    "axis_angle_from_matrix",
    "quaternion_from_axis_angle",
]


# ------------------------------------------------------------ 축별 회전 행렬

def rot_x(theta: float) -> np.ndarray:
    """x축 기준 회전 행렬 (theta 는 **라디안**). x 성분은 보존된다."""
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [1.0, 0.0, 0.0],
        [0.0, c, -s],
        [0.0, s, c],
    ])


def rot_y(theta: float) -> np.ndarray:
    """y축 기준 회전 행렬 (theta 는 라디안). y 성분은 보존된다.

    부호 배치가 x·z 와 반대로 보이는 이유는 노트북 2-1 에서 설명한다.
    """
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [c, 0.0, s],
        [0.0, 1.0, 0.0],
        [-s, 0.0, c],
    ])


def rot_z(theta: float) -> np.ndarray:
    """z축 기준 회전 행렬 (theta 는 라디안). z 성분은 보존된다."""
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [c, -s, 0.0],
        [s, c, 0.0],
        [0.0, 0.0, 1.0],
    ])


def rodrigues(axis, theta: float) -> np.ndarray:
    """로드리게스 공식으로 임의 축 회전 행렬을 만든다.

        R = I + sin(theta) * K + (1 - cos(theta)) * K @ K,   K = [k]_x

    - 축은 함수 안에서 단위벡터로 정규화한다
      (정규화되지 않은 축을 넣어도 같은 결과가 나와야 한다).
    - 문제 1 의 `skew` 를 반드시 사용한다.
    """
    axis = normalize(axis)
    K = skew(axis)
    c = np.cos(theta)
    s = np.sin(theta)
    return c * np.eye(3) + (1.0 - c) * np.outer(axis, axis) + s * K


# ------------------------------------------------------------- 재직교화 관련

def gram_schmidt(A) -> np.ndarray:
    """**열벡터**에 대해 Gram-Schmidt 직교정규화를 수행한다.

        q1 = a1 / |a1|
        vj = aj - sum_{i<j} (qi · aj) qi
        qj = vj / |vj|

    각 열에서 앞선 열 방향 성분(정사영)을 빼고 정규화하는 것이며,
    문제 1 의 project / reject 와 같은 연산의 반복이다.

    수치적으로는 성분을 빼자마자 갱신하는 modified Gram-Schmidt 가 더 안정적이다.
    앞선 열들에 종속인 열이 있으면 ValueError.
    """
    A = np.asarray(A, dtype=float)
    if A.ndim != 2:
        raise ValueError("A must be a two-dimensional matrix")

    if A.shape[0] < A.shape[1]:
        raise ValueError("A cannot have more columns than rows")

    Q = np.empty_like(A)
    for j in range(A.shape[1]):
        v = A[:, j].copy()
        for i in range(j):
            v -= np.dot(Q[:, i], v) * Q[:, i]

        v_norm = float(np.sqrt(np.sum(v * v)))
        col_norm = float(np.sqrt(np.sum(A[:, j] * A[:, j])))
        if v_norm <= np.finfo(float).eps * max(1.0, col_norm):
            raise ValueError("A contains linearly dependent columns")
        Q[:, j] = v / v_norm

    return Q


def orthogonality_error(R) -> float:
    """직교성 이탈 지표: || R^T R - I ||_F  (프로베니우스 노름).

    완전한 직교행렬이면 0 이고, 클수록 직교성이 무너진 것이다.
    """
    R = np.asarray(R, dtype=float)
    if R.ndim != 2:
        raise ValueError("R must be a two-dimensional matrix")
    error = R.T @ R - np.eye(R.shape[1])
    return float(np.sqrt(np.sum(error * error)))


def is_rotation(R, atol: float = 1e-8) -> bool:
    """회전행렬 판정: 직교(R^T R = I) **그리고** det(R) = +1 이면 True.

    det = -1 이면 직교이긴 하지만 반사가 섞여 있어 회전이 아니다.
    3x3 이 아니면 False.
    """
    R = np.asarray(R, dtype=float)
    if R.shape != (3, 3):
        return False

    return bool(
        np.allclose(R.T @ R, np.eye(3), atol=atol, rtol=0.0)
        and np.isclose(det(R), 1.0, atol=atol, rtol=0.0)
    )


# --------------------------------------------------- 회전축·회전각·쿼터니언

def axis_angle_from_matrix(R, atol: float = 1e-8):
    """고유값 분해로 회전축을, 대각합으로 회전각을 복원한다.

    - 회전축은 고유값 1 에 대응하는 실수 고유벡터다 (R k = k).
      -> 여기서는 `np.linalg.eig` 를 써도 된다 (검산이 아니라 축 복원이 목적).
    - 회전각은 trace(R) = 1 + 2 cos(theta) 에서 구한다.
    - arccos 의 치역이 [0, pi] 라 '어느 쪽으로 도는지'는 알 수 없고,
      고유벡터도 부호가 정해지지 않는다. 반대칭 성분
      R - R^T = 2 sin(theta) [k]_x 를 이용해 부호를 맞춘다.
    - theta = 0 (회전 없음) 과 theta = pi (sin = 0) 는 따로 처리해야 한다.
      두 경우에 어떤 규약을 쓸지 정하고 주석으로 남긴다.

    Returns
    -------
    axis : 단위 회전축 (3,)
    angle : 회전각 [rad], 0 <= angle <= pi
    """
    R = np.asarray(R, dtype=float)
    if not is_rotation(R, atol=atol):
        raise ValueError("R must be a 3x3 rotation matrix")

    cos_angle = float(np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0))
    angle = float(np.arccos(cos_angle))

    # Identity has no unique axis; use +x as a deterministic convention.
    if angle <= atol:
        return np.array([1.0, 0.0, 0.0]), 0.0

    eigenvalues, eigenvectors = np.linalg.eig(R)
    index = int(np.argmin(np.abs(eigenvalues - 1.0)))
    axis = np.real_if_close(eigenvectors[:, index], tol=1000)
    if np.iscomplexobj(axis):
        raise ValueError("could not recover a real rotation axis")
    axis = normalize(np.asarray(axis, dtype=float))

    # Away from pi, the skew part fixes the otherwise arbitrary eigenvector sign.
    skew_vector = np.array([
        R[2, 1] - R[1, 2],
        R[0, 2] - R[2, 0],
        R[1, 0] - R[0, 1],
    ])
    if float(np.sqrt(np.sum(skew_vector * skew_vector))) > atol:
        if float(np.dot(axis, skew_vector)) < 0.0:
            axis = -axis
    else:
        # At pi both signs are equivalent. Pick one deterministically.
        first_nonzero = np.flatnonzero(np.abs(axis) > atol)
        if first_nonzero.size and axis[first_nonzero[0]] < 0.0:
            axis = -axis

    return axis, angle


def quaternion_from_axis_angle(axis, angle: float) -> np.ndarray:
    """축-각에서 단위 쿼터니언을 만든다.

        q = (k * sin(theta/2), cos(theta/2))

    반환 순서는 SciPy `Rotation.as_quat()` 와 같은 **(x, y, z, w)** 로 맞춘다
    (그래야 문제 6-5 에서 바로 비교할 수 있다).
    """
    axis = normalize(axis)
    half_angle = float(angle) / 2.0
    xyz = axis * np.sin(half_angle)
    quaternion = np.concatenate((xyz, [np.cos(half_angle)]))
    # Suppress tiny drift and guarantee unit length for very large angles.
    return quaternion / np.sqrt(np.sum(quaternion * quaternion))
