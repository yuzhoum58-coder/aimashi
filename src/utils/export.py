"""
导出工具
"""
import numpy as np
from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QMessageBox
from src.registration.transform_utils import save_transform_matrix


def export_transform_matrix(parent_widget, matrix: np.ndarray):
    """导出变换矩阵对话框"""
    filepath, _ = QFileDialog.getSaveFileName(
        parent_widget,
        "导出变换矩阵",
        str(Path.home() / "registration_transform.npy"),
        "NumPy矩阵 (*.npy);;文本矩阵 (*.tfm);;所有文件 (*)"
    )
    if filepath:
        save_transform_matrix(matrix, filepath)
        QMessageBox.information(
            parent_widget,
            "导出成功",
            f"变换矩阵已保存到:\n{filepath}\n\n"
            f"平移: {matrix[:3, 3].round(2)}\n"
            f"格式: .npy (可加载) + .tfm (可读)"
        )
