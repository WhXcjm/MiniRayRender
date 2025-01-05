# model/shape_generator.py
from utils.logger import logger
import numpy as np
import math
import glm

class ShapeGenerator:
    @staticmethod
    def generate_sphere(radius=1.0, segments=32, rings=32):
        logger.info(f"Generating sphere with radius={radius}, segments={segments}, rings={rings}")
        vertices = []
        faces = []
        normals = []
        texcoords = []

        for i in range(rings + 1):
            phi = math.pi * i / rings
            for j in range(segments + 1):
                theta = 2 * math.pi * j / segments
                x = radius * math.sin(phi) * math.cos(theta)
                y = radius * math.cos(phi)
                z = radius * math.sin(phi) * math.sin(theta)
                vertices.append((x, y, z))
                normals.append((x / radius, y / radius, z / radius))
                texcoords.append((j / segments, i / rings))

        for i in range(rings):
            for j in range(segments):
                p1 = i * (segments + 1) + j
                p2 = p1 + (segments + 1)
                faces.append((p1, p1 + 1, p2))
                faces.append((p2, p1 + 1, p2 + 1))

        indices = np.array(faces, dtype=np.uint32)
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        texcoords = np.array(texcoords, dtype=np.float32)

        return {
            "vertices": vertices,
            "normals": normals,
            "indices": indices,
            "texcoords": texcoords,
            "transform": glm.mat4(1.0)
        }

    @staticmethod
    def generate_cuboid(width=1.0, height=1.0, depth=1.0):
        logger.info(f"Generating cuboid with width={width}, height={height}, depth={depth}")
        w, h, d = width / 2, height / 2, depth / 2
        vertices = [
            # 后面
            (-w, -h, -d), (w, -h, -d), (w, h, -d), (-w, h, -d),
            # 前面
            (-w, -h, d), (w, -h, d), (w, h, d), (-w, h, d)
        ]
        
        # 立方体的面，每个面由两个三角形组成
        faces = [
            # 后面
            (0, 1, 2), (0, 2, 3),
            # 前面
            (4, 5, 6), (4, 6, 7),
            # 底面
            (0, 1, 5), (0, 5, 4),
            # 顶面
            (3, 2, 6), (3, 6, 7),
            # 左面
            (0, 4, 7), (0, 7, 3),
            # 右面
            (1, 5, 6), (1, 6, 2)
        ]

        # 计算法线（每个面都有一个法线）
        normals = [
            (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1),  # 后面
            (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1),  # 前面
            (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0),  # 左面
            (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0),  # 右面
            (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0),  # 底面
            (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0),  # 顶面
        ]

        # 纹理坐标
        texcoords = [
            (0, 0), (1, 0), (1, 1), (0, 1),  # 后面
            (0, 0), (1, 0), (1, 1), (0, 1),  # 前面
            (0, 0), (1, 0), (1, 1), (0, 1),  # 底面
            (0, 0), (1, 0), (1, 1), (0, 1),  # 顶面
            (0, 0), (1, 0), (1, 1), (0, 1),  # 左面
            (0, 0), (1, 0), (1, 1), (0, 1)   # 右面
        ]
        
        indices = np.array(faces, dtype=np.uint32)
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        texcoords = np.array(texcoords, dtype=np.float32)

        return {
            "vertices": vertices,
            "normals": normals,
            "indices": indices,
            "texcoords": texcoords,
            "transform": glm.mat4(1.0)
        }

    @staticmethod
    def generate_plane(size=1.0):
        logger.info(f"Generating plane with size={size}")
        s = size / 2
        vertices = [
            # 四个顶点
            (-s, 0, -s), (s, 0, -s), (s, 0, s), (-s, 0, s)
        ]
        
        # 面的构成
        faces = [
            (0, 1, 2), (0, 2, 3)
        ]
        
        # 法线
        normals = [(0, 1, 0)] * 4  # 所有点的法线都朝上

        # 纹理坐标
        texcoords = [
            (0, 0), (1, 0), (1, 1), (0, 1)
        ]
        
        indices = np.array(faces, dtype=np.uint32)
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        texcoords = np.array(texcoords, dtype=np.float32)

        return {
            "vertices": vertices,
            "normals": normals,
            "indices": indices,
            "texcoords": texcoords,
            "transform": glm.mat4(1.0)
        }

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
