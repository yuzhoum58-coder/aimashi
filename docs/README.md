# 多模态医学影像手动配准浏览器 — 研发资料

> 技术方案: Python桌面端 (PySide6 + VTK + SimpleITK)
> 代码仓库: https://github.com/yuzhoum58-coder/aimashi

## 目录

### 调研文档
| 文件 | 说明 |
|:----|:-----|
| `research/01_feasibility_report_python.md` | Python方案可行性报告 — 纯Python能做，手动配准比浏览器快2-3倍 |
| `research/02_python_library_survey.md` | Python开源库全调研 — 15库+5参考项目，三级推荐 |
| `research/03_requirements_v0.2.md` | 产品需求文档 v0.2 — Python桌面方案 |
| `research/04_development_plan.md` | 3周MVP开发计划 — 分3阶段，按天排期 |

### 参考资源
| 文件 | 说明 |
|:----|:-----|
| `references/open_source_projects.md` | 开源参考项目清单 — 含GitHub链接、Star数、可参考内容 |

## 核心技术栈

```
PySide6 6.9.3 → GUI框架 (LGPL)
VTK 9.6.2    → 3D渲染/MPR/体绘制 (BSD-3)
SimpleITK    → DICOM读取/配准/分割 (Apache-2.0)
pydicom      → DICOM解析 (MIT)
numpy/scipy  → 矩阵运算 (BSD)
scikit-image → 阈值/形态学 (BSD-3)
```
