from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QDoubleSpinBox, QLabel, QDialogButtonBox, QSlider
from PySide6.QtCore import Qt
from utils.logger import logger
import glm

class TransformConfigDialog(QDialog):
	def __init__(self, obj, callback, parent=None):
		self.obj = obj
		name = obj["name"]
		translation = obj["translation"]
		rotation = obj["rotation"]
		scale = obj["scale"]

		# 创建备份及回调
		self.original_translation = glm.vec3(translation)
		self.original_rotation = glm.vec3(rotation)
		self.original_scale = glm.vec3(scale)
		self.callback = callback

		super().__init__(parent)
		self.setWindowTitle(f"Transform - {name}")

		# 操作和确认布局
		global_layout = QVBoxLayout()

		# 主布局：大布局，包含平移、旋转和缩放
		main_layout = QHBoxLayout()

		# 第一列：平移
		translation_layout = QVBoxLayout()

		# 第一行，平移 X
		translation_x_layout = QHBoxLayout()
		self.translation_x_label = QLabel("Translation X")
		self.translation_x = QDoubleSpinBox()
		self.translation_x.setRange(-1000, 1000)
		self.translation_x.setValue(translation[0])
		translation_x_layout.addWidget(self.translation_x_label)
		translation_x_layout.addWidget(self.translation_x)
		translation_layout.addLayout(translation_x_layout)

		# 第二行，平移 X 滑动条
		self.translation_x_slider = QSlider(Qt.Horizontal)
		self.translation_x_slider.setRange(-100, 100)
		self.translation_x_slider.setValue(int(translation[0]))
		self.translation_x_slider.setSingleStep(1)
		self.translation_x_slider.setTickInterval(20)
		self.translation_x_slider.setTickPosition(QSlider.TicksBelow)
		translation_layout.addWidget(self.translation_x_slider)
		self.sync_translation_x_slider()

		# 同步信号
		self.translation_x.valueChanged.connect(self.sync_translation_x_slider)
		self.translation_x_slider.valueChanged.connect(self.sync_translation_x_spinbox)

		# 重复上述步骤为 Y 和 Z
		translation_y_layout = QHBoxLayout()
		self.translation_y_label = QLabel("Translation Y")
		self.translation_y = QDoubleSpinBox()
		self.translation_y.setRange(-1000, 1000)
		self.translation_y.setValue(translation[1])
		translation_y_layout.addWidget(self.translation_y_label)
		translation_y_layout.addWidget(self.translation_y)
		translation_layout.addLayout(translation_y_layout)

		self.translation_y_slider = QSlider(Qt.Horizontal)
		self.translation_y_slider.setRange(-100, 100)
		self.translation_y_slider.setValue(int(translation[1]))
		self.translation_y_slider.setSingleStep(1)
		self.translation_y_slider.setTickInterval(20)
		self.translation_y_slider.setTickPosition(QSlider.TicksBelow)
		translation_layout.addWidget(self.translation_y_slider)
		self.sync_translation_y_slider()

		# 同步信号
		self.translation_y.valueChanged.connect(self.sync_translation_y_slider)
		self.translation_y_slider.valueChanged.connect(self.sync_translation_y_spinbox)

		translation_z_layout = QHBoxLayout()
		self.translation_z_label = QLabel("Translation Z")
		self.translation_z = QDoubleSpinBox()
		self.translation_z.setRange(-1000, 1000)
		self.translation_z.setValue(translation[2])
		translation_z_layout.addWidget(self.translation_z_label)
		translation_z_layout.addWidget(self.translation_z)
		translation_layout.addLayout(translation_z_layout)

		self.translation_z_slider = QSlider(Qt.Horizontal)
		self.translation_z_slider.setRange(-100, 100)
		self.translation_z_slider.setValue(int(translation[2]))
		self.translation_z_slider.setSingleStep(1)
		self.translation_z_slider.setTickInterval(20)
		self.translation_z_slider.setTickPosition(QSlider.TicksBelow)
		translation_layout.addWidget(self.translation_z_slider)
		self.sync_translation_z_slider()

		# 同步信号
		self.translation_z.valueChanged.connect(self.sync_translation_z_slider)
		self.translation_z_slider.valueChanged.connect(self.sync_translation_z_spinbox)

		# 第二列：旋转
		rotation_layout = QVBoxLayout()

		rotation_x_layout = QHBoxLayout()
		self.rotation_x_label = QLabel("Rotation X")
		self.rotation_x = QDoubleSpinBox()
		self.rotation_x.setRange(-360, 360)
		self.rotation_x.setValue(rotation[0])
		rotation_x_layout.addWidget(self.rotation_x_label)
		rotation_x_layout.addWidget(self.rotation_x)
		rotation_layout.addLayout(rotation_x_layout)

		self.rotation_x_slider = QSlider(Qt.Horizontal)
		self.rotation_x_slider.setRange(-180, 180)
		self.rotation_x_slider.setValue(int(rotation[0]))
		self.rotation_x_slider.setTickInterval(30)
		self.rotation_x_slider.setTickPosition(QSlider.TicksBelow)
		rotation_layout.addWidget(self.rotation_x_slider)
		self.sync_rotation_x_slider()

		# 同步信号
		self.rotation_x.valueChanged.connect(self.sync_rotation_x_slider)
		self.rotation_x_slider.valueChanged.connect(self.sync_rotation_x_spinbox)

		rotation_y_layout = QHBoxLayout()
		self.rotation_y_label = QLabel("Rotation Y")
		self.rotation_y = QDoubleSpinBox()
		self.rotation_y.setRange(-360, 360)
		self.rotation_y.setValue(rotation[1])
		rotation_y_layout.addWidget(self.rotation_y_label)
		rotation_y_layout.addWidget(self.rotation_y)
		rotation_layout.addLayout(rotation_y_layout)

		self.rotation_y_slider = QSlider(Qt.Horizontal)
		self.rotation_y_slider.setRange(-180, 180)
		self.rotation_y_slider.setValue(int(rotation[1]))
		self.rotation_y_slider.setTickInterval(30)
		self.rotation_y_slider.setTickPosition(QSlider.TicksBelow)
		rotation_layout.addWidget(self.rotation_y_slider)
		self.sync_rotation_y_slider()
		
		# 同步信号
		self.rotation_y.valueChanged.connect(self.sync_rotation_y_slider)
		self.rotation_y_slider.valueChanged.connect(self.sync_rotation_y_spinbox)

		rotation_z_layout = QHBoxLayout()
		self.rotation_z_label = QLabel("Rotation Z")
		self.rotation_z = QDoubleSpinBox()
		self.rotation_z.setRange(-360, 360)
		self.rotation_z.setValue(rotation[2])
		rotation_z_layout.addWidget(self.rotation_z_label)
		rotation_z_layout.addWidget(self.rotation_z)
		rotation_layout.addLayout(rotation_z_layout)

		self.rotation_z_slider = QSlider(Qt.Horizontal)
		self.rotation_z_slider.setRange(-180, 180)
		self.rotation_z_slider.setValue(int(rotation[2]))
		self.rotation_z_slider.setTickInterval(30)
		self.rotation_z_slider.setTickPosition(QSlider.TicksBelow)
		rotation_layout.addWidget(self.rotation_z_slider)
		self.sync_rotation_z_slider()

		# 同步信号
		self.rotation_z.valueChanged.connect(self.sync_rotation_z_slider)
		self.rotation_z_slider.valueChanged.connect(self.sync_rotation_z_spinbox)

		# 第三列：缩放
		scale_layout = QVBoxLayout()

		scale_x_layout = QHBoxLayout()
		self.scale_x_label = QLabel("Scale X")
		self.scale_x = QDoubleSpinBox()
		self.scale_x.setRange(0.1, 1000)
		self.scale_x.setValue(scale[0])
		scale_x_layout.addWidget(self.scale_x_label)
		scale_x_layout.addWidget(self.scale_x)
		scale_layout.addLayout(scale_x_layout)

		self.scale_x_slider = QSlider(Qt.Horizontal)
		self.scale_x_slider.setRange(1, 100)
		self.scale_x_slider.setValue(int(scale[0]))
		self.scale_x_slider.setTickInterval(10)
		self.scale_x_slider.setTickPosition(QSlider.TicksBelow)
		scale_layout.addWidget(self.scale_x_slider)
		self.sync_scale_x_slider()

		# 同步信号
		self.scale_x.valueChanged.connect(self.sync_scale_x_slider)
		self.scale_x_slider.valueChanged.connect(self.sync_scale_x_spinbox)

		scale_y_layout = QHBoxLayout()
		self.scale_y_label = QLabel("Scale Y")
		self.scale_y = QDoubleSpinBox()
		self.scale_y.setRange(0.1, 1000)
		self.scale_y.setValue(scale[1])
		scale_y_layout.addWidget(self.scale_y_label)
		scale_y_layout.addWidget(self.scale_y)
		scale_layout.addLayout(scale_y_layout)

		self.scale_y_slider = QSlider(Qt.Horizontal)
		self.scale_y_slider.setRange(1, 100)
		self.scale_y_slider.setValue(int(scale[1]))
		self.scale_y_slider.setTickInterval(10)
		self.scale_y_slider.setTickPosition(QSlider.TicksBelow)
		scale_layout.addWidget(self.scale_y_slider)
		self.sync_scale_y_slider()

		# 同步信号
		self.scale_y.valueChanged.connect(self.sync_scale_y_slider)
		self.scale_y_slider.valueChanged.connect(self.sync_scale_y_spinbox)

		scale_z_layout = QHBoxLayout()
		self.scale_z_label = QLabel("Scale Z")
		self.scale_z = QDoubleSpinBox()
		self.scale_z.setRange(0.1, 1000)
		self.scale_z.setValue(scale[2])
		scale_z_layout.addWidget(self.scale_z_label)
		scale_z_layout.addWidget(self.scale_z)
		scale_layout.addLayout(scale_z_layout)

		self.scale_z_slider = QSlider(Qt.Horizontal)
		self.scale_z_slider.setRange(1, 100)
		self.scale_z_slider.setValue(int(scale[2]))
		self.scale_z_slider.setTickInterval(10)
		self.scale_z_slider.setTickPosition(QSlider.TicksBelow)
		scale_layout.addWidget(self.scale_z_slider)
		self.sync_scale_z_slider()

		# 同步信号
		self.scale_z.valueChanged.connect(self.sync_scale_z_slider)
		self.scale_z_slider.valueChanged.connect(self.sync_scale_z_spinbox)

		# 同步信号：每当值变化时，实时更新视图
		self.translation_x.valueChanged.connect(self.update_view)
		self.translation_y.valueChanged.connect(self.update_view)
		self.translation_z.valueChanged.connect(self.update_view)
		self.translation_x_slider.valueChanged.connect(self.update_view)
		self.translation_y_slider.valueChanged.connect(self.update_view)
		self.translation_z_slider.valueChanged.connect(self.update_view)
		self.rotation_x.valueChanged.connect(self.update_view)
		self.rotation_y.valueChanged.connect(self.update_view)
		self.rotation_z.valueChanged.connect(self.update_view)
		self.rotation_x_slider.valueChanged.connect(self.update_view)
		self.rotation_y_slider.valueChanged.connect(self.update_view)
		self.rotation_z_slider.valueChanged.connect(self.update_view)
		self.scale_x.valueChanged.connect(self.update_view)
		self.scale_y.valueChanged.connect(self.update_view)
		self.scale_z.valueChanged.connect(self.update_view)
		self.scale_x_slider.valueChanged.connect(self.update_view)
		self.scale_y_slider.valueChanged.connect(self.update_view)
		self.scale_z_slider.valueChanged.connect(self.update_view)

		# 将三个小布局添加到主布局中
		main_layout.addLayout(translation_layout)
		main_layout.addLayout(rotation_layout)
		main_layout.addLayout(scale_layout)

		# 确定与取消按钮
		global_layout.addLayout(main_layout)
		buttons = QDialogButtonBox(self)  # 创建自定义按钮框
		buttons.addButton("Apply", QDialogButtonBox.AcceptRole)  # 添加 Apply 按钮
		buttons.addButton("Reset All", QDialogButtonBox.ResetRole)   # 添加 Reset 按钮
		buttons.addButton("Cancel", QDialogButtonBox.RejectRole)  # 添加 Cancel 按钮
		buttons.clicked.connect(self.handle_button_click)

		global_layout.addWidget(buttons, alignment=Qt.AlignCenter)
		self.setLayout(global_layout)
	
	def handle_button_click(self, button):
		"""
		处理按钮点击事件，根据不同按钮执行不同逻辑。
		"""
		role = self.sender().buttonRole(button)
		if role == QDialogButtonBox.AcceptRole:  # Apply 按钮
			self.update_view()
			self.accept()  # 关闭对话框
		elif role == QDialogButtonBox.ResetRole:  # Reset 按钮
			self.reset()  # 重置所有值
		elif role == QDialogButtonBox.RejectRole:  # Cancel 按钮
			self.cancel_changes()
			self.reject()  # 关闭对话框

	# 同步滑动条和输入框的值
	def sync_translation_x_slider(self):
		self.translation_x_slider.setValue(int(self.translation_x.value()*10))

	def sync_translation_x_spinbox(self):
		self.translation_x.setValue(self.translation_x_slider.value()/10)

	def sync_translation_y_slider(self):
		self.translation_y_slider.setValue(int(self.translation_y.value()*10))

	def sync_translation_y_spinbox(self):
		self.translation_y.setValue(self.translation_y_slider.value()/10)

	def sync_translation_z_slider(self):
		self.translation_z_slider.setValue(int(self.translation_z.value()*10))

	def sync_translation_z_spinbox(self):
		self.translation_z.setValue(self.translation_z_slider.value()/10)

	def sync_rotation_x_slider(self):
		self.rotation_x_slider.setValue(int(self.rotation_x.value()))

	def sync_rotation_x_spinbox(self):
		self.rotation_x.setValue(self.rotation_x_slider.value())

	def sync_rotation_y_slider(self):
		self.rotation_y_slider.setValue(int(self.rotation_y.value()))

	def sync_rotation_y_spinbox(self):
		self.rotation_y.setValue(self.rotation_y_slider.value())

	def sync_rotation_z_slider(self):
		self.rotation_z_slider.setValue(int(self.rotation_z.value()))

	def sync_rotation_z_spinbox(self):
		self.rotation_z.setValue(self.rotation_z_slider.value())

	def sync_scale_x_slider(self):
		self.scale_x_slider.setValue(int(self.scale_x.value()*10))

	def sync_scale_x_spinbox(self):
		self.scale_x.setValue(self.scale_x_slider.value()/10)

	def sync_scale_y_slider(self):
		self.scale_y_slider.setValue(int(self.scale_y.value()*10))

	def sync_scale_y_spinbox(self):
		self.scale_y.setValue(self.scale_y_slider.value()/10)

	def sync_scale_z_slider(self):
		self.scale_z_slider.setValue(int(self.scale_z.value()*10))

	def sync_scale_z_spinbox(self):
		self.scale_z.setValue(self.scale_z_slider.value()/10)

	def update_transform(self):
		# 获取新的平移、旋转和缩放值
		obj=self.obj

		new_translation = glm.vec3(self.translation_x.value(), self.translation_y.value(), self.translation_z.value())
		new_rotation = glm.vec3(self.rotation_x.value(), self.rotation_y.value(), self.rotation_z.value())
		new_scale = glm.vec3(self.scale_x.value(), self.scale_y.value(), self.scale_z.value())

		# 更新 obj 中的值
		obj["translation"] = new_translation
		obj["rotation"] = new_rotation
		obj["scale"] = new_scale

		# 使用新的平移、旋转和缩放值重新合成 transform
		obj["transform"] = glm.mat4(1.0)  # 重置为单位矩阵

		# 最后平移
		obj["transform"] = glm.translate(obj["transform"], new_translation)

		# 使用四元数进行旋转以避免万向锁问题
		rotation_quaternion = glm.quat()
		rotation_quaternion = glm.rotate(rotation_quaternion, glm.radians(new_rotation.x), glm.vec3(1.0, 0.0, 0.0))  # 绕 X 轴旋转
		rotation_quaternion = glm.rotate(rotation_quaternion, glm.radians(new_rotation.y), glm.vec3(0.0, 1.0, 0.0))  # 绕 Y 轴旋转
		rotation_quaternion = glm.rotate(rotation_quaternion, glm.radians(new_rotation.z), glm.vec3(0.0, 0.0, 1.0))  # 绕 Z 轴旋转

		# 将旋转四元数转换为矩阵
		obj["transform"] = obj["transform"] * glm.mat4_cast(rotation_quaternion)

		# 先缩放
		obj["transform"] = glm.scale(obj["transform"], new_scale)

	def reset(self):
		self.translation_x.setValue(0)
		self.translation_y.setValue(0)
		self.translation_z.setValue(0)
		self.rotation_x.setValue(0)
		self.rotation_y.setValue(0)
		self.rotation_z.setValue(0)
		self.scale_x.setValue(1)
		self.scale_y.setValue(1)
		self.scale_z.setValue(1)
		self.update_view()

	def cancel_changes(self):
		self.translation_x.setValue(self.original_translation[0])
		self.translation_y.setValue(self.original_translation[1])
		self.translation_z.setValue(self.original_translation[2])
		self.rotation_x.setValue(self.original_rotation[0])
		self.rotation_y.setValue(self.original_rotation[1])
		self.rotation_z.setValue(self.original_rotation[2])
		self.scale_x.setValue(self.original_scale[0])
		self.scale_y.setValue(self.original_scale[1])
		self.scale_z.setValue(self.original_scale[2])
		self.update_view()

	def update_view(self):
		self.update_transform()
		self.callback()
		pass
