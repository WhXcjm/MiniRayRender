'''
Author: Wh_Xcjm
Date: 2025-01-04 14:40:01
LastEditor: Wh_Xcjm
LastEditTime: 2025-01-04 16:21:27
FilePath: \大作业\model\shape_generator.py
Description: 

Copyright (c) 2025 by WhXcjm, All Rights Reserved. 
Github: https://github.com/WhXcjm
'''
from utils.logger import logger  # 导入日志工具
import numpy as np
import math

class ShapeGenerator:
    @staticmethod
    def generate_sphere(radius=1.0, segments=16, rings=16):
        logger.info(f"Generating sphere with radius={radius}, segments={segments}, rings={rings}")
        vertices = []
        faces = []

        for i in range(rings + 1):
            phi = math.pi * i / rings  # 从北极到南极的角度
            for j in range(segments + 1):
                theta = 2 * math.pi * j / segments  # 水平方向的角度

                x = radius * math.sin(phi) * math.cos(theta)
                y = radius * math.cos(phi)
                z = radius * math.sin(phi) * math.sin(theta)
                vertices.append((x, y, z))

        for i in range(rings):
            for j in range(segments):
                # 计算索引
                p1 = i * (segments + 1) + j
                p2 = p1 + (segments + 1)

                # 每个格子由两个三角形组成
                faces.append((p1, p2, p1 + 1))
                faces.append((p2, p2 + 1, p1 + 1))

        logger.info(f"Sphere generated: {len(vertices)} vertices, {len(faces)} faces")
        return np.array(vertices, dtype=np.float32), faces

    @staticmethod
    def generate_cuboid(width=1.0, height=1.0, depth=1.0):
        logger.info(f"Generating cuboid with width={width}, height={height}, depth={depth}")
        w, h, d = width / 2, height / 2, depth / 2
        vertices = [
            (-w, -h, -d), (w, -h, -d), (w, h, -d), (-w, h, -d),  # 后面
            (-w, -h, d), (w, -h, d), (w, h, d), (-w, h, d)       # 前面
        ]

        faces = [
            (0, 1, 2), (0, 2, 3),  # 后面
            (4, 5, 6), (4, 6, 7),  # 前面
            (0, 1, 5), (0, 5, 4),  # 底面
            (3, 2, 6), (3, 6, 7),  # 顶面
            (0, 4, 7), (0, 7, 3),  # 左面
            (1, 5, 6), (1, 6, 2),  # 右面
        ]

        logger.info(f"Cuboid generated: {len(vertices)} vertices, {len(faces)} faces")
        return vertices, faces

    @staticmethod
    def generate_plane(size=1.0):
        logger.info(f"Generating plane with size={size}")
        s = size / 2
        vertices = [
            (-s, 0, -s), (s, 0, -s), (s, 0, s), (-s, 0, s)
        ]
        faces = [
            (0, 1, 2), (0, 2, 3)
        ]
        logger.info(f"Plane generated: {len(vertices)} vertices, {len(faces)} faces")
        return vertices, faces

    @staticmethod
    def generate_shape(shape_name, size):
        """
        通用几何体生成接口，根据名称调用对应方法
        """
        logger.info(f"Generating shape: {shape_name} with size={size}")
        if shape_name == "Sphere":
            return ShapeGenerator.generate_sphere(radius=size)
        elif shape_name == "Cuboid":
            return ShapeGenerator.generate_cuboid(width=size, height=size, depth=size)
        elif shape_name == "Plane":
            return ShapeGenerator.generate_plane(size=size)
        else:
            logger.error(f"Unknown shape: {shape_name}")
            raise ValueError(f"Unknown shape: {shape_name}")
