"""
主窗口 — PySide6 + VTK 四视图布局
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QFileDialog, QMenuBar, QMenu, QStatusBar
)
from PySide6.QtCore import Qt, Signal
from src.viewer.dicom_loader import DicomLoader
from src.viewer.mpr_viewer import MPRViewerWidget
from src.registration.manual_registration import ManualRegistrationPanel


class MainWindow(QMainWindow):
    """主窗口：左侧四视图 + 右侧配准控制面板"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("多模态医学影像手动配准浏览器")
        self.resize(1600, 1000)

        self.dicom_loader = DicomLoader()
        self._setup_ui()
        self._setup_menus()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        # 左侧：四视图（MPR + 3D）
        self.mpr_viewer = MPRViewerWidget()
        splitter.addWidget(self.mpr_viewer)

        # 右侧：配准控制面板
        self.registration_panel = ManualRegistrationPanel()
        self.registration_panel.transform_changed.connect(self._on_transform_changed)
        splitter.addWidget(self.registration_panel)

        splitter.setSizes([1100, 500])
        layout.addWidget(splitter)

        self.statusBar().showMessage("就绪 — 打开DICOM文件开始")

    def _setup_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件(&F)")

        open_ct = file_menu.addAction("打开CT序列...")
        open_ct.triggered.connect(self._open_ct)
        open_ct.setShortcut("Ctrl+O")

        open_mri = file_menu.addAction("打开MRI序列...")
        open_mri.triggered.connect(self._open_mri)

        file_menu.addSeparator()

        export_action = file_menu.addAction("导出变换矩阵...")
        export_action.triggered.connect(self._export_transform)
        export_action.setShortcut("Ctrl+E")

        file_menu.addSeparator()

        exit_action = file_menu.addAction("退出")
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")

    def _open_ct(self):
        folder = QFileDialog.getExistingDirectory(self, "选择CT序列文件夹")
        if folder:
            self.statusBar().showMessage(f"加载CT: {folder}")
            volume, metadata = self.dicom_loader.load_series(folder)
            if volume is not None:
                self.mpr_viewer.set_volume(volume, metadata, "CT")
                self.statusBar().showMessage(f"CT已加载: {metadata.get('series_description', '')} ({volume.shape[0]}层)")

    def _open_mri(self):
        folder = QFileDialog.getExistingDirectory(self, "选择MRI序列文件夹")
        if folder:
            self.statusBar().showMessage(f"加载MRI: {folder}")
            volume, metadata = self.dicom_loader.load_series(folder)
            if volume is not None:
                self.mpr_viewer.set_volume(volume, metadata, "MRI")
                self.statusBar().showMessage(f"MRI已加载: {metadata.get('series_description', '')} ({volume.shape[0]}层)")

    def _on_transform_changed(self, transform_matrix):
        """手动配准滑块变化 → 更新VTK渲染"""
        self.mpr_viewer.update_fusion_transform(transform_matrix)

    def _export_transform(self):
        from src.utils.export import export_transform_matrix
        export_transform_matrix(self, self.registration_panel.get_current_matrix())
