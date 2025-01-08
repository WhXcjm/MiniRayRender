'''
Author: Wh_Xcjm
Date: 2025-01-04 14:30:47
LastEditor: Wh_Xcjm
LastEditTime: 2025-01-08 12:22:35
FilePath: \大作业\main.py
Description: 

Copyright (c) 2025 by WhXcjm, All Rights Reserved. 
Github: https://github.com/WhXcjm
'''
import sys, glm
import numpy as np
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.add_shape import *

def main():
    """
    程序入口，初始化应用程序并启动主窗口
    """
    # 创建应用程序实例
    app = QApplication(sys.argv)

    # 初始化主窗口
    camera = glm.vec3(0, 10, 20)
    main_window = MainWindow(
        eye = camera,
        center = glm.vec3(0, 0, 0),
        light_pos = glm.vec3(-2, 10, 5)
    )
    # 加地平面棋盘
    main_window.add_object(add_shape_to_scene("Plane", 8, texture="assets/chessboard.jpg"))
    # main_window.object_list.resizeColumnsToContents()
    main_window.show()

    # 进入主事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
