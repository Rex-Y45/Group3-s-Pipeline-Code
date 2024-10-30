import os
from PySide2 import QtWidgets, QtCore
import maya.cmds as cmds
from PySide2.QtWidgets import QFileDialog
import time

class AssetLoaderTool(QtWidgets.QWidget):
    def __init__(self):
        super(AssetLoaderTool, self).__init__()
        self.setWindowTitle("Asset Loader Tool")
        self.setGeometry(300, 300, 500, 500)
        
        # 初始化项目路径
        self.project_folder = None
        self.last_modified_times = {}  # 用于存储每个资产的最新修改时间
        
        # 创建UI布局
        self.create_ui()

        # 创建定时器，用于定期检测文件更新
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.check_for_updates)
        
    def create_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # 搜索项目文件夹按钮
        self.search_btn = QtWidgets.QPushButton("Search Project Folder")
        self.search_btn.clicked.connect(self.select_project_folder)
        layout.addWidget(self.search_btn)

        # 显示选定的项目路径
        self.project_path_display = QtWidgets.QLabel("No project folder selected")
        layout.addWidget(self.project_path_display)

        # 序列选择下拉菜单
        self.sequence_combo = QtWidgets.QComboBox()
        self.sequence_combo.addItem("Empty")  
        self.sequence_combo.currentIndexChanged.connect(self.update_shot_list)
        layout.addWidget(QtWidgets.QLabel("Sequence"))
        layout.addWidget(self.sequence_combo)

        # 镜头选择
        self.shot_combo = QtWidgets.QComboBox()
        self.shot_combo.addItem("Empty")  
        self.shot_combo.currentIndexChanged.connect(self.update_asset_types)
        layout.addWidget(QtWidgets.QLabel("Shot"))
        layout.addWidget(self.shot_combo)

        # 资产类型列表
        self.asset_type_list = QtWidgets.QListWidget()
        layout.addWidget(QtWidgets.QLabel("Detected Asset Types"))
        layout.addWidget(self.asset_type_list)

        # 加载按钮
        self.load_btn = QtWidgets.QPushButton("Load Latest Asset Versions")
        self.load_btn.clicked.connect(self.load_assets)
        layout.addWidget(self.load_btn)

        # 检测更新按钮
        self.detect_update_btn = QtWidgets.QPushButton("Start Detecting Asset Updates")
        self.detect_update_btn.clicked.connect(self.start_detection)
        layout.addWidget(self.detect_update_btn)

        # 回滚选择
        self.rollback_combo = QtWidgets.QComboBox()
        layout.addWidget(QtWidgets.QLabel("Select Version to Rollback"))
        layout.addWidget(self.rollback_combo)

        # 回滚按钮
        self.rollback_btn = QtWidgets.QPushButton("Rollback to Selected Version")
        self.rollback_btn.clicked.connect(self.rollback_version)
        layout.addWidget(self.rollback_btn)

        # 设置主布局
        self.setLayout(layout)

    def select_project_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.project_folder = folder
            self.project_path_display.setText(f"Selected Project: {self.project_folder}")
            self.update_sequence_list()
            self.last_modified_times.clear()  # 清空旧的时间记录

    def update_sequence_list(self):
        self.sequence_combo.clear()
        
        sequence_path = os.path.join(self.project_folder, "publish", "sequence")
        if os.path.exists(sequence_path):
            sequences = [d for d in os.listdir(sequence_path) if os.path.isdir(os.path.join(sequence_path, d))]
            self.sequence_combo.addItems(sequences)
        else:
            self.sequence_combo.addItem("Empty")

    def update_shot_list(self):
        self.shot_combo.clear()
        
        sequence = self.sequence_combo.currentText()
        if sequence == "Empty":
            self.shot_combo.addItem("Empty")
            return
        
        shot_path = os.path.join(self.project_folder, "publish", "sequence", sequence)
        shots = [d for d in os.listdir(shot_path) if os.path.isdir(os.path.join(shot_path, d))]
        
        if shots:
            self.shot_combo.addItems(shots)
        else:
            self.shot_combo.addItem("Empty")

    def update_asset_types(self):
        """根据选定镜头更新资产类型列表"""
        self.asset_type_list.clear()
        
        sequence = self.sequence_combo.currentText()
        shot = self.shot_combo.currentText()
        
        if sequence == "Empty" or shot == "Empty":
            return

        # 构建镜头路径
        shot_path = os.path.join(self.project_folder, "publish", "sequence", sequence, shot)
        if not os.path.exists(shot_path):
            print(f"Shot path does not exist: {shot_path}")
            return

        required_assets = {
            "set": os.path.join("set", "source"),
            "layout (camera)": os.path.join("layout", "caches", "fbx"),
            "character animation cache": os.path.join("animation", "caches", "alembic"),
            "prop cache": os.path.join("prop", "caches", "alembic")
        }
        
        for asset_type, subfolder in required_assets.items():
            asset_folder = os.path.join(shot_path, subfolder)
            print(f"Checking asset folder for {asset_type}: {asset_folder}")
            if os.path.exists(asset_folder):
                versions = sorted([f for f in os.listdir(asset_folder) if f.endswith((".mb", ".fbx", ".abc", ".ma"))])
                if versions:
                    latest_file = os.path.join(asset_folder, versions[-1])
                    self.asset_type_list.addItem(f"{asset_type} - {versions[-1]}")
                    self.last_modified_times[latest_file] = os.path.getmtime(latest_file)
                else:
                    print(f"No matching files found in {asset_folder}")
            else:
                print(f"Asset folder not found for {asset_type}: {asset_folder}")

    def load_assets(self):
        sequence = self.sequence_combo.currentText()
        shot = self.shot_combo.currentText()
        
        if sequence == "Empty" or shot == "Empty":
            cmds.warning("Please select a sequence and shot.")
            return

        shot_path = os.path.join(self.project_folder, "publish", "sequence", sequence, shot)
        required_assets = {
            "set": os.path.join("set", "source"),
            "layout (camera)": os.path.join("layout", "caches", "fbx"),
            "character animation cache": os.path.join("animation", "caches", "alembic"),
            "prop cache": os.path.join("prop", "caches", "alembic")
        }
        
        for asset_type, subfolder in required_assets.items():
            asset_folder = os.path.join(shot_path, subfolder)
            if os.path.exists(asset_folder):
                versions = sorted([f for f in os.listdir(asset_folder) if f.endswith((".mb", ".fbx", ".abc", ".ma"))])
                if versions:
                    latest_file = os.path.join(asset_folder, versions[-1])
                    namespace = f"{sequence}_{shot}_{asset_type.replace(' ', '_')}"
                    try:
                        cmds.file(latest_file, reference=True, namespace=namespace)
                        print(f"Loaded {latest_file} with namespace {namespace}")
                    except Exception as e:
                        cmds.warning(f"Failed to load asset {latest_file}: {e}")

    def start_detection(self):
        if not self.update_timer.isActive():
            self.update_timer.start(10000)  # 每10秒检测一次
            self.detect_update_btn.setText("Stop Detecting Asset Updates")
        else:
            self.update_timer.stop()
            self.detect_update_btn.setText("Start Detecting Asset Updates")

    def check_for_updates(self):
        for asset_path, last_modified in self.last_modified_times.items():
            if os.path.exists(asset_path):
                current_modified = os.path.getmtime(asset_path)
                if current_modified > last_modified:
                    self.last_modified_times[asset_path] = current_modified
                    QtWidgets.QMessageBox.information(
                        self,
                        "Asset Update Detected",
                        f"An update for {os.path.basename(asset_path)} is available."
                    )

    def rollback_version(self):
        sequence = self.sequence_combo.currentText()
        shot = self.shot_combo.currentText()
        asset_type = self.asset_type_list.currentItem().text().split(" - ")[0] if self.asset_type_list.currentItem() else None
        selected_version = self.rollback_combo.currentText()

        if not asset_type or selected_version == "":
            cmds.warning("Please select an asset and version to rollback.")
            return

        asset_folder = os.path.join(self.project_folder, "publish", "sequence", sequence, shot, asset_type, "source")
        rollback_file = os.path.join(asset_folder, selected_version)

        namespace = f"{sequence}_{shot}_{asset_type.replace(' ', '_')}_rollback"
        try:
            cmds.file(rollback_file, reference=True, namespace=namespace)
            print(f"Rolled back to {rollback_file} with namespace {namespace}")
        except Exception as e:
            cmds.warning(f"Failed to rollback to version {selected_version}: {e}")

def show_tool():
    if cmds.window("assetLoaderWindow", exists=True):
        cmds.deleteUI("assetLoaderWindow", window=True)
    
    global asset_loader_window
    asset_loader_window = AssetLoaderTool()
    asset_loader_window.show()

# 启动工具
show_tool()
