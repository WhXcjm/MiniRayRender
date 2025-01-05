'''
Author: Wh_Xcjm
Date: 2025-01-04 14:36:07
LastEditor: Wh_Xcjm
LastEditTime: 2025-01-05 22:25:51
FilePath: \大作业\gui\main_window.py
Description: 

Copyright (c) 2025 by WhXcjm, All Rights Reserved. 
Github: https://github.com/WhXcjm
'''
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QFileDialog, QHeaderView, QDialog
from PySide6.QtCore import Qt
from gui.preview_widget import PreviewWidget
from model.shape_generator import ShapeGenerator
from model.add_shape import AddShapeDialog, add_shape_to_scene
from model.transform_config import TransformConfigDialog
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

        # 物体列表
        self.object_list = QTableWidget()
        self.object_list.setColumnCount(3)
        self.object_list.setHorizontalHeaderLabels(["Name", "Appearance","More"])
        self.object_list.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        self.object_list.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        self.object_list.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.ResizeToContents)
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
            appearance = f"Texture: \"{obj['texture']}\"" if "texture" in obj else f"Color: {obj['color']}"
            item = QTableWidgetItem(appearance)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item.setToolTip(appearance)  # 鼠标悬停时显示完整内容
            self.object_list.setItem(row, 1, item)

            button = QPushButton("...")
            button.setMinimumWidth(5)
            button.setMaximumWidth(50)
            button.clicked.connect(lambda _, o=obj: self.show_transform_dialog(o))
            self.object_list.setCellWidget(row, 2, button)

        self.preview.update_objects(self.scene_objects)

    def show_transform_dialog(self, obj):
        """
        显示平移、旋转和缩放设置对话框，并根据修改更新 transform。
        """
        # 获取物体的当前平移、旋转和缩放值
        obj["translation"] = glm.vec3(0.0) if "translation" not in obj else obj["translation"]
        obj["rotation"] = glm.vec3(0.0) if "rotation" not in obj else obj["rotation"]
        obj["scale"] = glm.vec3(1.0, 1.0, 1.0) if "scale" not in obj else obj["scale"]

        # 创建并展示 TransformConfigDialog 对话框
        dialog = TransformConfigDialog(
            obj["name"],
            translation=obj["translation"],
            rotation=obj["rotation"],
            scale=obj["scale"]
        )

        if dialog.exec() == QDialog.Accepted:
            # 获取新的平移、旋转和缩放值
            new_translation = glm.vec3(dialog.translation_x.value(), dialog.translation_y.value(), dialog.translation_z.value())
            new_rotation = glm.vec3(dialog.rotation_x.value(), dialog.rotation_y.value(), dialog.rotation_z.value())
            new_scale = glm.vec3(dialog.scale_x.value(), dialog.scale_y.value(), dialog.scale_z.value())

            # 更新 obj 中的值
            obj["translation"] = new_translation
            obj["rotation"] = new_rotation
            obj["scale"] = new_scale

            # 使用新的平移、旋转和缩放值重新合成 transform
            obj["transform"] = glm.mat4(1.0)  # 重置为单位矩阵

            # 先缩放
            obj["transform"] = glm.scale(obj["transform"], new_scale)

            # 使用四元数进行旋转以避免万向锁问题
            rotation_quaternion = glm.quat()
            rotation_quaternion = glm.rotate(rotation_quaternion, glm.radians(new_rotation.x), glm.vec3(1.0, 0.0, 0.0))  # 绕 X 轴旋转
            rotation_quaternion = glm.rotate(rotation_quaternion, glm.radians(new_rotation.y), glm.vec3(0.0, 1.0, 0.0))  # 绕 Y 轴旋转
            rotation_quaternion = glm.rotate(rotation_quaternion, glm.radians(new_rotation.z), glm.vec3(0.0, 0.0, 1.0))  # 绕 Z 轴旋转

            # 将旋转四元数转换为矩阵
            obj["transform"] = obj["transform"] * glm.mat4_cast(rotation_quaternion)

            # 最后平移
            obj["transform"] = glm.translate(obj["transform"], new_translation)

            # 更新物体列表
            self.update_object_list()  # 更新列表与渲染
            
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
        self.rotate_button.setText("Stop Rotation")  # 更新按钮文本
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
            self.add_object(shape_data)

            name = shape_data["name"]
            logger.info(f"Added shape: {name} to scene")