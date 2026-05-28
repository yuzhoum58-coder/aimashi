# 【产品需求】多模态影像配准浏览器开发 — 需求文档 v0.2（Python桌面方案）

> 来源: 多模态影像配准浏览器开发 KB (yYvRpkDY)

# 多模态影像配准浏览器开发 — 产品需求文档 v0.2

> 更新说明：基于Python可行性报告结论，技术路线从纯浏览器前端调整为Python桌面端
> 更新日期：2026-05-28

## 1. 产品定位

替代 Mimics 26，专注骨科场景：多模态配准 + 分割建模 + 手术规划工具。

## 2. 技术路线

**选定方案：Python桌面端** (PySide6 + VTK + SimpleITK)
- 原因：手动配准阶段Python方案开发快2-3倍，配准库成熟度高
- 详见：【可行性报告】Python桌面端多模态医学影像手动配准浏览器

## 3. 核心需求（P0 — MVP阶段，合计3周）

| 编号 | 需求 | 实现方案 | 工期 |
|:----:|:----|:---------|:----:|
| P0-1 | DICOM序列读取（CT+MRI） | pydicom + SimpleITK | 2天 |
| P0-2 | 序列管理（加载+切换） | Python文件系统索引 | 1天 |
| P0-3 | 四视图（横断/矢状/冠状/3D） | VTK多视口渲染 | 3天 |
| P0-4 | 三维体渲染（VR） | VTK GPU体绘制 | 2天 |
| P0-5 | 多模态叠加（CT+MRI混合） | VTK多volume叠加+透明度 | 2天 |
| P0-6 | **手动配准（6DOF）** | 6轴滑条→SimpleITK Transform→VTK实时 | 3天 |
| P0-7 | 变换矩阵实时显示+导出 | numpy .npy/.tfm | 1天 |
| P0-8 | 窗宽窗位调节 | VTK PiecewiseFunction | 1天 |
| P0-9 | 阈值分割+三维网格模型 | SimpleITK+VTK MarchingCubes | 3天 |
| P0-10 | 模拟置钉（圆柱体） | VTK vtkCylinderSource | 1天 |

## 4. 技术栈

| 层级 | 选型 | License | 
|:----|:-----|:--------|
| GUI框架 | PySide6 | LGPL ✅ |
| 3D渲染 | VTK 9.4+ | BSD-3 ✅ |
| 医学图像处理+配准 | SimpleITK | Apache-2.0 ✅ |
| DICOM解析 | pydicom | MIT ✅ |
| 矩阵/变换运算 | numpy + scipy | BSD ✅ |
| 图像处理 | scikit-image | BSD-3 ✅ |
| 打包 | PyInstaller + UPX | GPL ⚠️（仅打包工具） |

## 5. 开发计划（3周MVP）

- 第1周：PySide6框架+VTK视口+DICOM读取 → 四视图显示
- 第2周：多模态叠加+窗宽窗位+**手动配准**（核心）
- 第3周：阈值分割+3D模型+模拟置钉+导出功能

## 6. 与v0.1（浏览器方案）的主要变更

- 浏览器技术栈（Cornerstone3D/VTK.js/ITK-Wasm）→ Python桌面技术栈（PySide6/VTK/SimpleITK）
- 手动配准实现从ITK-Wasm改为SimpleITK原生
- 开发周期从8-12周缩短到3周
