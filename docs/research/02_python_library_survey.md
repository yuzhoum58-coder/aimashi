# 【Python开源库清单】医学影像桌面开发 — 全库调研

> 来源: 多模态影像配准浏览器开发 KB (yYvRpkDY)

# Python医学影像桌面开发 — 高质量开源库清单

> 更新时间：2026-05-28
> 适用场景：多模态医学影像浏览器（CT+MRI），手动配准，三维可视化，分割建模

## 📊 核心库速查表

| 库名 | 版本 | ⭐ Stars | License | 定位 | 推荐度 |
|:----|:----:|:-------:|:-------:|:----|:------:|
| **VTK** | 9.4+ | ~12k | BSD-3-Clause | 3D渲染引擎（医用级） | ⭐⭐⭐ |
| **SimpleITK** | 2.4+ | ~1.3k | Apache-2.0 | 医学图像处理+配准 | ⭐⭐⭐ |
| **pydicom** | 3.1+ | ~2.3k | MIT | DICOM文件解析 | ⭐⭐⭐ |
| **PySide6** | 6.7+ | ~1.5k | LGPL | Qt6 Python绑定（GUI框架） | ⭐⭐⭐ |
| **numpy/scipy** | 1.26+/1.14+ | — | BSD | 矩阵运算+变换 | ⭐⭐⭐ |
| **scikit-image** | 0.25+ | ~6.2k | BSD-3-Clause | 图像处理（阈值/形态学） | ⭐⭐⭐ |
| **nibabel** | 5.2+ | ~620 | MIT | 医学图像格式读写（NIfTI为主） | ⭐⭐ |
| **napari** | 0.4.19+ | ~8.5k | BSD-3-Clause | 多维图像查看器 | ⭐⭐ |
| **PyQtGraph** | 0.13+ | ~3.9k | MIT | 科学绘图控件 | ⭐⭐ |
| **MONAI** | 1.4+ | ~6.5k | Apache-2.0 | 深度学习医学影像框架 | ⭐⭐ |
| **dipy** | 1.9+ | ~700 | BSD-3-Clause | 弥散张量成像分析 | ⭐ |
| **cellpose** | 3.0+ | ~3.2k | BSD-3-Clause | 深度学习细胞分割（可迁移） | ⭐ |
| **ANTsPy** | 0.3+ | ~800 | Apache-2.0 | 图像配准（ANTs Python封装） | ⭐ |
| **itk-elastix** | — | — | Apache-2.0 | 弹性配准（Elastix封装） | ⭐ |

---

## 🏆 Tier 1：核心依赖（项目基石，必用）

### 1. VTK — Visualization Toolkit

| 项目 | 内容 |
|:----|:-----|
| **GitHub** | https://github.com/Kitware/VTK |
| **Stars** | ~12,000 |
| **版本** | 9.4.1 (2025) |
| **License** | BSD-3-Clause |
| **PyPI** | `pip install vtk` |

**能做什么：**
- GPU体绘制（Volume Rendering）— 医用级别
- 多平面重建（MPR—Multiplanar Reformatting）
- 三维表面重建（Marching Cubes）
- 多图层叠加渲染（CT+MRI混合可视化）
- 几何体渲染（模拟螺钉/克氏针）
- 交互操作（旋转/缩放/平移/切割）

**与本项目的关系：** 渲染引擎核心。四视图、VR、多模态叠加、模拟置钉，全部依赖VTK。
**坑：** 多视口之间的事件路由需要自行处理（Qt的QVTKRenderWindowInteractor不支持多视口独立交互，需要hack）。

**Python安装：** `pip install vtk` 即装即用，无需编译。

---

### 2. SimpleITK — Simplified Insight Toolkit

| 项目 | 内容 |
|:----|:-----|
| **GitHub** | https://github.com/SimpleITK/SimpleITK |
| **Stars** | ~1,300 |
| **版本** | 2.4.1 (2025) |
| **License** | Apache-2.0 |
| **PyPI** | `pip install SimpleITK` |

**能做什么：**
- DICOM序列读取（转换为numpy array）
- 图像重采样与空间变换
- **手动配准：** `Euler3DTransform`（6DOF刚性）配合`Resample`
- **点对配准：** `LandmarkBasedTransformInitializer`（对应点初始化变换）
- 阈值分割 + Connected Component分析
- 图像滤波（高斯、中值、双边等）

