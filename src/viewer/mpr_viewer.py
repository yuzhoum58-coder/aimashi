"""
四视图MPR + 3D — 使用vtkImageReslice + vtkImageActor + vtkVolume

架构:
- 横断(Axial)/矢状(Sagittal)/冠状(Coronal): vtkImageReslice生成2D切片
- 3D视图: vtkGPUVolumeRayCastMapper体绘制
- 切片位置: 滚动条→更新reslice origin→重绘
"""
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel
from PySide6.QtCore import Qt, Signal

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class MPRViewerWidget(QWidget):
    """四视图：横断(Axial) / 矢状(Sagittal) / 冠状(Coronal) / 3D体绘制"""

    slice_changed = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.volumes = {}
        self.metadata = {}
        self.vtk_images = {}
        self.current_slice = 0
        self.max_slice = 0
        # 每个MPR视图保存: (reslice, axis_str)
        self.slice_pipelines = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.vtk_widget = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtk_widget, 1)

        ren_win = self.vtk_widget.GetRenderWindow()
        ren_win.SetSize(900, 700)
        ren_win.SetOffScreenRendering(True)

        # 四视口: 2x2
        vp = [
            (0.0, 0.5, 0.5, 1.0, "Axial",     (0.08, 0.08, 0.10)),
            (0.5, 0.5, 1.0, 1.0, "Sagittal",   (0.10, 0.08, 0.08)),
            (0.0, 0.0, 0.5, 0.5, "Coronal",    (0.08, 0.10, 0.08)),
            (0.5, 0.0, 1.0, 0.5, "3D",         (0.10, 0.10, 0.12)),
        ]
        self.renderers = {}
        for x0, y0, x1, y1, name, bg in vp:
            ren = vtk.vtkRenderer()
            ren.SetBackground(*bg)
            ren.SetViewport(x0, y0, x1, y1)
            ren_win.AddRenderer(ren)
            self.renderers[name] = ren

            # 视口标签
            txt = vtk.vtkTextActor()
            txt.SetInput(name)
            txt.GetTextProperty().SetColor(0.8, 0.8, 0.8)
            txt.GetTextProperty().SetFontSize(14)
            txt.SetDisplayPosition(10, int((y1 - y0) * 700) - 20)
            ren.AddActor2D(txt)

        self.vtk_widget.Initialize()
        self.vtk_widget.GetRenderWindow().GetInteractor().SetInteractorStyle(
            vtk.vtkInteractorStyleTrackballCamera()
        )

        # 切片滚动条
        bar = QHBoxLayout()
        bar.addWidget(QLabel("切片:"))
        self.slice_slider = QSlider(Qt.Horizontal)
        self.slice_slider.setRange(0, 100)
        self.slice_slider.setValue(50)
        self.slice_slider.valueChanged.connect(self._on_slider)
        bar.addWidget(self.slice_slider)
        self.slice_label = QLabel("0/0")
        bar.addWidget(self.slice_label)
        layout.addLayout(bar)

    # ── 数据管理 ────────────────────────────────────────

    def set_volume(self, volume: np.ndarray, meta: dict, name: str):
        self.volumes[name] = volume
        self.metadata[name] = meta
        self.vtk_images[name] = self._numpy_to_vtk(volume)
        self._rebuild_views()
        self.vtk_widget.GetRenderWindow().Render()

    def _numpy_to_vtk(self, vol: np.ndarray) -> vtk.vtkImageData:
        from vtk.util import numpy_support
        # (Z,Y,X) → VTK (X,Y,Z)
        vol_t = np.transpose(vol, (2, 1, 0)).astype(np.float32, order='C')
        img = vtk.vtkImageData()
        img.SetDimensions(*vol_t.shape)
        img.SetSpacing(1.0, 1.0, 1.0)
        arr = numpy_support.numpy_to_vtk(vol_t.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
        img.GetPointData().SetScalars(arr)
        return img

    # ── 视图重建 ────────────────────────────────────────

    def _rebuild_views(self):
        if not self.vtk_images:
            return

        primary = list(self.vtk_images.keys())[0]
        img = self.vtk_images[primary]
        dims = img.GetDimensions()
        zmax = dims[2] - 1

        self.max_slice = zmax
        self.current_slice = min(self.current_slice, zmax)
        self.slice_slider.setRange(0, zmax)
        self.slice_slider.setValue(self.current_slice)

        # MPR: 名称→(法向量, 切片轴索引, 相机轴)
        mpr = [
            ("Axial",    (0, 0, 1),  2, 'z'),
            ("Sagittal", (1, 0, 0),  0, 'x'),
            ("Coronal",  (0, 1, 0),  1, 'y'),
        ]
        self.slice_pipelines.clear()

        for pname, normal, axis_idx, ax in mpr:
            ren = self.renderers[pname]
            ren.RemoveAllViewProps()

            # vtkImageReslice — 从体数据中切出一张2D切片
            reslice = vtk.vtkImageReslice()
            reslice.SetInputData(img)
            reslice.SetOutputDimensionality(2)
            reslice.SetResliceAxesDirectionCosines(1, 0, 0, 0, 1, 0, 0, 0, 1)
            reslice.SetInterpolationModeToLinear()
            reslice.AutoCropOutputOn()

            # 设置切片位置
            origin = [0.0, 0.0, 0.0]
            origin[axis_idx] = float(self.current_slice)
            reslice.SetResliceAxesOrigin(*origin)

            reslice.Update()

            # vtkImageMapper + vtkActor2D 显示切片
            mapper = vtk.vtkImageMapper()
            mapper.SetInputData(reslice.GetOutput())
            mapper.SetColorWindow(1500)
            mapper.SetColorLevel(300)

            actor = vtk.vtkActor2D()
            actor.SetMapper(mapper)
            ren.AddActor2D(actor)

            # 如果是Axis视图且有MRI，额外加一个MRI叠加层
            if pname == "Axial" and len(self.vtk_images) > 1:
                mri_name = [k for k in self.vtk_images if k != primary][0]
                mri_img = self.vtk_images[mri_name]

                mri_reslice = vtk.vtkImageReslice()
                mri_reslice.SetInputData(mri_img)
                mri_reslice.SetOutputDimensionality(2)
                mri_reslice.SetResliceAxesDirectionCosines(1, 0, 0, 0, 1, 0, 0, 0, 1)
                mri_reslice.SetInterpolationModeToLinear()
                mri_reslice.AutoCropOutputOn()
                mri_reslice.SetResliceAxesOrigin(*origin)
                mri_reslice.Update()

                mri_mapper = vtk.vtkImageMapper()
                mri_mapper.SetInputData(mri_reslice.GetOutput())
                mri_mapper.SetColorWindow(255)
                mri_mapper.SetColorLevel(127)

                mri_actor = vtk.vtkActor2D()
                mri_actor.SetMapper(mri_mapper)
                # 半透明叠加 (通过vtkProperty的透明度)
                mri_actor.GetProperty().SetOpacity(0.4)
                ren.AddActor2D(mri_actor)

            ren.ResetCamera()
            self.slice_pipelines[pname] = (reslice, axis_idx)

        # 3D体绘制
        self._setup_3d(primary)

    def _setup_3d(self, name: str):
        ren = self.renderers["3D"]
        ren.RemoveAllViewProps()

        img = self.vtk_images[name]

        vol_map = vtk.vtkGPUVolumeRayCastMapper()
        vol_map.SetInputData(img)
        vol_map.SetAutoAdjustSampleDistances(1)
        vol_map.SetSampleDistance(0.5)

        ctf = vtk.vtkColorTransferFunction()
        ctf.AddRGBPoint(-500, 0, 0, 0)
        ctf.AddRGBPoint(100, 0.6, 0.4, 0.2)
        ctf.AddRGBPoint(400, 0.8, 0.7, 0.5)
        ctf.AddRGBPoint(1000, 1, 1, 1)

        otf = vtk.vtkPiecewiseFunction()
        otf.AddPoint(-500, 0.0)
        otf.AddPoint(100, 0.05)
        otf.AddPoint(400, 0.2)
        otf.AddPoint(1000, 0.6)

        gtf = vtk.vtkPiecewiseFunction()
        gtf.AddPoint(0, 0.0)
        gtf.AddPoint(50, 0.2)
        gtf.AddPoint(200, 0.8)

        prop = vtk.vtkVolumeProperty()
        prop.SetColor(ctf)
        prop.SetScalarOpacity(otf)
        prop.SetGradientOpacity(gtf)
        prop.SetInterpolationTypeToLinear()
        prop.ShadeOn()
        prop.SetAmbient(0.3)
        prop.SetDiffuse(0.6)
        prop.SetSpecular(0.2)

        vol = vtk.vtkVolume()
        vol.SetMapper(vol_map)
        vol.SetProperty(prop)
        ren.AddVolume(vol)
        ren.ResetCamera()
        cam = ren.GetActiveCamera()
        cam.Azimuth(45)
        cam.Elevation(30)

    # ── 切片更新 ────────────────────────────────────────

    def _on_slider(self, value):
        self.current_slice = value
        self._update_slices()
        self.slice_label.setText(f"{value}/{self.max_slice}")
        self.vtk_widget.GetRenderWindow().Render()

    def _update_slices(self):
        for pname, (reslice, axis_idx) in self.slice_pipelines.items():
            origin = [0.0, 0.0, 0.0]
            origin[axis_idx] = float(self.current_slice)
            reslice.SetResliceAxesOrigin(*origin)
            reslice.Update()

    def update_fusion_transform(self, matrix: np.ndarray):
        self.vtk_widget.GetRenderWindow().Render()
