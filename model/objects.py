'''
Author: Wh_Xcjm
Date: 2025-01-05 14:20:45
LastEditor: Wh_Xcjm
LastEditTime: 2025-01-13 04:17:16
FilePath: \大作业\model\objects.py
Description: 

Copyright (c) 2025 by WhXcjm, All Rights Reserved. 
Github: https://github.com/WhXcjm
'''
from PIL import Image
import numpy as np
import glm, math
from utils.logger import logger


class Object():
    def __init__(self, id=None, name="Object", obj_type="Custom", vertices=[], normals=[], indices=[], texcoords=[],
                 translation=glm.vec3(0.0, 0.0, 0.0), rotation=glm.vec3(0.0, 0.0, 0.0), scale=glm.vec3(1.0, 1.0, 1.0),
                 color=glm.vec3(1.0, 1.0, 1.0), ambient=0.35, diffuse=0.9,
                 specular=0.25, shininess=8, reflectivity=0.2, texture=None):
        """
        Initialize an Object.

        Parameters:
        id (int): Identifier for the object.
        name (str): Name of the object.
        obj_type (str): Type of the object, can be "Sphere", "Cuboid", "Plane", or "Custom".
        vertices (list): List of vertices.
        normals (list): List of normals.
        indices (list): List of indices.
        texcoords (list): List of texture coordinates.
        translation (glm.vec3): Translation vector.
        rotation (glm.vec3): Rotation vector.
        scale (glm.vec3): Scale vector.
        color (glm.vec3): Color vector.
        ambient (float): Ambient intensity.
        diffuse (float): Diffuse intensity.
        specular (float): Specular intensity.
        reflectivity (float): Reflectivity.
        shininess (int): Shininess.
        texture (any): Texture.
        """
        # Attribute information
        self.id = id
        self.name = name
        self.obj_type = obj_type

        # Shape information
        self.vertices = vertices
        self.normals = normals
        self.indices = indices
        self.texcoords = texcoords

        # Transformation information
        self.translation = translation
        self.rotation = rotation
        self.scale = scale
        self.transform = glm.mat4(1.0)

        # Material information
        self.color = color
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.reflectivity = reflectivity
        self.shininess = shininess
        self.texture = texture
        self.texture_data = None

    def update_transform(self):
        """
        Update the transformation matrix based on translation, rotation, and scale.
        """
        self.transform = glm.mat4(1.0)  # Reset to identity matrix

        # Apply translation
        self.transform = glm.translate(self.transform, self.translation)

        # Apply rotation using quaternion to avoid gimbal lock
        rotation_quaternion = glm.quat()
        rotation_quaternion = glm.rotate(rotation_quaternion, glm.radians(self.rotation.x), glm.vec3(1.0, 0.0, 0.0))  # Rotate around X axis
        rotation_quaternion = glm.rotate(rotation_quaternion, glm.radians(self.rotation.y), glm.vec3(0.0, 1.0, 0.0))  # Rotate around Y axis
        rotation_quaternion = glm.rotate(rotation_quaternion, glm.radians(self.rotation.z), glm.vec3(0.0, 0.0, 1.0))  # Rotate around Z axis

        # Convert quaternion to matrix and apply
        self.transform = self.transform * glm.mat4_cast(rotation_quaternion)

        # Apply scale
        self.transform = glm.scale(self.transform, self.scale)

    def get_texture_data(self):
        if self.texture_data is None:
            self.texture_data = np.array(Image.open(self.texture).convert('RGB'))
        return self.texture_data

    def get_color_by_texcoord(self, texcoord):
        """
        Given a texture coordinate (texcoord), return the corresponding color from the texture.
        texcoord should be normalized in the range [0, 1].
        """
        if self.texture:
            texture_data = self.get_texture_data()
            # Convert the normalized texcoord to pixel coordinates
            width, height = texture_data.shape[1], texture_data.shape[0]
            x = int(texcoord[0] * (width - 1))
            y = int(texcoord[1] * (height - 1))
            color = texture_data[y, x]  # (R, G, B)
            return glm.vec3(color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
        else:
            return self.color  # Return pure color if no texture is applied


class Hitable(Object):
    def __init__(self, id=None, name="Hitable", obj_type="Custom", vertices=[], normals=[], indices=[], texcoords=[],
                 translation=glm.vec3(0.0, 0.0, 0.0), rotation=glm.vec3(0.0, 0.0, 0.0), scale=glm.vec3(1.0, 1.0, 1.0),
                 color=glm.vec3(1.0, 1.0, 1.0), ambient=0.35, diffuse=0.9,
                 specular=0.25, shininess=8, reflectivity=0.2, texture=None,center=glm.vec3(0.0, 0.0, 0.0)):
        super().__init__(id, name, obj_type, vertices, normals, indices, texcoords, translation, rotation, scale, color, ambient, diffuse, specular, shininess, reflectivity, texture)
        self.center = center
        self.transformed_center = center

    def hit(self, ray_origin, ray_direction):
        """
        Determine the closest intersection between the ray and the object.
        Returns the t value, the normal of the surface, and the color at the intersection.
        """
        # Ensure indices is a 1D numpy array
        self.indices = np.ravel(self.indices)
        min_t = float('inf')
        hit_normal = None
        hit_color = None

        # Update the transformation matrix
        self.update_transform()

        for i in range(0, len(self.indices), 3):
            v0 = glm.vec3(self.transform * glm.vec4(self.vertices[self.indices[i]], 1.0)) + self.center
            v1 = glm.vec3(self.transform * glm.vec4(self.vertices[self.indices[i+1]], 1.0)) + self.center
            v2 = glm.vec3(self.transform * glm.vec4(self.vertices[self.indices[i+2]], 1.0)) + self.center
            normal = glm.normalize(glm.vec3(self.transform * glm.vec4(self.normals[self.indices[i]], 0.0)) +
                                   glm.vec3(self.transform * glm.vec4(self.normals[self.indices[i+1]], 0.0)) +
                                   glm.vec3(self.transform * glm.vec4(self.normals[self.indices[i+2]], 0.0)))

            edge1 = v1 - v0
            edge2 = v2 - v0
            h = glm.cross(ray_direction, edge2)
            a = glm.dot(edge1, h)

            if -1e-6 < a < 1e-6:
                continue  # Parallel to the triangle
            f = 1.0 / a
            s = ray_origin - v0
            u = f * glm.dot(s, h)

            if u < 0.0 or u > 1.0:
                continue

            q = glm.cross(s, edge1)
            v = f * glm.dot(ray_direction, q)

            if v < 0.0 or u + v > 1.0:
                continue

            t = f * glm.dot(edge2, q)
            if t > 1e-6 and t < min_t:
                min_t = t
                hit_normal = normal

                # Calculate the texture coordinates for the intersection point
                # Get the texcoords from the triangle's vertices
                texcoord = u * self.texcoords[self.indices[i+1]] + v * self.texcoords[self.indices[i+2]] + (1 - u - v) * self.texcoords[self.indices[i]]

                # Get the color from the texture
                hit_color = self.get_color_by_texcoord(texcoord)

        if min_t == float('inf'):
            return None, None, None  # Not hit
        return min_t, hit_normal, hit_color

class Sphere(Hitable):
    # 注：球体的center固定为 (0, 0, 0)，平移通过translation实现
    def __init__(self, id=None, name="Sphere", obj_type="Sphere", vertices=[], normals=[], indices=[], texcoords=[],
                 translation=glm.vec3(0.0, 0.0, 0.0), rotation=glm.vec3(0.0, 0.0, 0.0), scale=glm.vec3(1.0, 1.0, 1.0),
                 color=glm.vec3(1.0, 1.0, 1.0), ambient=0.35, diffuse=0.9,
                 specular=0.25, shininess=8, reflectivity=0.2, texture=None, center=glm.vec3(0.0, 0.0, 0.0), size=1.0):
        super().__init__(id, name, obj_type, vertices, normals, indices, texcoords, translation, rotation, scale, color, ambient, diffuse, specular, shininess, reflectivity, texture, center)
        self.size = size

    def hit(self, ray_origin, ray_direction):
        # Sphere-ray intersection using the quadratic formula
        # Update the transformation matrix
        self.update_transform()
        ray_direction = glm.normalize(ray_direction)

        # 计算逆变换矩阵
        inverse_transform = glm.inverse(self.transform)
        inverse_transpose = glm.transpose(inverse_transform)

        # 将光线从世界坐标系转换到物体坐标系
        # 光线原点 (点) 需要乘以逆变换矩阵
        ray_origin_obj = glm.vec3(inverse_transform * glm.vec4(ray_origin, 1.0))
        # 光线方向 (向量) 需要乘以逆变换矩阵，不考虑平移
        ray_direction_obj = glm.normalize(glm.vec3(inverse_transform * glm.vec4(ray_direction, 0.0)))

        oc = ray_origin_obj - self.center
        a = glm.dot(ray_direction_obj, ray_direction_obj)
        b = 2.0 * glm.dot(oc, ray_direction_obj)
        c = glm.dot(oc, oc) - self.size * self.size
        discriminant = b * b - 4.0 * a * c

        if discriminant < 0:
            return None, None, None  # No intersection

        t0 = (-b - glm.sqrt(discriminant)) / (2.0 * a)
        t1 = (-b + glm.sqrt(discriminant)) / (2.0 * a)
        t_obj = min(t0, t1) if t0 > 1e-6 else t1
        if t_obj < 1e-6:
            return None, None, None

        # 交点在物体坐标系下
        hit_point_obj = ray_origin_obj + t_obj * ray_direction_obj
        normal_obj = glm.normalize(hit_point_obj - glm.vec3(0.0, 0.0, 0.0))  # 法线在物体坐标系下

        # 将交点转换回世界坐标系
        hit_point_world = glm.vec3(self.transform * glm.vec4(hit_point_obj, 1.0))

        # 将法线转换回世界坐标系
        normal_world = glm.normalize(glm.vec3(inverse_transpose * glm.vec4(normal_obj, 0.0)))

        t_world = glm.length(hit_point_world - ray_origin)

        if self.texture:
            # 计算球面坐标
            theta = math.atan2(normal_obj.z, normal_obj.x)  # 范围：[-pi, pi]
            phi = math.acos(normal_obj.y / self.size)     # 范围：[0, pi]

            # 将 theta 规范化到 [0, 2*pi]
            if theta < 0:
                theta += 2 * math.pi

            # 映射到纹理坐标 [0, 1]
            u = 1 - (theta / (2 * math.pi))
            v = phi / math.pi

            # 检查 u 和 v 是否在 [0, 1] 范围内
            if not (0.0 <= u <= 1.0) or not (0.0 <= v <= 1.0):
                raise ValueError(f"Texture coordinates out of range: u={u}, v={v}")

            # 从纹理中获取颜色
            hit_color = self.get_color_by_texcoord((u, v))
        else:
            hit_color = self.color

        return t_world, normal_world, glm.vec3(hit_color)

class Cuboid(Hitable):
    def __init__(self, id=None, name="Cuboid", obj_type="Cuboid", vertices=[], normals=[], indices=[], texcoords=[],
                 translation=glm.vec3(0.0, 0.0, 0.0), rotation=glm.vec3(0.0, 0.0, 0.0), scale=glm.vec3(1.0, 1.0, 1.0),
                 color=glm.vec3(1.0, 1.0, 1.0), ambient=0.35, diffuse=0.9,
                 specular=0.25, shininess=8, reflectivity=0.2, texture=None, center=glm.vec3(0.0, 0.0, 0.0), size=1.0):
        super().__init__(id, name, obj_type, vertices, normals, indices, texcoords, translation, rotation, scale, color, ambient, diffuse, specular, shininess, reflectivity, texture, center)
        self.size = size

class Plane(Hitable):
    def __init__(self, id=None, name="Plane", obj_type="Plane", vertices=[], normals=[], indices=[], texcoords=[],
                 translation=glm.vec3(0.0, 0.0, 0.0), rotation=glm.vec3(0.0, 0.0, 0.0), scale=glm.vec3(1.0, 1.0, 1.0),
                 color=glm.vec3(1.0, 1.0, 1.0), ambient=0.35, diffuse=0.9,
                 specular=0.25, shininess=8, reflectivity=0.2, texture=None, center=glm.vec3(0.0, 0.0, 0.0), size=1.0):
        super().__init__(id, name, obj_type, vertices, normals, indices, texcoords, translation, rotation, scale, color, ambient, diffuse, specular, shininess, reflectivity, texture, center)
        self.size = size

if __name__ == "__main__":
    obj = Sphere(size=1,translation = glm.vec3(2.0, 0.0, 0.0),scale=glm.vec3(1,1,1),texture="assets/earthmap.jpg")
    print(obj.hit(glm.vec3(0.0, 0.0, 0.0), glm.vec3(1.0, 0.5, 0.0)))