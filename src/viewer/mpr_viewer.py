"""
四视图MPR + 3D — VTK多视口
"""
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel
from PySide6.QtCore import Qt

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class MPRViewerWidget(QWidget):
    """四视图：横断(Axial) / 矢状(Sagittal) / 冠状(Coronal) / 3D"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ct_volume = None
        self.mri_volume = None
        self.ct_metadata = None
        self.mri_metadata = None

        self.fusion_transform = np.eye(4)  # 当前配准变换矩阵

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # VTK渲染窗口
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtk_widget, 1)

        render_window = self.vtk_widget.GetRenderWindow()

        # 创建4个视口
        self.renderers = []
        viewport_layout = [
            (0.0, 0.5, 0.5, 1.0, "Axial"),       # 左上：横断
            (0.5, 0.5, 1.0, 1.0, "Sagittal"),      # 右上：矢状
            (0.0, 0.0, 0.5, 0.5, "Coronal"),        # 左下：冠状
            (0.5, 0.0, 1.0, 0.5, "3D"),             # 右下：3D
        ]

        self.image_mappers = {}  # 保存mapper用于更新
        self.volume_props = {}

        for xmin, ymin, xmax, ymax, name in viewport_layout:
            renderer = vtk.vtkRenderer()
            renderer.SetBackground(0.1, 0.1, 0.12)
            renderer.SetViewport(xmin, ymin, xmax, ymax)
            render_window.AddRenderer(renderer)
            self.renderers.append((name, renderer))

        # 初始化交互器
        self.vtk_widget.GetRenderWindow().GetInteractor().Initialize()

        # 切片滚动条
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("切片:"))
        self.slice_slider = QSlider(Qt.Horizontal)
        self.slice_slider.setRange(0, 100)
        self.slice_slider.setValue(50)
        self.slice_slider.valueChanged.connect(self._on_slice_changed)
        slider_layout.addWidget(self.slice_slider)
        layout.addLayout(slider_layout)

    def set_volume(self, volume: np.ndarray, metadata: dict, modality: str):
        """设置CT或MRI体积数据"""
        if modality == "CT":
            self.ct_volume = volume
            self.ct_metadata = metadata
        else:
            self.mri_volume = volume
            self.mri_metadata = metadata

        self._update_views()

    def _update_views(self):
        """更新所有视图"""
        render_window = self.vtk_widget.GetRenderWindow()

        # 清除旧actor
        for name, renderer in self.renderers:
            renderer.RemoveAllViewProps()

        if self.ct_volume is None:
            render_window.Render()
            return

        # 创建CT体积渲染
        ct_data = self._numpy_to_vtk_image(self.ct_volume)

        for name, renderer in self.renderers:
            if name == "3D":
                self._setup_3d_view(renderer, ct_data)
            else:
                self._setup_mpr_view(renderer, ct_data, name)

        # 如果有MRI，叠加显示
        if self.mri_volume is not None:
            mri_data = self._numpy_to_vtk_image(self.mri_volume)
            for name, renderer in self.renderers:
                if name != "3D":
                    self._overlay_mri(renderer, mri_data, name)
                    break  # 只在横断位叠加

        render_window.Render()

    def _numpy_to_vtk_image(self, volume: np.ndarray) -> vtk.vtkImageData:
        """numpy数组 → VTK ImageData"""
        # 确保方向正确 (Z, Y, X) → VTK (X, Y, Z)
        vol_swapped = np.transpose(volume, (2, 1, 0))  # (X, Y, Z)

        vtk_image = vtk.vtkImageData()
        vtk_image.SetDimensions(vol_swapped.shape)
        vtk_image.SetSpacing(1.0, 1.0, 1.0)
        vtk_image.AllocateScalars(vtk.VTK_FLOAT, 1)

        # 复制数据
        flat = vol_swapped.flatten().astype(np.float32)
        vtk_array = vtk.vtkFloatArray()
        vtk_array.SetNumberOfValues(len(flat))
        for i in range(len(flat)):
            vtk_array.SetValue(i, flat[i])
        vtk_image.GetPointData().SetScalars(vtk_array)

        return vtk_image

    def _setup_mpr_view(self, renderer, image_data, plane_name):
        """MPR视图 — 使用vtkImageResliceMapper"""
        mapper = vtk.vtkImageResliceMapper()
        mapper.SetInputData(image_data)

        # 根据视口设置切片方向
        if plane_name == "Axial":
            mapper.SliceAtFocalPointOn()
            mapper.SliceFacesCameraOn()
        elif plane_name == "Sagittal":
            mapper.SliceAtFocalPointOn()
            mapper.SliceFacesCameraOn()
        elif plane_name == "Coronal":
            mapper.SliceAtFocalPointOn()
            mapper.SliceFacesCameraOn()

        actor = vtk.vtkImageSlice()
        actor.SetMapper(mapper)

        # 窗宽窗位
        prop = actor.GetProperty()
        prop.SetColorWindow(2000)   # 骨窗
        prop.SetColorLevel(500)

        renderer.AddActor(actor)
        renderer.ResetCamera()

    def _setup_3d_view(self, renderer, image_data):
        """3D体绘制视图"""
        # 体绘制管线
        volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
        volume_mapper.SetInputData(image_data)

        # 传输函数
        color_func = vtk.vtkColorTransferFunction()
        color_func.AddRGBPoint(-1000, 0.0, 0.0, 0.0)
        color_func.AddRGBPoint(200, 0.8, 0.6, 0.4)
        color_func.AddRGBPoint(1500, 1.0, 1.0, 1.0)

        opacity_func = vtk.vtkPiecewiseFunction()
        opacity_func.AddPoint(-1000, 0.0)
        opacity_func.AddPoint(200, 0.1)
        opacity_func.AddPoint(600, 0.3)
        opacity_func.AddPoint(1500, 0.8)

        volume_prop = vtk.vtkVolumeProperty()
        volume_prop.SetColor(color_func)
        volume_prop.SetScalarOpacity(opacity_func)
        volume_prop.ShadeOn()

        volume = vtk.vtkVolume()
        volume.SetMapper(volume_mapper)
        volume.SetProperty(volume_prop)

        renderer.AddVolume(volume)
        renderer.ResetCamera()

    def _overlay_mri(self, renderer, mri_data, plane_name):
        """叠加MRI（半透明）"""
        mapper = vtk.vtkImageResliceMapper()
        mapper.SetInputData(mri_data)
        mapper.SliceAtFocalPointOn()
        mapper.SliceFacesCameraOn()

        # 应用配准变换
        transform = vtk.vtkTransform()
        transform.SetMatrix(self.fusion_transform.ravel())
        mapper.SetTransform(transform)

        actor = vtk.vtkImageSlice()
        actor.SetMapper(mapper)

        # MRI用暖色半透明
        prop = actor.GetProperty()
        prop.SetColorWindow(1500)
        prop.SetColorLevel(500)
        prop.SetOpacity(0.5)  # 半透明

        renderer.AddActor(actor)

    def update_fusion_transform(self, matrix: np.ndarray):
        """更新融合变换矩阵"""
        self.fusion_transform = matrix
        # MRI叠加的变换由VTK的SetUserMatrix处理
        # 这里需要重新更新叠加层
        self.vtk_widget.GetRenderWindow().Render()

    def _on_slice_changed(self, value):
        """切片滚动条"""
        self.vtk_widget.GetRenderWindow().Render()
