# model/add_shape.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QDoubleSpinBox, QPushButton, QColorDialog, QFileDialog, QLineEdit
from utils.logger import logger
from model.shape_generator import ShapeGenerator
from model.objects import *
import sys

class AddShapeDialog(QDialog):
    shape_id_counter = 0  # 维护一个全局的id计数器
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Shape")

        # 设置布局
        layout = QVBoxLayout()

        # 选择形状
        self.shape_selector = QComboBox()
        self.shape_selector.addItems(["Sphere", "Cuboid", "Plane"])
        layout.addWidget(self.shape_selector)

        # 输入大小
        self.size_input = QDoubleSpinBox()
        self.size_input.setSingleStep(0.1)
        self.size_input.setRange(0.1, 10)
        self.size_input.setValue(1)
        layout.addWidget(self.size_input)

        # 创建并排的布局用于选择颜色和纹理
        button_layout = QHBoxLayout()

        # 选择颜色按钮
        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)
        button_layout.addWidget(self.color_button)

        # 选择纹理按钮
        self.texture_button = QPushButton("Select Texture")
        self.texture_button.clicked.connect(self.select_texture)
        button_layout.addWidget(self.texture_button)

        layout.addLayout(button_layout)

        # 显示选择信息（不可编辑的 QLineEdit）
        self.selection_text = QLineEdit("No color or texture selected")
        self.selection_text.setReadOnly(True)  # 设置为只读，无法编辑
        layout.addWidget(self.selection_text)

        # 添加按钮
        self.add_button = QPushButton("Add")
        layout.addWidget(self.add_button)
        self.add_button.setEnabled(False)

        self.setLayout(layout)
        self.add_button.clicked.connect(self.accept)

        # 初始化颜色和纹理
        self.color = None
        self.texture = None

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.add_button.setEnabled(True)
            self.texture = None		# 当选择颜色时，清除纹理信息
            self.color = color.getRgbF()[:3]
            self.selection_text.setText(f"Color selected: {color.name()}")

    def select_texture(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Texture", "", "Image Files (*.png *.jpg *.bmp *.jpeg *.tiff)")
        if file:
            self.add_button.setEnabled(True)
            self.color = None		# 当选择纹理时，清除颜色信息
            self.texture = file
            self.selection_text.setText(f"Texture selected: {file}")
            
    def get_next_shape_id(self):
        AddShapeDialog.shape_id_counter += 1
        return AddShapeDialog.shape_id_counter

def add_shape_to_scene(shape_name, size, color=None, texture=None, name=None):
    """
    根据选中的形状名称、大小、颜色和纹理生成对应的形状，并返回形状数据。
    """
    shape_id = AddShapeDialog().get_next_shape_id()  # 获取新的唯一id
    logger.info(f"Generating shape #{shape_id}: {shape_name} with size={size}, color={color}, texture={texture}")
    obj = ShapeGenerator.generate_shape(shape_name, size)
    obj.id = shape_id
    obj.name = name if name else f"{shape_name}_{shape_id}"

    # 根据选择的颜色或纹理修改数据
    if color:
        obj.color = color
    elif texture:
        obj.texture = texture

    return obj

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])

    dialog = AddShapeDialog()
    if dialog.exec() == QDialog.Accepted:
        shape_data = add_shape_to_scene(dialog.shape_selector.currentText(), dialog.size_input.value(), dialog.color, dialog.texture)
        logger.info(f"Shape data: {shape_data}")
    else:
        logger.info("User canceled the operation")
        sys.exit(0)