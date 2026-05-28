"""
主窗口 — PySide6 + VTK 四视图布局
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QFileDialog, QMenuBar, QMenu,
    QStatusBar, QMessageBox
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from src.viewer.dicom_loader import DicomLoader
from src.viewer.mpr_viewer import MPRViewerWidget
from src.registration.manual_registration import ManualRegistrationPanel
from src.utils.test_data import generate_ct_phantom, generate_mri_phantom


class MainWindow(QMainWindow):
    """主窗口：左侧四视图MPR + 右侧配准控制面板"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("多模态医学影像手动配准浏览器")
        self.resize(1600, 1000)

        self.dicom_loader = DicomLoader()
        self._setup_ui()
        self._setup_menus()
        self._setup_test_data()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        # 左侧：四视图MPR + 3D
        self.mpr_viewer = MPRViewerWidget()
        splitter.addWidget(self.mpr_viewer)

        # 右侧：配准控制面板
        self.registration_panel = ManualRegistrationPanel()
        self.registration_panel.transform_changed.connect(self._on_transform_changed)
        splitter.addWidget(self.registration_panel)

        splitter.setSizes([1100, 500])
        layout.addWidget(splitter)

        self.statusBar().showMessage("就绪 — 已加载合成测试数据")

    def _setup_menus(self):
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        act = file_menu.addAction("打开CT序列...")
        act.triggered.connect(self._open_ct)
        act.setShortcut("Ctrl+O")
        
        act = file_menu.addAction("打开MRI序列...")
        act.triggered.connect(self._open_mri)
        
        file_menu.addSeparator()
        
        act = file_menu.addAction("导出变换矩阵...")
        act.triggered.connect(self._export_transform)
        act.setShortcut("Ctrl+E")
        
        file_menu.addSeparator()
        
        act = file_menu.addAction("退出")
        act.triggered.connect(self.close)
        act.setShortcut("Ctrl+Q")

        # 测试菜单
        test_menu = menubar.addMenu("测试(&T)")
        act = test_menu.addAction("加载合成CT体模")
        act.triggered.connect(self._load_test_ct)
        act = test_menu.addAction("加载合成CT+MRI (双模态)")
        act.triggered.connect(self._load_test_both)

    # ── 合成测试数据 ──────────────────────────────────────

    def _setup_test_data(self):
        """启动时自动加载合成测试数据"""
        self._load_test_both()

    def _load_test_ct(self):
        self.statusBar().showMessage("生成合成CT体模...")
        ct = generate_ct_phantom(128, 64)
        self.mpr_viewer.set_volume(ct, {"modality": "CT", "series_description": "合成CT体模"}, "CT")
        self.statusBar().showMessage("合成CT体模已加载")

    def _load_test_both(self):
        self.statusBar().showMessage("生成合成CT+MRI双模态数据...")
        ct = generate_ct_phantom(128, 64)
        mri = generate_mri_phantom(128, 64)
        self.mpr_viewer.set_volume(ct, {"modality": "CT", "series_description": "合成CT"}, "CT")
        self.mpr_viewer.set_volume(mri, {"modality": "MRI", "series_description": "合成MRI"}, "MRI")
        self.statusBar().showMessage("✅ CT+MRI双模态合成数据已加载")

    # ── DICOM加载 ─────────────────────────────────────────

    def _open_ct(self):
        folder = QFileDialog.getExistingDirectory(self, "选择CT序列文件夹")
        if folder:
            self.statusBar().showMessage(f"加载CT: {folder}")
            volume, metadata = self.dicom_loader.load_series(folder)
            if volume is not None:
                self.mpr_viewer.set_volume(volume, metadata, "CT")
                desc = metadata.get('series_description', '')
                self.statusBar().showMessage(f"CT已加载: {desc} ({volume.shape[0]}层)")
            else:
                QMessageBox.warning(self, "加载失败", f"无法读取DICOM序列:\n{folder}")

    def _open_mri(self):
        folder = QFileDialog.getExistingDirectory(self, "选择MRI序列文件夹")
        if folder:
            self.statusBar().showMessage(f"加载MRI: {folder}")
            volume, metadata = self.dicom_loader.load_series(folder)
            if volume is not None:
                self.mpr_viewer.set_volume(volume, metadata, "MRI")
                desc = metadata.get('series_description', '')
                self.statusBar().showMessage(f"MRI已加载: {desc} ({volume.shape[0]}层)")
            else:
                QMessageBox.warning(self, "加载失败", f"无法读取DICOM序列:\n{folder}")

    # ── 配准 ──────────────────────────────────────────────

    def _on_transform_changed(self, matrix):
        self.mpr_viewer.update_fusion_transform(matrix)

    def _export_transform(self):
        from src.utils.export import export_transform_matrix
        export_transform_matrix(self, self.registration_panel.get_current_matrix())
