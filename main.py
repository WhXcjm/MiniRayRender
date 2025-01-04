'''
Author: Wh_Xcjm
Date: 2025-01-04 14:30:47
LastEditor: Wh_Xcjm
LastEditTime: 2025-01-04 16:06:07
FilePath: \大作业\main.py
Description: 

Copyright (c) 2025 by WhXcjm, All Rights Reserved. 
Github: https://github.com/WhXcjm
'''
import sys, glm
import numpy as np
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """
    程序入口，初始化应用程序并启动主窗口
    """
    # 创建应用程序实例
    app = QApplication(sys.argv)

    # 初始化主窗口
    main_window = MainWindow()
    # 加地平面棋盘
    size = 8
    vertices = np.array([
        [-size, 0, -size], [size, 0, -size],
        [-size, 0, size], [size, 0, size]
    ], dtype=np.float32)
    normals = np.array([
        [0, 1, 0], [0, 1, 0], [0, 1, 0],
        [0, 1, 0]
    ], dtype=np.float32)
    indices = np.array([0, 1, 2, 1, 2, 3], dtype=np.uint32)
    texcoords = np.array([
        [0, 0], [1, 0],
        [0, 1], [1, 1],
    ], dtype=np.float32)
    main_window.add_object({
        "name": "chessboard",
        "vertices": vertices,
        "normals": normals,
        "indices": indices,
        "texcoords": texcoords,
        "texture": "chessboard.jpg",
        # "color": [0.5, 0.5, 0.5],
        "transform": glm.mat4(1.0)
    })
    main_window.show()

    # 进入主事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
