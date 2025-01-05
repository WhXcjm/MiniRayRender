'''
Author: Wh_Xcjm
Date: 2025-01-05 14:11:50
LastEditor: Wh_Xcjm
LastEditTime: 2025-01-05 14:35:34
FilePath: \大作业\render\render.py
Description: 

Copyright (c) 2025 by WhXcjm, All Rights Reserved. 
Github: https://github.com/WhXcjm
'''
import numpy as np
import matplotlib.pyplot as plt
import glm
from model.objects import *

class VectorUtils:
    @staticmethod
    def normalize(vector):
        return vector / np.linalg.norm(vector)

    @staticmethod
    def reflected(ray_direction, normal):
        return ray_direction - 2 * np.dot(ray_direction, normal) * normal

    @staticmethod
    def refracted(ray_direction, normal, ior):
        cos_theta_i = -np.dot(ray_direction, normal)
        sin_theta_t2 = ior ** 2 * (1 - cos_theta_i ** 2)
        if sin_theta_t2 > 1:
            return VectorUtils.reflected(ray_direction, normal)
        cos_theta_t = np.sqrt(1 - sin_theta_t2)
        refracted_direction = ior * ray_direction + (ior * cos_theta_i - cos_theta_t) * normal
        return refracted_direction

class RayTracer:
    def __init__(self, width, height, max_depth, camera, light, objects, screen):
        self.width = width
        self.height = height
        self.max_depth = max_depth
        self.camera = camera
        self.light = light
        self.objects = objects
        self.screen = screen
        self.image = np.zeros((height, width, 3))

    def trace_ray(self, ray_origin, ray_direction, current_depth=0):
        if current_depth >= self.max_depth:
            return np.zeros(3)  # 如果递归深度超出，返回黑色

        nearest_object, min_distance = self.nearest_intersected_object(ray_origin, ray_direction)
        if nearest_object is None:
            return np.zeros(3)  # 没有交点，返回黑色

        intersection = ray_origin + min_distance * ray_direction
        normal_to_surface = VectorUtils.normalize(intersection - nearest_object.center if isinstance(nearest_object, Sphere) else intersection - (nearest_object.min_point + nearest_object.max_point) / 2)

        shifted_point = intersection + 1e-5 * normal_to_surface  # 防止光线陷入物体

        # 计算光线是否被遮挡（阴影判断）
        intersection_to_light = VectorUtils.normalize(self.light['position'] - shifted_point)
        _, shadow_distance = self.nearest_intersected_object(shifted_point, intersection_to_light)
        is_shadowed = shadow_distance < np.linalg.norm(self.light['position'] - shifted_point)

        # 计算光照
        illumination = np.zeros(3)
        if not is_shadowed:
            # 环境光
            illumination += nearest_object.ambient * self.light['ambient']
            # 漫反射
            illumination += nearest_object.diffuse * self.light['diffuse'] * max(np.dot(intersection_to_light, normal_to_surface), 0)
            # 高光
            intersection_to_camera = VectorUtils.normalize(self.camera - intersection)
            H = VectorUtils.normalize(intersection_to_light + intersection_to_camera)
            illumination += nearest_object.specular * self.light['specular'] * (max(np.dot(normal_to_surface, H), 0) ** (nearest_object.shininess / 4))

        # 反射
        reflection_color = np.zeros(3)
        reflection_ray_direction = VectorUtils.reflected(ray_direction, normal_to_surface)
        reflection_color += nearest_object.reflection * self.trace_ray(shifted_point, reflection_ray_direction, current_depth + 1)

        # 综合结果（反射 + 光照）
        color = illumination + reflection_color
        return np.clip(color, 0, 1)  # 确保颜色值在合法范围内

    def nearest_intersected_object(self, ray_origin, ray_direction):
        distances = []
        for obj in self.objects:
            dist = obj.intersect(ray_origin, ray_direction)
            distances.append(dist)

        nearest_object = None
        min_distance = np.inf
        for index, distance in enumerate(distances):
            if distance and distance < min_distance:
                min_distance = distance
                nearest_object = self.objects[index]

        return nearest_object, min_distance

    def render(self, samples_per_pixel=4, output='image.png'):
        for i, y in enumerate(np.linspace(self.screen[1], self.screen[3], self.height)):
            for j, x in enumerate(np.linspace(self.screen[0], self.screen[2], self.width)):
                # 对每个像素发射多个光线进行超采样
                pixel_color = np.zeros(3)
                for dy in np.linspace(-0.5, 0.5, int(np.sqrt(samples_per_pixel))):
                    for dx in np.linspace(-0.5, 0.5, int(np.sqrt(samples_per_pixel))):
                        subpixel = np.array([x + dx / self.width, y + dy / self.height, 0])
                        ray_direction = VectorUtils.normalize(subpixel - self.camera)
                        pixel_color += self.trace_ray(self.camera, ray_direction)

                self.image[i, j] = np.clip(pixel_color / samples_per_pixel, 0, 1)

            print(f"{i + 1}/{self.height}")

        plt.imsave(output, self.image)

class Render:
    def __init__(self, width=1200, height=1200, max_depth=4, camera=glm.vec3(0, 10, 20), light_pos=glm.vec3(-1.0, 3.0, -2.0), light_color=glm.vec3(1.0, 1.0, 1.0)):
        self.width = width
        self.height = height
        self.max_depth = max_depth
        self.camera = camera

        light = {
            'position': light_pos,
            'ambient': 0.1 * light_color,
            'diffuse': 1.0 * light_color,
            'specular': 0.5 * light_color
        }
        self.light = light

        self.image = np.zeros((height, width, 3))
        ratio = float(width) / height  # 宽高比
        screen = (-1, 1 / ratio, 1, -1 / ratio)  # left, top, right, bottom
        self.screen = screen

    def run(self, objects, samples_per_pixel=4, output='image.png'):
        # 渲染
        ray_tracer = RayTracer(self.width, self.height, self.max_depth, self.camera, self.light,  self.screen)
        ray_tracer.render(objects, samples_per_pixel=samples_per_pixel, output=output)

# 场景物体
objects = [
    Sphere(np.array([-0.2, 0, -1]), 0.7, np.array([0.1, 0, 0]), np.array([0.7, 0, 0]), np.array([1, 1, 1]), 100, 0.5, 1.5),
    Sphere(np.array([0.1, -0.3, 0]), 0.1, np.array([0.1, 0, 0.1]), np.array([0.7, 0, 0.7]), np.array([1, 1, 1]), 100, 0.5, 1.5),
    Sphere(np.array([-0.3, 0, 0]), 0.15, np.array([0, 0.1, 0]), np.array([0, 0.6, 0]), np.array([1, 1, 1]), 100, 0.5, 1.5),
    Sphere(np.array([0, -9000, 0]), 9000 - 0.7, np.array([0.1, 0.1, 0.1]), np.array([0.6, 0.6, 0.6]), np.array([1, 1, 1]), 100, 0.5, 1.5),
    Cuboid(np.array([0.5, 0.5, -2]), np.array([1, 1, -1]), np.array([0.2, 0.2, 0.2]), np.array([0.6, 0.6, 0.6]), np.array([1, 1, 1]), 100, 0.4, 1)
]

if __name__ == '__main__':
    Render().run(objects, samples_per_pixel=4, output='image.png')