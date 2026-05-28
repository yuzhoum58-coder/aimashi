"""
变换工具 — 矩阵运算辅助
"""
import numpy as np
from scipy.spatial.transform import Rotation as R
from pathlib import Path


def compose_matrix(translation: tuple, rotation_deg: tuple) -> np.ndarray:
    """
    合成4x4仿射变换矩阵
    
    参数:
        translation: (tx, ty, tz) in mm
        rotation_deg: (rx, ry, rz) in degrees (XYZ Euler)
    
    返回:
        4x4 numpy array
    """
    mat = np.eye(4)
    mat[:3, 3] = translation
    rot = R.from_euler('xyz', np.radians(rotation_deg))
    mat[:3, :3] = rot.as_matrix()
    return mat


def decompose_matrix(mat: np.ndarray) -> tuple:
    """
    分解4x4仿射矩阵为平移和旋转
    
    返回:
        (translation, rotation_deg)
    """
    assert mat.shape == (4, 4), "必须是4x4矩阵"
    
    translation = mat[:3, 3].copy()
    rot = R.from_matrix(mat[:3, :3])
    rotation_deg = rot.as_euler('xyz', degrees=True)
    
    return translation, rotation_deg


def apply_transform_to_points(points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """
    对点集应用变换矩阵
    
    参数:
        points: (N, 3) 或 (3,) numpy array
        matrix: (4, 4) 仿射矩阵
    
    返回:
        变换后的点集
    """
    if points.ndim == 1:
        points = points.reshape(-1, 3)
    
    # 齐次坐标
    ones = np.ones((points.shape[0], 1))
    homogeneous = np.hstack([points, ones])
    
    transformed = homogeneous @ matrix.T
    return transformed[:, :3]


def save_transform_matrix(matrix: np.ndarray, filepath: str):
    """保存变换矩阵到.npy文件"""
    path = Path(filepath)
    np.save(path.with_suffix('.npy'), matrix)
    # 同时保存为TXT格式（可读）
    with open(path.with_suffix('.tfm'), 'w') as f:
        f.write("# Hermes Medical Image Viewer - Registration Transform\n")
        f.write("# Format: 4x4 Affine Matrix (row-major)\n")
        f.write(f"# Translation (mm): {matrix[:3, 3]}\n")
        f.write(f"# Rotation Matrix:\n")
        np.savetxt(f, matrix, fmt='%8.4f')


def load_transform_matrix(filepath: str) -> np.ndarray:
    """加载变换矩阵"""
    path = Path(filepath)
    if path.suffix == '.npy':
        return np.load(path)
    elif path.suffix == '.tfm':
        # 跳过注释行
        data = np.loadtxt(path, comments='#')
        return data
    return np.eye(4)
