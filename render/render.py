'''
Author: Wh_Xcjm
Date: 2025-01-05 14:11:50
LastEditor: Wh_Xcjm
LastEditTime: 2025-01-08 03:01:18
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
    def __init__(self, width, height, max_depth, camera, light, objects: list[Hitable], screen):
        self.width = width
        self.height = height
        self.max_depth = max_depth
        self.camera = camera
        self.light = light
        self.objects = objects
        self.screen = screen
        self.image = np.zeros((height, width, 3))

    def trace_ray(self, ray_origin, ray_direction, current_depth=0, current_strength=1.0):
        if current_depth >= self.max_depth:
            return np.zeros(3)  # 如果递归深度超出，返回黑色

        if current_strength < 0.1:
            return np.zeros(3)
        
        obj, min_distance, N = self.nearest_intersected_object(ray_origin, ray_direction)
        if obj is None:
            return np.zeros(3)  # 没有交点，返回黑色

        I = ray_origin + min_distance * ray_direction

        P = I + 1e-5 * N  # 防止光线陷入物体

        # 计算光线是否被遮挡（阴影判断）
        PL = VectorUtils.normalize(self.light['position'] - P)
        _, shadow_distance, _ = self.nearest_intersected_object(P, PL)
        is_shadowed = shadow_distance is not None and shadow_distance < np.linalg.norm(self.light['position'] - P)

        # 计算光照
        illumination = np.zeros(3)

        # 环境光
        illumination += obj.ambient * obj.color * self.light['ambient']
        
        if not is_shadowed:
            # 漫反射
            illumination += obj.diffuse * obj.color * self.light['diffuse'] * max(np.dot(PL, N), 0)
            
            # 高光
            PC = VectorUtils.normalize(self.camera - P)
            H = VectorUtils.normalize(PL + PC) # 半程向量
            illumination += obj.specular * obj.color * self.light['specular'] * (max(np.dot(N, H), 0) ** (obj.shininess))

        # 反射
        reflection_color = np.zeros(3)
        reflection_ray_direction = VectorUtils.reflected(ray_direction, N)
        reflection_color += obj.reflectivity * obj.color * self.trace_ray(P, reflection_ray_direction, current_depth + 1, current_strength * obj.reflectivity)

        # 综合结果（反射 + 光照）
        color = illumination + reflection_color
        return np.clip(color, 0, 1)  # 确保颜色值在合法范围内

    def nearest_intersected_object(self, ray_origin, ray_direction):
        nearest_object = None
        min_distance = np.inf
        normal_to_surface = None

        for obj in self.objects:
            dist, normal = obj.hit(ray_origin, ray_direction)
            if dist and dist < min_distance:
                min_distance = dist
                nearest_object = obj
                normal_to_surface = normal

        return nearest_object, min_distance, normal_to_surface

    def render(self, samples_per_pixel=4, output='image.png'):
        for i, y in enumerate(np.linspace(self.screen[1], self.screen[3], self.height)):
            for j, x in enumerate(np.linspace(self.screen[0], self.screen[2], self.width)):
                # 对每个像素发射多个光线进行超采样
                pixel_color = np.zeros(3)
                for dy in np.linspace(-0.5, 0.5, int(np.sqrt(samples_per_pixel))):
                    for dx in np.linspace(-0.5, 0.5, int(np.sqrt(samples_per_pixel))):
                        subpixel = glm.vec3(x + dx / self.width, y + dy / self.height, 0)
                        ray_direction = VectorUtils.normalize(subpixel - self.camera)
                        pixel_color += self.trace_ray(self.camera, ray_direction)

                self.image[i, j] = np.clip(pixel_color / samples_per_pixel, 0, 1)

            print(f"{i + 1}/{self.height}")

        plt.imsave(output, self.image)

class Render:
    def __init__(self, width=1200, height=1200, max_depth=5, camera=glm.vec3(0, 10, 20), light_pos=glm.vec3(-1.0, 3.0, -2.0), light_color=glm.vec3(1.0, 1.0, 1.0)):
        self.width = width
        self.height = height
        self.max_depth = max_depth
        self.camera = camera

        light = {
            'position': light_pos,
            'ambient': 1.0 * light_color,
            'diffuse': 1.0 * light_color,
            'specular': 1.0 * light_color
        }
        self.light = light

        self.image = np.zeros((height, width, 3))
        ratio = float(width) / height  # 宽高比
        screen = (-1, 1 / ratio, 1, -1 / ratio)  # left, top, right, bottom
        self.screen = screen

    def run(self, objects, samples_per_pixel=2, output='image.png'):
        # 渲染
        ray_tracer = RayTracer(self.width, self.height, self.max_depth, self.camera, self.light, objects, self.screen)
        ray_tracer.render(samples_per_pixel=samples_per_pixel, output=output)

if __name__ == '__main__':
    # 场景物体
    objects = [
        Sphere(center=glm.vec3(-0.2, 0, -1), size=0.7, ambient=0.3, diffuse=0.7, specular=1, shininess=100, reflectivity=0.5, color=np.array([1, 0, 0])),
        Sphere(center=glm.vec3(0.1, -0.3, 0), size=0.1, ambient=0.3, diffuse=0.7, specular=1, shininess=100, reflectivity=0.5, color=np.array([1, 0, 1])),
        Sphere(center=glm.vec3(-0.3, 0, 0), size=0.15, ambient=0.3, diffuse=0.6, specular=1, shininess=100, reflectivity=0.5, color=np.array([0, 1, 0])),
        Sphere(center=glm.vec3(0, -9000, 0), size=9000 - 0.7, ambient=0.3, diffuse=0.6, specular=1, shininess=100, reflectivity=0.5, color=np.array([0.6, 0.6, 0.6])),
        Cuboid(center=glm.vec3(0.75, 0.75, -1.5), size=0.05, ambient=0.4, diffuse=0.6, specular=1, shininess=100, reflectivity=0.4, color=np.array([1, 1, 1]))
    ]
    Render(width=1000,height=1000).run(objects, samples_per_pixel=4, output='image.png')