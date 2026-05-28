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

## 开源库路线

| 层级 | 选型 | 用途 |
|:----|:-----|:-----|
| GUI框架 | **PySide6** | 桌面应用底座 |
| 3D渲染（MPR/体绘制） | **VTK 原生** | 四视图MPR + 体绘制 |
| 3D（网格/模型） | **pyvista** | VTK高级封装，省样板代码 |
| 医学图像处理 | **SimpleITK** | DICOM读序列+配准+分割 |
| DICOM解析 | **pydicom** | Tag解析 |
| 图像处理 | **scikit-image** | 阈值+形态学 |

详见 `docs/references/library_audit_report.md` 全部库的核查报告。

## 研发资料

所有调研文档、库清单、开发计划都在 `docs/` 目录下：

```
docs/
├── README.md                                    # 文档索引
├── research/                                    # 调研文档
│   ├── 01_feasibility_report_python.md           # 可行性报告
│   ├── 02_python_library_survey.md               # 15库+5项目调研
│   ├── 03_requirements_v0.2.md                   # 需求文档
│   └── 04_development_plan.md                    # 3周开发计划
└── references/
    ├── open_source_projects.md                   # 开源参考项目清单
    └── library_audit_report.md                   # 库核查报告
```
