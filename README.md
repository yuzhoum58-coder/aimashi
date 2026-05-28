# 多模态医学影像手动配准浏览器

Python桌面端 (PySide6 + VTK + SimpleITK)

## 项目定位

替代 Mimics 26 场景的骨科多模态影像浏览器，专注：
- **手动配准**（用户拖滑条对齐CT与MRI）
- 四视图联动（横断/矢状/冠状/3D）
- 多模态叠加显示
- 分割建模与模拟置钉（后续）

## 技术栈

| 层级 | 选型 |
|:----|:-----|
| GUI框架 | PySide6 (LGPL) |
| 3D渲染 | VTK 9.4+ (BSD-3) |
| 医学图像处理 | SimpleITK (Apache-2.0) |
| DICOM解析 | pydicom (MIT) |
| 变换运算 | numpy + scipy (BSD) |
| 图像处理 | scikit-image (BSD-3) |

## 安装

```bash
pip install PySide6 vtk SimpleITK pydicom numpy scipy scikit-image
```

## 运行

```bash
python -m src.main
```

## 项目结构

```
src/
├── main.py                  # 入口
├── viewer/
│   ├── main_window.py       # 主窗口 + 菜单
│   ├── dicom_loader.py      # DICOM加载
│   └── mpr_viewer.py        # 四视图MPR + 3D
├── registration/
│   ├── manual_registration.py  # 手动配准面板 (6DOF)
│   └── transform_utils.py      # 变换矩阵工具
├── segmentation/
│   └── threshold_seg.py     # 阈值分割 (待实现)
└── utils/
    └── export.py            # 导出工具
```

## 开发计划 (3周MVP)

- **第1周**: PySide6框架 + VTK四视图 + DICOM加载
- **第2周**: 多模态叠加 + 手动配准 (核心功能)
- **第3周**: 阈值分割 + 3D模型 + 模拟置钉 + 导出

## 详情

KB: https://github.com/yuzhoum58-coder/-
