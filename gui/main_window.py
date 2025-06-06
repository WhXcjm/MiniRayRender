'''
Author: Wh_Xcjm
Date: 2025-01-04 14:36:07
LastEditor: Wh_Xcjm
LastEditTime: 2025-01-12 16:20:57
FilePath: \大作业\gui\main_window.py
Description: 

Copyright (c) 2025 by WhXcjm, All Rights Reserved. 
Github: https://github.com/WhXcjm
'''
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QFileDialog, QHeaderView, QDialog, QLabel, QProgressBar, QSizePolicy
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtCore import Qt, QThread
from gui.preview_widget import PreviewWidget
from gui.add_shape import AddShapeDialog, add_shape_to_scene
from gui.transform import TransformConfigDialog
from model.shape_generator import ShapeGenerator
from render.render import RenderThread
from utils.logger import logger
import matplotlib.pyplot as plt
import glm, os
import numpy as np
from PIL import Image
from OpenGL.GL import *

class MainWindow(QMainWindow):
	"""
	主窗口，包含左侧预览窗格和右侧功能列表。
	"""
	def __init__(self, light_pos = glm.vec3(-1.0, 3.0, -2.0), eye=glm.vec3(0, 5, 10), center=glm.vec3(0, 0, 0), up=glm.vec3(0, 1, 0), fov=60, near=0.1, far=100.0):
		super().__init__()
		self.setWindowTitle("MiniRayRender")
		self.setWindowIcon(QIcon("assets/icon.png"))
		self.setGeometry(100, 100, 1200, 800)
		self.properties = {
			"eye": eye,
			"center": center,
			"up": up,
			"fov": fov,
			"near": near,
			"far": far
		}

		# 主布局
		main_layout = QHBoxLayout()

		# 左侧预览窗格
		self.preview = PreviewWidget(self, light_pos, eye, center, up, fov, near, far)
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

		# 进度条
		self.progress_bar = QProgressBar()
		self.progress_bar.setRange(0, 100)
		self.progress_bar.setValue(0)

		# 自定义进度条样式
		self.progress_bar.setTextVisible(True)
		self.progress_bar.setStyleSheet("""
			QProgressBar {
				border-width: 1px;
				border-style: solid;
				border-color: #E7E7E7 #E7E7E7 #C2C2C2 #E7E7E7;
				border-radius: 5px;
				background-color: #FBFBFB;
				margin: 0px 2px 0px 2px;
			}
			QProgressBar::chunk {
				background-color: #4caf50;
				border-radius: 5px;
			}
			QProgressBar::horizontal {
				text-align: center;
			}
		""")
		right_layout.addWidget(self.progress_bar)
		self.progress_bar.setVisible(False)

		# 设置右侧功能区
		right_widget = QWidget(self)
		right_widget.setLayout(right_layout)
		main_layout.addWidget(right_widget, 2)

		# 设置主窗口的中央部件
		main_widget = QWidget(self)
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
		self.object_list.cellChanged.connect(self.handle_name_change)

	def handle_name_change(self, row, column):
		"""
		处理名称修改时更新物体名称。
		"""
		if column == 0:  # 只处理第一列的修改
			item = self.object_list.item(row, 0)
			if item:
				new_name = item.text()
				# 找到对应物体并更新名称
				obj = self.scene_objects[row]
				obj.name = new_name
				self.update_object_list()  # 刷新列表显示新的名称

	def update_object_list(self):
		"""
		更新 GUI 列表并同步预览窗口
		"""
		self.object_list.blockSignals(True)  # 阻止信号触发
		for row in range(self.object_list.rowCount()):
			self.object_list.removeRow(row)
		self.object_list.setRowCount(0)
		
		# 删除无用物体，注意避免内存泄漏
		to_remove = []
		for obj in self.scene_objects:
			if getattr(obj, 'removed', False):
				to_remove.append(obj)
		for obj in to_remove:
			self.scene_objects.remove(obj)
			del obj
		
		for obj in self.scene_objects:
			row = self.object_list.rowCount()
			self.object_list.insertRow(row)
			self.object_list.setItem(row, 0, QTableWidgetItem(obj.name))
			appearance = f"Texture: \"{obj.texture}\"" if obj.texture else f"Color: {obj.color}"
			appearance_item = QTableWidgetItem(appearance)
			appearance_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
			appearance_item.setToolTip(appearance)  # 鼠标悬停时显示完整内容
			appearance_item.setFlags(appearance_item.flags() & ~Qt.ItemIsEditable)
			self.object_list.setItem(row, 1, appearance_item)
			
			button_widget = QWidget()
			button_layout = QHBoxLayout()
			button_layout.setSpacing(0)
			button_layout.setContentsMargins(0, 0, 0, 0)
			
			more_button = QPushButton("Trans")
			# more_button.setMinimumWidth(28)
			more_button.setMaximumWidth(50)
			more_button.clicked.connect(lambda _, o=obj: self.show_transform_dialog(o))
			button_layout.addWidget(more_button)

			del_button = QPushButton("Del")
			# del_button.setMinimumWidth(28)
			del_button.setMaximumWidth(50)
			del_button.clicked.connect(lambda _, o=obj: self.delete_object(o))
			button_layout.addWidget(del_button)
			
			more_button.setStyleSheet("padding-top: 5px; padding-bottom: 5px; margin-top: 0px; margin-bottom: 0px; padding-left: 5px; padding-right: 5px")
			del_button.setStyleSheet("padding-top: 5px; padding-bottom: 5px; margin-top: 0px; margin-bottom: 0px; padding-left: 5px; padding-right: 5px")

			button_widget = QWidget()
			button_widget.setLayout(button_layout)
			self.object_list.setCellWidget(row, 2, button_widget)

		self.object_list.blockSignals(False)  # 阻止信号触发
		self.preview.update_objects(self.scene_objects)

	def delete_object(self, obj):
		obj.removed = True
		self.update_object_list()
	
	def show_transform_dialog(self, obj):
		"""
		显示平移、旋转和缩放设置对话框，并根据修改更新 transform。
		"""
		# 创建并展示 TransformConfigDialog 对话框
		dialog = TransformConfigDialog(obj, callback=self.update_object_list, parent=self)

		dialog.show()
			
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
		self.render_button.setEnabled(False)
		self.progress_bar.setVisible(True)
		self.progress_bar.setValue(0)

		# 创建新的窗口来展示渲染效果
		class RenderWindow(QDialog):
			def __init__(self, width, height):
				super().__init__()
				self.aspect_ratio = width / height  # 保持宽高比
				self.setWindowTitle("Rendering...")
				self.setGeometry(100, 100, width, height)
				self.setMinimumWidth(200)  # 设置最小宽度，防止窗口过小
				self.setMinimumHeight(200)  # 设置最小高度，防止窗口过小

			def resizeEvent(self, event):
				""" 保持宽高比固定 """
				new_width = event.size().width()
				new_height = int(new_width / self.aspect_ratio)  # 根据宽高比计算新的高度

				# 调整窗口高度以保持宽高比
				self.resize(new_width, new_height)
				event.accept()  # 继续处理事件
		self.render_width = self.preview.width
		self.render_height = self.preview.height
		self.render_window = RenderWindow(self.render_width, self.render_height)
		self.render_window.setGeometry(100, 100, self.render_width, self.render_height)
		# 获取窗口所在的屏幕
		screen = self.screen()
		device_pixel_ratio = screen.devicePixelRatio() if screen else 1  # 获取缩放倍率
		self.render_width = int(self.render_width * device_pixel_ratio)
		self.render_height = int(self.render_height * device_pixel_ratio)
		self.render_window_layout = QVBoxLayout()

		# 创建一个 QLabel 来展示渲染图像
		self.render_image_label = QLabel()
		# 设置自动缩放
		self.render_image_label.setScaledContents(True)
		# 设置大小策略为扩展
		self.render_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.render_window_layout.addWidget(self.render_image_label)
		self.render_window.setLayout(self.render_window_layout)
		self.render_window.show()
		self.render_image = np.zeros((self.render_height, self.render_width, 3))
		# 在新线程中执行渲染过程
		self.start_rendering()

	def start_rendering(self):
		"""
		启动渲染并通过回调更新进度和图像显示
		"""

		self.progress_bar.setRange(0, 100)
		self.progress_bar.setValue(0)

		# 启动渲染的异步操作
		
		self.properties['eye'] = self.preview.auto_eye
		self.properties['center'] = self.preview.center
		self.render_thread = RenderThread(self.scene_objects, self.properties, self.render_width, height=self.render_height, light_pos=self.preview.light_pos)
		self.render_thread.ray_tracer.signals.progress_update.connect(self.on_progress_update)
		self.render_thread.ray_tracer.signals.finished.connect(self.on_render_finished)

		# 启动渲染线程
		self.render_thread.start()
	
	def on_progress_update(self, progress, image_data):
		"""
		更新进度条和渲染图像
		"""
		# 更新进度条
		self.progress_bar.setValue(progress)

		# 将颜色值从 0-1 区间转换到 0-255 区间
		image_data = (image_data.copy() * 255).astype(np.uint8)

		# 转换为 QImage 并显示在 QLabel 中
		height, width, _ = image_data.shape
		qimg = QImage(image_data.data, width, height, 3 * width, QImage.Format_RGB888)
		pixmap = QPixmap.fromImage(qimg)
		self.render_image_label.setPixmap(pixmap)
		self.render_image_label.repaint()

	def on_render_finished(self):
		"""
		渲染完成后的处理
		"""
		self.render_button.setEnabled(True)
		# self.progress_bar.setVisible(False)
		# 从 image.png 文件中读取图像并显示在 QLabel 中
		image_path = "image.png"
		image = QImage(image_path)
		if image.isNull():
			logger.error(f"Failed to load image from {image_path}")
		else:
			pixmap = QPixmap.fromImage(image)
			self.render_image_label.setPixmap(pixmap)
		self.render_window.setWindowTitle("Render Finished")

	def add_shape(self):
		self.add_shape_dialog = AddShapeDialog(self)
		self.add_shape_dialog.finished.connect(self.handle_add_shape_dialog_finished)
		self.add_shape_dialog.show()
		self.add_shape_button.setEnabled(False)
	
	def handle_add_shape_dialog_finished(self, result):
		"""
		处理 AddShapeDialog 的完成事件。
		"""
		if result == QDialog.Accepted:  # 用户点击 OK
			# 获取对话框中的数据
			shape_name = self.add_shape_dialog.shape_selector.currentText()
			size = self.add_shape_dialog.size_input.value()
			color = self.add_shape_dialog.color
			texture = self.add_shape_dialog.texture

			# 使用 `add_shape_to_scene` 生成形状数据
			obj = add_shape_to_scene(shape_name, size, color, texture)

			# 将生成的形状添加到场景中
			self.add_object(obj)

			name = obj.name
			logger.info(f"Added shape: {name} to scene")

		# 清理对话框引用（避免内存泄漏）
		self.add_shape_dialog = None
		self.add_shape_button.setEnabled(True)