**与本项目的关系：** 配准核心。读DICOM→numpy→配准→重采样整个管线由它承担。
**手动配准API示例：**
```python
import SimpleITK as sitk
# 创建6DOF变换
transform = sitk.Euler3DTransform()
transform.SetTranslation([tx, ty, tz])
transform.SetRotation(rx, ry, rz)  # 弧度
# 重采样
resampled = sitk.Resample(moving, fixed, transform, sitk.sitkLinear)
```

**坑：** DICOM读取时如果序列顺序不连续会报错，需先排序。ImagePositionPatient必须一致。

---

### 3. pydicom — DICOM ToolKit

| 项目 | 内容 |
|:----|:-----|
| **GitHub** | https://github.com/pydicom/pydicom |
| **Stars** | ~2,300 |
| **版本** | 3.1.0 (2025) |
| **License** | MIT |
| **PyPI** | `pip install pydicom` |

**能做什么：**
- 读取/写入/修改DICOM文件
- 解析所有标准+私有Tag
- DICOMDIR目录解析
- 序列组织与排序
- 像素数据解压（JPEG/JPEG2000/RLE等压缩格式）

**与本项目的关系：** DICOM解析器。获取像素数据+空间坐标信息（ImagePositionPatient, PixelSpacing, ImageOrientationPatient等）。
**注意：** 多帧DICOM（Enhanced MR/CT）也支持，但需要`pydicom.encaps`处理。

---

### 4. PySide6 — Qt for Python

| 项目 | 内容 |
|:----|:-----|
| **GitHub** | https://github.com/qtproject/pyside-pyside-setup |
| **Stars** | ~1,500 |
| **版本** | 6.7.3 (2025) |
| **License** | LGPL-3.0 / GPL-2.0 |
| **PyPI** | `pip install PySide6` |

**能做什么：**
- 完整的桌面GUI框架
- Qt Widgets（按钮、滑动条、面板、菜单）
- QVTKRenderWindowInteractor（VTK嵌入Qt的桥接，需要pip install PySide6-QtVTK）
- 信号/槽机制（滑动条值变化→VTK重绘）
- 多线程支持（后台加载DICOM不卡界面）

**为什么选PySide6而不是PyQt6：**
- PySide6是Qt官方维护，LGPL许可证友好（商业可用）
- PyQt6是Riverbank第三方维护，GPL许可证（商业要额外付费）
- PySide6社区更大，更新更快

---

### 5. scikit-image

| 项目 | 内容 |
|:----|:-----|
| **GitHub** | https://github.com/scikit-image/scikit-image |
| **Stars** | ~6,200 |
| **版本** | 0.25.2 (2025) |
| **License** | BSD-3-Clause |
| **PyPI** | `pip install scikit-image` |

**能做什么：**
- 阈值分割（Otsu, Li, Yen, Triangle等10+算法）
- 形态学操作（膨胀/腐蚀/开闭/骨架化）
- 连通组件分析
- 边缘检测
- 图像滤波器

**与本项目的关系：** 阈值分割管线的主力。

---

## 🥈 Tier 2：重要辅助库（推荐使用）

### 6. napari

| 项目 | 内容 |
|:----|:-----|
| **GitHub** | https://github.com/napari/napari |
| **Stars** | ~8,500 |
| **版本** | 0.4.19 (2024) |
| **License** | BSD-3-Clause |
| **PyPI** | `pip install napari[all]` |

**能做什么：**
- 快速多维图像可视化
- 图层叠加管理（多模态超融合显示）
- 点/形状/标签层标注
- 插件系统
- **内置手动配准时：** 支持图层独立变换参数

**与本项目的关系：** **可作为快速原型验证工具**。如果用napari做原型，几个小时内就能验证多模态叠加+手动变换效果。但napari不是完整的桌面应用框架，**不适合作为最终产品**（无四视图、无DICOM序列管理）。

**建议：** 用napari做配准算法验证的沙盒，正式产品用PySide6+VTK开发。

---

### 7. nibabel

| 项目 | 内容 |
|:----|:-----|
| **GitHub** | https://github.com/nipy/nibabel |
| **Stars** | ~620 |
| **版本** | 5.2.1 (2024) |
| **License** | MIT |
| **PyPI** | `pip install nibabel` |

**能做什么：**
- 读写NIfTI（.nii / .nii.gz）、ANALYZE、MGH/MGZ等格式
- 仿射矩阵解析
- 图像方向处理

