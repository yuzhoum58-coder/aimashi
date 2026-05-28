"""
手动配准面板 — 6DOF滑动条控制
"""
import numpy as np
from scipy.spatial.transform import Rotation

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QSlider, QLabel, QPushButton, QFormLayout,
    QDoubleSpinBox, QTextEdit, QGridLayout
)
from PySide6.QtCore import Qt, Signal


class TransformSlider(QWidget):
    """单轴变换滑动条：平移(mm)或旋转(°)"""
    value_changed = Signal(float)

    def __init__(self, label: str, min_val: float, max_val: float, step: float, unit: str):
        super().__init__()
        self.unit = unit
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.name_label = QLabel(label)
        self.name_label.setFixedWidth(25)
        layout.addWidget(self.name_label)

        # 滑动条
        self.slider = QSlider(Qt.Horizontal)
        num_steps = int((max_val - min_val) / step)
        self.slider.setRange(0, num_steps)
        self.slider.setValue(num_steps // 2)
        layout.addWidget(self.slider, 1)

        # 数值显示
        self.value_label = QLabel(f"0.0 {unit}")
        self.value_label.setFixedWidth(80)
        layout.addWidget(self.value_label)

        # 精细调节
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setRange(min_val, max_val)
        self.spinbox.setSingleStep(step)
        self.spinbox.setValue(0.0)
        self.spinbox.setDecimals(1)
        self.spinbox.setFixedWidth(70)
        layout.addWidget(self.spinbox)

        # 连接信号
        self.slider.valueChanged.connect(self._on_slider)
        self.spinbox.valueChanged.connect(self._on_spinbox)

    def _on_slider(self, value):
        v = self._slider_to_value(value)
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(v)
        self.spinbox.blockSignals(False)
        self.value_label.setText(f"{v:.1f} {self.unit}")
        self.value_changed.emit(v)

    def _on_spinbox(self, value):
        v = self.spinbox.value()
        self.slider.blockSignals(True)
        self.slider.setValue(self._value_to_slider(v))
        self.slider.blockSignals(False)
        self.value_label.setText(f"{v:.1f} {self.unit}")
        self.value_changed.emit(v)

    def _slider_to_value(self, slider_val):
        r = self.slider.maximum() - self.slider.minimum()
        if r == 0:
            return 0.0
        return self.spinbox.minimum() + (slider_val / r) * (self.spinbox.maximum() - self.spinbox.minimum())

    def _value_to_slider(self, value):
        r = self.spinbox.maximum() - self.spinbox.minimum()
        if r == 0:
            return self.slider.minimum()
        return int((value - self.spinbox.minimum()) / r * (self.slider.maximum() - self.slider.minimum()))

    def get_value(self) -> float:
        return self.spinbox.value()

    def set_value(self, val: float):
        self.spinbox.setValue(val)


class ManualRegistrationPanel(QWidget):
    """手动配准控制面板 — 6DOF变换"""

    transform_changed = Signal(np.ndarray)  # 发射4x4变换矩阵

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # --- 平移控制 ---
        trans_group = QGroupBox("平移 (mm)")
        trans_layout = QFormLayout(trans_group)

        self.tx = TransformSlider("Tx", -50, 50, 0.5, "mm")
        self.ty = TransformSlider("Ty", -50, 50, 0.5, "mm")
        self.tz = TransformSlider("Tz", -50, 50, 0.5, "mm")

        trans_layout.addRow(self.tx)
        trans_layout.addRow(self.ty)
        trans_layout.addRow(self.tz)
        layout.addWidget(trans_group)

        # --- 旋转控制 ---
        rot_group = QGroupBox("旋转 (度)")
        rot_layout = QFormLayout(rot_group)

        self.rx = TransformSlider("Rx", -30, 30, 0.5, "°")
        self.ry = TransformSlider("Ry", -30, 30, 0.5, "°")
        self.rz = TransformSlider("Rz", -30, 30, 0.5, "°")

        rot_layout.addRow(self.rx)
        rot_layout.addRow(self.ry)
        rot_layout.addRow(self.rz)
        layout.addWidget(rot_group)

        # 连接信号
        for slider in [self.tx, self.ty, self.tz, self.rx, self.ry, self.rz]:
            slider.value_changed.connect(self._emit_transform)

        # --- 变换矩阵显示 ---
        matrix_group = QGroupBox("当前变换矩阵")
        matrix_layout = QVBoxLayout(matrix_group)
        self.matrix_display = QTextEdit()
        self.matrix_display.setReadOnly(True)
        self.matrix_display.setMaximumHeight(120)
        self.matrix_display.setFont(
            __import__('PySide6.QtGui').QtGui.QFont("Courier", 9)
        )
        matrix_layout.addWidget(self.matrix_display)
        layout.addWidget(matrix_group)

        # --- 控制按钮 ---
        btn_layout = QHBoxLayout()
        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self._reset)
        btn_layout.addWidget(reset_btn)

        snap_btn = QPushButton("对齐到原点")
        snap_btn.clicked.connect(self._snap_to_origin)
        btn_layout.addWidget(snap_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        # 初始显示
        self._emit_transform()

    def _compute_matrix(self) -> np.ndarray:
        """根据当前滑动条值计算4x4变换矩阵"""
        tx = self.tx.get_value()
        ty = self.ty.get_value()
        tz = self.tz.get_value()

        rx = np.radians(self.rx.get_value())
        ry = np.radians(self.ry.get_value())
        rz = np.radians(self.rz.get_value())

        # 旋转矩阵 (XYZ欧拉角)
        r = Rotation.from_euler('xyz', [rx, ry, rz])
        rot_mat = r.as_matrix()

        # 组装4x4仿射矩阵
        mat = np.eye(4)
        mat[:3, :3] = rot_mat
        mat[:3, 3] = [tx, ty, tz]

        return mat

    def _emit_transform(self):
        """滑块变化 → 发射矩阵"""
        mat = self._compute_matrix()

        # 更新显示
        mat_str = np.array2string(mat, precision=2, suppress_small=True)
        self.matrix_display.setText(mat_str)

        self.transform_changed.emit(mat)

    def _reset(self):
        """重置所有变换为0"""
        for s in [self.tx, self.ty, self.tz, self.rx, self.ry, self.rz]:
            s.set_value(0.0)

    def _snap_to_origin(self):
        """对齐到原点（同_reset）"""
        self._reset()

    def get_current_matrix(self) -> np.ndarray:
        """获取当前变换矩阵（用于导出）"""
        return self._compute_matrix()

    def set_transform(self, matrix: np.ndarray):
        """从外部设置变换矩阵"""
        if matrix.shape != (4, 4):
            return
        # 提取平移分量
        tx, ty, tz = matrix[:3, 3]
        # 提取旋转（欧拉角）
        r = Rotation.from_matrix(matrix[:3, :3])
        rx, ry, rz = np.degrees(r.as_euler('xyz'))

        self.tx.blockSignals(True)
        self.ty.blockSignals(True)
        self.tz.blockSignals(True)
        self.rx.blockSignals(True)
        self.ry.blockSignals(True)
        self.rz.blockSignals(True)

        self.tx.set_value(tx)
        self.ty.set_value(ty)
        self.tz.set_value(tz)
        self.rx.set_value(rx)
        self.ry.set_value(ry)
        self.rz.set_value(rz)

        for s in [self.tx, self.ty, self.tz, self.rx, self.ry, self.rz]:
            s.blockSignals(False)

        self._emit_transform()
