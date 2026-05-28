# 开源库核查报告 — 按MVP优先级

> 核查日期: 2026-05-28
> 目标: 确认每条技术路线的依赖库，哪些已装、哪些缺、哪些值得加

---

## 核查结果总表

| 库 | MVP阶段需要？ | 已安装？ | 推荐？ | 说明 |
|:---|:-----------:|:-------:|:-----:|:----|
| **PySide6** | ✅ 核心 | ✅ 6.9.3 | ✅ | GUI框架，整个应用的底座 |
| **VTK** | ✅ 核心 | ✅ 9.6.2 | ✅ | 3D渲染/MPR/体绘制/网格生成 |
| **SimpleITK** | ✅ 核心 | ✅ 2.5.5 | ✅ | DICOM读序列+配准+分割 |
| **pydicom** | ✅ 核心 | ✅ 3.0.2 | ✅ | DICOM tag解析 |
| **numpy** | ✅ 核心 | ✅ 2.4.4 | ✅ | 矩阵运算，整个数据层的基础 |
| **scipy** | ✅ 核心 | ✅ 1.17.1 | ✅ | 旋转矩阵、插值 |
| **scikit-image** | ✅ 核心 | ✅ 0.26.0 | ✅ | 阈值分割、形态学操作 |
| **pyvista** | ⚠️ 建议加 | ❌ | **✅推荐** | VTK高级封装，3D网格/体绘制省大量样板代码 |
| **pyvistaqt** | ⚠️ 建议加 | ❌ | **✅推荐** | pyvista嵌入PySide6，比原生QVTKWidget简洁 |
| **vedo** | ❌ 不急需 | ❌ | ❌跳过 | 功能与pyvista重叠，选pyvista一个即可 |
| **pynetdicom** | ❌ 后续 | ❌ | ⏳P3 | 等需要PACs联通再加 |
| **itk-elastix** | ❌ 后续 | ❌ | ⏳P2 | 等做自动配准再加 |
| **3D Slicer** | 🔍 参考 | N/A | 🔍 架构参考 | C++核心，不可直接复用，看架构 |
| **MITK** | 🔍 参考 | N/A | 🔍 参考 | C++核心，同上 |
| **ITK-SNAP** | 🔍 参考 | N/A | 🔍 交互参考 | 分割交互设计值得看 |

---

## 按优先级分类

### P0 — MVP必装（已在requirements.txt）
```
PySide6 vtk SimpleITK pydicom numpy scipy scikit-image
```

### P1 — 建议加（我现在装）
```
pyvista pyvistaqt
```

### P2 — 后续阶段再加
```
pynetdicom          # 等需要PACs联通
itk-elastix         # 等做自动配准
```

### P3 — 参考架构，不装到项目里
```
3D Slicer           # 看代码架构，不可复用
MITK                # 同上
ITK-SNAP            # 看交互设计
```

---

## 关于pyvista vs 原生VTK —— 我的推荐

经过实测评估，**我建议两者都用，分工明确**：

| 场景 | 用哪个 | 原因 |
|:----|:------|:-----|
| **MPR四视图**（横矢冠切片） | 原生VTK | pyvista的`pyvista.ImageData`切片能力有限，没有现成的vtkImageResliceMapper多方向切片支持 |
| **3D体绘制（VR）** | **pyvista** | `plotter.add_volume()`一行代码搞定，原生VTK要写20+行 |
| **三维网格模型**（MarchingCubes→STL） | **pyvista** | `mesh = volume.contour()`一行搞定，原生VTK需要vtkDiscreteMarchingCubes+vtkWindowedSincPolyDataFilter等5-6个filter串联 |
| **模拟置钉（圆柱体）** | **pyvista** | `cylinder = pv.Cylinder()`直接生成，可加变换和颜色 |
| **变换矩阵应用** | 原生VTK / pyvista | 两者都支持，pyvista的`.transform()`也能用 |
| **QVTK集成到PySide6** | **pyvistaqt** | `QtInteractor`比原生`QVTKRenderWindowInteractor`少了很多样板代码 |

**结论：** MPR手动配准用原生VTK（底层可控），3D展示/网格/模型用pyvista（省代码）。
