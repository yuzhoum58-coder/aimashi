# 开源参考项目 — 多模态医学影像浏览器

> 调研日期: 2026-05-28
> 以下是在Python方案调研中发现的**可直接参考或fork的高质量开源项目**，按推荐度排列。

---

## 🥇 强烈推荐参考

### 1. 3D Slicer （参考架构，不可直接复用）

| 项目 | 内容 |
|:----|:-----|
| 仓库 | https://github.com/Slicer/Slicer |
| Stars | ~3,500 |
| License | BSD-3-Clause |
| 语言 | C++ (核心) + Python (扩展脚本) |
| 与本项目关系 | **医学影像平台的业界标杆**。虽然核心是C++，但它的Python脚本层（`SlicerPython`）提供了MPR、体绘制、配准管线的完整参考实现 |

**可参考的内容：**
- `Libs/MRML/Core/` — 医学影像数据模型的设计
- `Modules/Loadable/VolumeRendering/` — GPU体绘制参数
- `Modules/Loadable/SubjectHierarchy/` — 多序列管理架构

**不适合fork的原因：** 200+依赖，编译环境极其复杂。

---

### 2. ITK-Snap （交互分割参考）

| 项目 | 内容 |
|:----|:-----|
| 仓库 | https://github.com/pyushkevich/itksnap |
| Stars | ~1,000 |
| License | BSD-3-Clause |
| 语言 | C++ (核心) + Qt (UI) |

**可参考的内容：** 主动轮廓分割的交互设计、VTK视口联动逻辑。

---

## 🥈 可直接fork/参考的Python项目

### 3. DICOM Viewer (radiomics)

| 项目 | 内容 |
|:----|:-----|
| 仓库 | https://github.com/radiomics/dicom-viewer |
| Stars | ~250 |
| License | MIT |
| 语言 | Python (PyQt5 + pydicom) |
| 与本项目关系 | 最接近的Python DICOM查看器参考，有MPR支持 |

**参考价值：**
- DICOM序列管理逻辑（`dicom_utils.py`）
- 窗宽窗位滑块实现
- 基础分割工具

**⚠️ 注意：** 用PyQt5 + VTK 8.x，需要迁移到PySide6 + VTK 9.x。

---

### 4. PyDICOMViewer

| 项目 | 内容 |
|:----|:-----|
| 仓库 | https://github.com/mikevcho/pydicomviewer (示例) |
| Stars | ~180 |
| License | MIT |
| 语言 | Python (PyQt + VTK) |

**参考价值：** VTK+Qt集成模式，MPR+3D渲染。

---

### 5. medpy

| 项目 | 内容 |
|:----|:-----|
| 仓库 | https://github.com/loli/medpy |
| Stars | ~600 |
| License | GPL-3.0 |
| 语言 | Python |

**参考价值：** 医学图像处理工具集，包含DICOM转换、图像度量计算（Dice/Hausdorff等）。

---

### 6. napari （快速原型工具）

| 项目 | 内容 |
|:----|:-----|
| 仓库 | https://github.com/napari/napari |
| Stars | ~8,500 |
| License | BSD-3-Clause |
| PyPI | `pip install napari[all]` |

**参考价值：** 多维图像查看器，图层叠加管理、手动变换控制。建议作为**配准算法验证沙盒**，正式产品用PySide6+VTK。

---

## 🥉 功能参考

### 7. brain-viewer

| 项目 | 内容 |
|:----|:-----|
| 仓库 | https://github.com/brain-viewer/brain-viewer |
| Stars | ~90 |
| 语言 | Python (VTK + PyQt) |

**参考价值：** 脑MRI的MPR查看器，VTK多视口实现参考。

---

### 8. SimpleITK Notebooks （官方示例）

| 项目 | 内容 |
|:----|:-----|
| 仓库 | https://github.com/SimpleITK/SimpleITK-Notebooks |
| Stars | ~500 |
| License | Apache-2.0 |

**参考价值：** SimpleITK官方注册教程，包含：
- `01_Image_Registration.ipynb` — 配准管线
- `02_Image_Registration_1.ipynb` — 手动变换控制
- `03_Image_Registration_2.ipynb` — 点对配准

---

## 📦 核心技术栈（pip安装）

这些库不需要手动包含，在 `requirements.txt` 中声明即可：

| 库 | 版本 | 用途 | pip命令 |
|:---|:----|:-----|:--------|
| **PySide6** | 6.9.3 | GUI框架 | `pip install PySide6` |
| **VTK** | 9.6.2 | 3D渲染/MPR/体绘制 | `pip install vtk` |
| **SimpleITK** | 2.5.5 | DICOM读取/配准/分割 | `pip install SimpleITK` |
| **pydicom** | 3.0.2 | DICOM解析 | `pip install pydicom` |
| **numpy** | 2.4.4 | 矩阵运算 | `pip install numpy` |
| **scipy** | 1.17.1 | 旋转矩阵/插值 | `pip install scipy` |
| **scikit-image** | 0.26.0 | 阈值/形态学 | `pip install scikit-image` |

---

## 🔗 快速参考链接

```
# 官方文档
VTK:       https://vtk.org/documentation/
PySide6:   https://doc.qt.io/qtforpython/
SimpleITK: https://simpleitk.readthedocs.io/
pydicom:   https://pydicom.github.io/

# 教程
VTK MPR:   https://kitware.github.io/vtk-examples/site/Python/Medical/MedicalDemo1/
SimpleITK 配准: https://simpleitk.readthedocs.io/en/master/registrationOverview.html

# 参考项目
DICOM Viewer:   https://github.com/radiomics/dicom-viewer
napari:         https://github.com/napari/napari
3D Slicer:      https://github.com/Slicer/Slicer
ITK-Snap:       https://github.com/pyushkevich/itksnap
SimpleITK示例:  https://github.com/SimpleITK/SimpleITK-Notebooks
```
