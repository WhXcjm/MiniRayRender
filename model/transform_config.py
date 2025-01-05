from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QDoubleSpinBox, QLabel, QDialogButtonBox, QSlider
from PySide6.QtCore import Qt
from utils.logger import logger

class TransformConfigDialog(QDialog):
	def __init__(self, name, translation, rotation, scale, parent=None):
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
		self.translation_x_slider.setRange(-50, 50)
		self.translation_x_slider.setValue(int(translation[0]))
		self.translation_x_slider.setSingleStep(1)
		self.translation_x_slider.setTickInterval(10)
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
		self.translation_y_slider.setRange(-50, 50)
		self.translation_y_slider.setValue(int(translation[1]))
		self.translation_y_slider.setSingleStep(1)
		self.translation_y_slider.setTickInterval(10)
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
		self.translation_z_slider.setRange(-50, 50)
		self.translation_z_slider.setValue(int(translation[2]))
		self.translation_z_slider.setSingleStep(1)
		self.translation_z_slider.setTickInterval(10)
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
		self.scale_x_slider.setRange(0.1, 5)
		self.scale_x_slider.setValue(int(scale[0]))
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
		self.scale_y_slider.setRange(0.1, 5)
		self.scale_y_slider.setValue(int(scale[1]))
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
		self.scale_z_slider.setRange(0.1, 5)
		self.scale_z_slider.setValue(int(scale[2]))
		scale_layout.addWidget(self.scale_z_slider)
		self.sync_scale_z_slider()

		# 同步信号
		self.scale_z.valueChanged.connect(self.sync_scale_z_slider)
		self.scale_z_slider.valueChanged.connect(self.sync_scale_z_spinbox)

		# 同步信号：每当值变化时，实时更新视图
		self.translation_x.valueChanged.connect(self.update_transform)
		self.translation_y.valueChanged.connect(self.update_transform)
		self.translation_z.valueChanged.connect(self.update_transform)
		self.translation_x_slider.valueChanged.connect(self.update_transform)
		self.translation_y_slider.valueChanged.connect(self.update_transform)
		self.translation_z_slider.valueChanged.connect(self.update_transform)
		self.rotation_x.valueChanged.connect(self.update_transform)
		self.rotation_y.valueChanged.connect(self.update_transform)
		self.rotation_z.valueChanged.connect(self.update_transform)
		self.rotation_x_slider.valueChanged.connect(self.update_transform)
		self.rotation_y_slider.valueChanged.connect(self.update_transform)
		self.rotation_z_slider.valueChanged.connect(self.update_transform)
		self.scale_x.valueChanged.connect(self.update_transform)
		self.scale_y.valueChanged.connect(self.update_transform)
		self.scale_z.valueChanged.connect(self.update_transform)
		self.scale_x_slider.valueChanged.connect(self.update_transform)
		self.scale_y_slider.valueChanged.connect(self.update_transform)
		self.scale_z_slider.valueChanged.connect(self.update_transform)

		# 将三个小布局添加到主布局中
		main_layout.addLayout(translation_layout)
		main_layout.addLayout(rotation_layout)
		main_layout.addLayout(scale_layout)

		# 确定与取消按钮
		global_layout.addLayout(main_layout)
		buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)
		global_layout.addWidget(buttons, alignment=Qt.AlignCenter)

		self.setLayout(global_layout)

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
		self.scale_x_slider.setValue(int(self.scale_x.value()))

	def sync_scale_x_spinbox(self):
		self.scale_x.setValue(self.scale_x_slider.value())

	def sync_scale_y_slider(self):
		self.scale_y_slider.setValue(int(self.scale_y.value()))

	def sync_scale_y_spinbox(self):
		self.scale_y.setValue(self.scale_y_slider.value())

	def sync_scale_z_slider(self):
		self.scale_z_slider.setValue(int(self.scale_z.value()))

	def sync_scale_z_spinbox(self):
		self.scale_z.setValue(self.scale_z_slider.value())

	def update_transform(self):
		# 待填充
		logger.info("Updating transform...")
		pass
