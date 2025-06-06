# model/shape_generator.py
from utils.logger import logger
from model.objects import *
import numpy as np
import math
import glm

class ShapeGenerator:
    @staticmethod
    def generate_sphere(radius=1.0, segments=32, rings=32, id=None, name="Sphere", obj_type="Sphere", 
                 translation=glm.vec3(0.0, 0.0, 0.0), rotation=glm.vec3(0.0, 0.0, 0.0), scale=None, 
                 color=glm.vec3(1.0, 1.0, 1.0), ambient=0.35, diffuse=0.9, 
                 specular=0.25, shininess=8, reflectivity=0.2, texture=None, center=glm.vec3(0.0, 0.0, 0.0)):
        logger.info(f"Generating sphere with radius={radius}, segments={segments}, rings={rings}")
        # 临时性解决方案，将size(radius)直接作为缩放量，保证逆变换后球体会到单位球体。
        if scale is None:
            scale = glm.vec3(radius, radius, radius)
        radius = 1.0
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
                texcoords.append((1 - j / segments, i / rings))

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

        obj = Sphere(vertices=vertices, normals=normals, indices=indices, texcoords=texcoords, id=id, name=name, obj_type=obj_type, translation=translation, rotation=rotation, scale=scale, color=color, ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflectivity=reflectivity, texture=texture, center=center, size=radius)

        obj.update_transform()
        return obj

    @staticmethod
    def generate_cuboid(width=1.0, height=1.0, depth=1.0, id=None, name="Cuboid", obj_type="Cuboid",
                 translation=glm.vec3(0.0, 0.0, 0.0), rotation=glm.vec3(0.0, 0.0, 0.0), scale=glm.vec3(1.0, 1.0, 1.0), 
                 color=glm.vec3(1.0, 1.0, 1.0), ambient=0.35, diffuse=0.9, 
                 specular=0.25, shininess=8, reflectivity=0.2, texture=None, center=glm.vec3(0.0, 0.0, 0.0), size=1.0):
        logger.info(f"Generating cuboid with width={width}, height={height}, depth={depth}")
        
        # 计算每个顶点的半边长度
        w, h, d = width / 2, height / 2, depth / 2
        
        # 定义顶点（每个面4个顶点，共6个面）
        vertices = [
            # 后面
            (-w, -h, -d), (w, -h, -d), (w, h, -d), (-w, h, -d),
            # 前面
            (-w, -h, d), (w, -h, d), (w, h, d), (-w, h, d),
            # 底面
            (-w, -h, -d), (w, -h, -d), (w, -h, d), (-w, -h, d),
            # 顶面
            (-w, h, -d), (w, h, -d), (w, h, d), (-w, h, d),
            # 左面
            (-w, -h, -d), (-w, -h, d), (-w, h, d), (-w, h, -d),
            # 右面
            (w, -h, -d), (w, -h, d), (w, h, d), (w, h, -d)
        ]
        
        # 每个面对应的法线
        normals = [
            (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1),  # 后面
            (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1),  # 前面
            (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0),  # 底面
            (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0),  # 顶面
            (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0),  # 左面
            (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0)  # 右面
        ]
        
        # 纹理坐标
        texcoords = [
            (1, 1), (0, 1), (0, 0), (1, 0),  # 后面
            (0, 1), (1, 1), (1, 0), (0, 0),  # 前面
            (0, 1), (1, 1), (1, 0), (0, 0),  # 底面
            (0, 0), (1, 0), (1, 1), (0, 1),  # 顶面
            (0, 1), (1, 1), (1, 0), (0, 0),  # 左面
            (1, 1), (0, 1), (0, 0), (1, 0)  # 右面
        ]
        
        # 面的顶点索引（每个面由两个三角形组成）
        faces = [
            (0, 1, 2), (0, 2, 3),  # 后面
            (4, 5, 6), (4, 6, 7),  # 前面
            (8, 9, 10), (8, 10, 11),  # 底面
            (12, 13, 14), (12, 14, 15),  # 顶面
            (16, 17, 18), (16, 18, 19),  # 左面
            (20, 21, 22), (20, 22, 23)  # 右面
        ]

        indices = np.array(faces, dtype=np.uint32)
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        texcoords = np.array(texcoords, dtype=np.float32)

        return Cuboid(vertices=vertices, normals=normals, indices=indices, texcoords=texcoords, id=id, name=name, obj_type=obj_type, translation=translation, rotation=rotation, scale=scale, color=color, ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflectivity=reflectivity, texture=texture, center=center, size=size)


    @staticmethod
    def generate_plane(size=1.0, id=None, name="Plane", obj_type="Plane", 
                 translation=glm.vec3(0.0, 0.0, 0.0), rotation=glm.vec3(0.0, 0.0, 0.0), scale=glm.vec3(1.0, 1.0, 1.0), 
                 color=glm.vec3(1.0, 1.0, 1.0), ambient=0.35, diffuse=0.9, 
                 specular=0.25, shininess=8, reflectivity=0.2, texture=None, center=glm.vec3(0.0, 0.0, 0.0)):
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

        return Plane(vertices=vertices, normals=normals, indices=indices, texcoords=texcoords, id=id, name=name, obj_type=obj_type, translation=translation, rotation=rotation, scale=scale, color=color, ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflectivity=reflectivity, texture=texture, center=center, size=size)

    @staticmethod
    def generate_shape(shape_name, size, id, name):
        """
        通用几何体生成接口，根据名称调用对应方法
        """
        logger.info(f"Generating shape: {shape_name} with size={size}")
        if shape_name == "Sphere":
            return ShapeGenerator.generate_sphere(radius=size, id=id, name=name)
        elif shape_name == "Cuboid":
            return ShapeGenerator.generate_cuboid(width=size * 2, height=size * 2, depth=size * 2, id=id, name=name)
        elif shape_name == "Plane":
            return ShapeGenerator.generate_plane(size=size * 2, id=id, name=name)
        else:
            logger.error(f"Unknown shape: {shape_name}")
            raise ValueError(f"Unknown shape: {shape_name}")
