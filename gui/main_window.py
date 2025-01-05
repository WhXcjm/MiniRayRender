from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QFileDialog, QColorDialog, QDialog
from gui.preview_widget import PreviewWidget
from model.shape_generator import ShapeGenerator
from model.add_shape import AddShapeDialog, add_shape_to_scene
from utils.logger import logger
import glm
import numpy as np
from PIL import Image
from OpenGL.GL import *


class MainWindow(QMainWindow):
    """
    主窗口，包含左侧预览窗格和右侧功能列表。
    """
    def __init__(self, light_pos = glm.vec3(-1.0, 3.0, -2.0), view = glm.lookAt(glm.vec3(0, 5, 10), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))):
        super().__init__()
        self.setWindowTitle("MiniRayRender")
        self.setGeometry(100, 100, 1200, 800)

        # 主布局
        main_layout = QHBoxLayout()

        # 左侧预览窗格
        self.preview = PreviewWidget(light_pos=light_pos, view=view)
        main_layout.addWidget(self.preview, 5)

        # 右侧功能区
        right_layout = QVBoxLayout()

        # 物体列表（改为 QTableWidget）
        self.object_list = QTableWidget()
        self.object_list.setColumnCount(3)  # 列数：名称、类型、外观
        self.object_list.setHorizontalHeaderLabels(["Name", "Type", "Appearance"])
        self.object_list.setColumnWidth(0, 81)  # 第一列
        self.object_list.setColumnWidth(1, 53)  # 第二列
        self.object_list.setColumnWidth(2, 162)  # 第三列
        right_layout.addWidget(self.object_list)

        # 添加功能按钮
        self.import_button = QPushButton("Import Object")
        self.export_button = QPushButton("Export Object")
        self.reset_button = QPushButton("Reset View")
        self.render_button = QPushButton("Render")
        self.add_shape_button = QPushButton("Add Shape")
        self.rotate_button = QPushButton("Start Rotation")

        right_layout.addWidget(self.add_shape_button)
        right_layout.addWidget(self.import_button)
        right_layout.addWidget(self.export_button)
        right_layout.addWidget(self.rotate_button)
        right_layout.addWidget(self.reset_button)
        right_layout.addWidget(self.render_button)

        # 设置右侧功能区
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, 2)

        # 设置主窗口的中央部件
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 信号与槽连接
        self.import_button.clicked.connect(self.import_object)
        self.export_button.clicked.connect(self.export_object)
        self.reset_button.clicked.connect(self.reset_view)
        self.render_button.clicked.connect(self.render_scene)
        self.add_shape_button.clicked.connect(self.add_shape)
        self.rotate_button.clicked.connect(self.toggle_rotation)

        # 初始化物体列表
        self.scene_objects = []
        self.update_object_list()
        self.preview.update_objects(self.scene_objects)

        self.is_rotating = False  # 旋转状态

    def update_object_list(self):
        """
        更新 GUI 列表并同步预览窗口
        """
        self.object_list.setRowCount(0)  # 清空列表
        for obj in self.scene_objects:
            row = self.object_list.rowCount()
            self.object_list.insertRow(row)
            self.object_list.setItem(row, 0, QTableWidgetItem(obj["name"]))
            obj_type = "texture" if "texture" in obj else "color"
            self.object_list.setItem(row, 1, QTableWidgetItem(obj_type))
            appearance =f"Texture: \"{obj['texture']}\"" if "texture" in obj else f"Color: {obj['color']}"
            self.object_list.setItem(row, 2, QTableWidgetItem(appearance))
        self.preview.update_objects(self.scene_objects)

    def toggle_rotation(self):
        """
        切换旋转状态，开始或停止旋转
        """
        if self.is_rotating:
            self.preview.stop_rotation()  # 停止旋转
            self.rotate_button.setText("Start Rotation")  # 更新按钮文本
        else:
            self.preview.start_rotation()  # 开始旋转
            self.rotate_button.setText("Stop Rotation")  # 更新按钮文本
        self.is_rotating = not self.is_rotating

    def add_object(self, obj):
        """
        添加物体到场景
        """
        self.scene_objects.append(obj)
        self.update_object_list()

    def import_object(self):
        """
        导入 .obj 文件
        """
        filename, _ = QFileDialog.getOpenFileName(self, "Import Object", "", "OBJ Files (*.obj)")
        if filename:
            logger.info(f"Importing object from {filename}")
            try:
                vertices, faces = ShapeGenerator.load_obj(filename)
                obj_name = f"Imported_{len(self.scene_objects)}"
                transform = glm.mat4(1.0)
                self.scene_objects.append({
                    "name": obj_name,
                    "vertices": vertices,
                    "transform": transform,
                    "color": (1.0, 1.0, 1.0)  # 默认白色
                })
                self.update_object_list()
                logger.info(f"Successfully imported object: {obj_name}")
            except Exception as e:
                logger.error(f"Failed to import object: {e}")

    def export_object(self):
        """
        导出当前场景到 .obj 文件
        """
        filename, _ = QFileDialog.getSaveFileName(self, "Export Object", "", "OBJ Files (*.obj)")
        if filename:
            logger.info(f"Exporting scene to {filename}")
            try:
                self.preview.export_scene_to_obj(filename)
                logger.info("Scene exported successfully")
            except Exception as e:
                logger.error(f"Failed to export scene: {e}")

    def reset_view(self):
        """
        重置预览窗口的视图
        """
        logger.info("Resetting view")
        self.preview.reset_view()

    def render_scene(self):
        """
        渲染当前场景
        """
        logger.info("Starting rendering process")
        self.preview.start_render()

    def add_shape(self):
        dialog = AddShapeDialog()
        if dialog.exec() == QDialog.Accepted:
            shape_name = dialog.shape_selector.currentText()
            size = dialog.size_input.value()
            color = dialog.color
            texture = dialog.texture

            # 使用 `add_shape_to_scene` 生成形状数据
            shape_data = add_shape_to_scene(shape_name, size, color, texture)

            # 将生成的形状添加到场景中
            self.scene_objects.append(shape_data)

            # 更新预览
            self.preview.update_objects(self.scene_objects)
            logger.info(f"Added shape: {shape_name} to scene")