**与本项目的关系：** 如果用户后续需要导出到NIfTI用于AI训练（MONAI）时使用。核心项目（DICOM为主）中不是必需品。

---

### 8. PyQtGraph

| 项目 | 内容 |
|:----|:-----|
| **GitHub** | https://github.com/pyqtgraph/pyqtgraph |
| **Stars** | ~3,900 |
| **版本** | 0.13.3 (2024) |
| **License** | MIT / BSD-3-Clause |
| **PyPI** | `pip install pyqtgraph` |

**能做什么：**
- 快速2D图像显示（比matplotlib快50x）
- 直方图绘制（用于窗宽窗位调节参考）
- ROI绘制
- 实时数据更新

**与本项目的关系：** 可替代VTK做2D视图部分（横断/矢冠），但VTK已经能覆盖2D+3D，引入PyQtGraph会增加架构复杂度。**建议只在需要直方图或图表功能时使用。**

---

## 🥉 Tier 3：可扩展/后续用

### 9. MONAI — Medical Open Network for AI

| 项目 | 内容 |
|:----|:-----|
| **GitHub** | https://github.com/Project-MONAI/MONAI |
| **Stars** | ~6,500 |
| **版本** | 1.4.1 (2025) |
| **License** | Apache-2.0 |
| **PyPI** | `pip install monai` |

**能做什么：**
- 深度学习分割（UNet, UNETR, SwinUNETR等）
- 深度学习配准
- 数据预处理管线
- 与PyTorch深度集成

**与本项目的关系：** 后续引入AI配准/自动分割时使用。**手动配准阶段不需要。**

---

### 10. cellpose

| 项目 | 内容 |
|:----|:-----|
| **GitHub** | https://github.com/MouseLand/cellpose |
| **Stars** | ~3,200 |
| **版本** | 3.0.5 (2025) |
| **License** | BSD-3-Clause |

**能做什么：** 通用细胞/物体分割。如果未来需要做软组织（如腘动脉）自动分割，可迁移使用。

---

### 11. dipy

| 项目 | 内容 |
|:----|:-----|
| **GitHub** | https://github.com/dipy/dipy |
| **Stars** | ~700 |
| **License** | BSD-3-Clause |

**能做什么：** 弥散MRI分析，包含仿射配准模块。非核心需要。

---

### 12. ANTsPy

| 项目 | 内容 |
|:----|:-----|
| **GitHub** | https://github.com/ANTsX/ANTsPy |
| **Stars** | ~800 |
| **Version** | 0.3.3 (2024) |
| **License** | Apache-2.0 |

**能做什么：** 高级图像配准（包含SyN弹性配准）。安装较复杂（依赖C++编译），可延后。

---

## 🔍 现有完整项目参考

| 项目 | 定位 | 可借鉴内容 |
|:----|:----|:----------|
| **3D Slicer** (C++ / Python scriptable) | 最成熟的医学影像平台 | 架构思路、模块化设计（但C++核心，不可直接复用） |
| **ITK-Snap** (C++ / Python plugin) | 半自动分割标杆 | 主动轮廓分割的交互设计 |
| **DICOM Viewer (radiomics)** | PyQt5 + pydicom | 基础的DICOM序列管理+MPR + 开源参考 ~250⭐ |
| **PyDICOMViewer** | VTK + PyQt, MPR + 3D | VTK+Qt集成方式参考 ~180⭐ |
| **medpy-viewer** | Medical Python viewer | 医学图像查看器 ~100⭐ |

**建议：** 重点看 **DICOM Viewer (radiomics)** 和 **PyDICOMViewer** 的源码，理解VTK+Qt的集成模式。不推荐直接fork，因为用了较老的VTK/PyQt5版本。

---

## 📦 最终推荐安装清单（MVP阶段）

```bash
pip install PySide6               # GUI框架
pip install vtk                    # 3D渲染
pip install SimpleITK              # DICOM读取+配准
pip install pydicom                # DICOM解析
pip install numpy scipy            # 矩阵运算
pip install scikit-image           # 图像处理
# 可选（MVP阶段不需要）：
# pip install napari               # 快速原型验证
# pip install nibabel              # NIfTI导出
# pip install PyQtGraph            # 图表
```

总依赖大小估算：~200MB（主要在VTK和PySide6）
