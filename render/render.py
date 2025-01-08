'''
Author: Wh_Xcjm
Date: 2025-01-05 14:11:50
LastEditor: Wh_Xcjm
LastEditTime: 2025-01-08 16:22:08
FilePath: \大作业\render\render.py
Description: 

Copyright (c) 2025 by WhXcjm, All Rights Reserved. 
Github: https://github.com/WhXcjm
'''
from multiprocessing import Pool
import numpy as np
import matplotlib.pyplot as plt
import glm
import os
import math
from model.objects import *
from model.shape_generator import *
from utils.logger import *
from PIL import Image

def split_list(lst, num_blocks):
    """
    将列表 `lst` 分成 `num_blocks` 块，尽量保持每块大小接近
    """
    avg = len(lst) // num_blocks
    remainder = len(lst) % num_blocks
    result = []
    start = 0
    for i in range(num_blocks):
        end = start + avg + (1 if i < remainder else 0)
        result.append(lst[start:end])
        start = end
    return result

def render_block_worker(args):
        """
        渲染一个矩形块
        :param y_list: 块的y坐标列表
        :param x_list: 块的x坐标列表
        :param spl: 每方向像素采样数
        :return: 渲染块的结果（像素数据）
        """
        parent, y_list, x_list, sy, sx, spl = args
        logger.info(f"Rendering block: Y range {y_list[0][0]}-{y_list[-1][0]}, X range {x_list[0][0]}-{x_list[-1][0]}")
        block_image = np.zeros((len(y_list), len(x_list), 3))  # 单独的块图像数据
        for i, y in y_list:
            for j, x in x_list:
                # 超采样
                pixel_color = np.zeros(3)
                for dy in np.linspace(-0.5, 0.5, spl):
                    for dx in np.linspace(-0.5, 0.5, spl):
                        subpixel = glm.vec3(
                            x + dx / parent.width, y + dy / parent.height, 0)
                        ray_direction = VectorUtils.normalize(
                            subpixel - parent.camera)
                        pixel_color += parent.trace_ray(parent.camera,
                                                      ray_direction)

                block_image[i-sy, j-sx] = np.clip(pixel_color / (spl * spl), 0, 1)
            # logger.info(f"Finished rendering line {i} : X range {x_list[0][0]}-{x_list[-1][0]}")
        logger.info(f"Finished rendering block: Y range {y_list[0][0]}-{y_list[-1][0]}, X range {x_list[0][0]}-{x_list[-1][0]}")
        return sy, sx, block_image  # 返回渲染结果

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
        refracted_direction = ior * ray_direction + \
            (ior * cos_theta_i - cos_theta_t) * normal
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

        obj, min_distance, N = self.nearest_intersected_object(
            ray_origin, ray_direction)
        if obj is None:
            return np.zeros(3)  # 没有交点，返回黑色

        I = ray_origin + min_distance * ray_direction

        P = I + 1e-3 * N  # 防止光线陷入物体

        # 计算光线是否被遮挡（阴影判断）
        PL = VectorUtils.normalize(self.light['position'] - P)
        _, shadow_distance, _ = self.nearest_intersected_object(P, PL)
        is_shadowed = shadow_distance is not None and shadow_distance < np.linalg.norm(
            self.light['position'] - I)

        # 计算光照
        illumination = np.zeros(3)

        # 环境光
        illumination += obj.ambient * obj.color * self.light['ambient']

        if not is_shadowed:
            # 漫反射
            illumination += obj.diffuse * obj.color * \
                self.light['diffuse'] * max(np.dot(PL, N), 0)

            # 高光
            PC = VectorUtils.normalize(self.camera - P)
            H = VectorUtils.normalize(PL + PC)  # 半程向量
            illumination += obj.specular * obj.color * \
                self.light['specular'] * \
                (max(np.dot(N, H), 0) ** (obj.shininess))

        # 反射
        reflection_color = np.zeros(3)
        reflection_ray_direction = VectorUtils.reflected(ray_direction, N)
        reflection_color += obj.reflectivity * (obj.color + np.array([1, 1, 1])) / 2 * \
            self.trace_ray(P, reflection_ray_direction,
                   current_depth + 1, current_strength * obj.reflectivity)

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

    def render(self, spl=3, output='image.png', preview=True, callback=None):
        # 获取设备核心数，计算核心数量
        core_count = os.cpu_count()
        blocks_per_line = int(math.sqrt(4*core_count))  # 每行块数
        y_blocks = split_list([(i,y) for i,y in enumerate(np.linspace(
            self.screen[1], self.screen[3], self.height))], blocks_per_line)
        x_blocks = split_list(list(enumerate(np.linspace(
            self.screen[0], self.screen[2], self.width))), blocks_per_line)
        tasks = [
                (self, y_list, x_list, y_list[0][0], x_list[0][0], spl)
                for y_list in y_blocks for x_list in x_blocks
            ]
        # 使用多进程池渲染
        ltasks = len(tasks)
        count = 0
        with Pool(processes=core_count) as pool:
            for sy, sx, block_image in pool.imap_unordered(render_block_worker, tasks):
                # 合并结果到主图像
                for i in range(block_image.shape[0]):
                    for j in range(block_image.shape[1]):
                        self.image[sy + i, sx + j] = block_image[i, j]

                count += 1
                progress = (count / ltasks) * 100
                logger.info(f"Completed {count} out of {ltasks} blocks ({progress:.2f}%)")

                # 实时回调
                if callback:
                    callback(progress, None)

        # 保存最终渲染结果
        plt.imsave(output, self.image)
        image = Image.fromarray((self.image * 255).astype(np.uint8))
        if preview:
            image.show()


class Render:
    def __init__(self, width=1200, height=1200, max_depth=5, camera=glm.vec3(0, 10, 20), light_pos=glm.vec3(-1.0, 3.0, -2.0), light_color=glm.vec3(1.0, 1.0, 1.0), ):
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

    def run(self, objects, callback=None, spl=3, output='image.png'):
        # 渲染
        ray_tracer = RayTracer(self.width, self.height, self.max_depth,
                               self.camera, self.light, objects, self.screen)
        ray_tracer.render(spl=spl, output=output, callback=callback)


if __name__ == '__main__':
    # 场景物体
    objects = [
        ShapeGenerator.generate_sphere(radius=0.7, center=glm.vec3(-0.2, 0, -1), ambient=0.3, diffuse=0.7,
                                       specular=1, shininess=100, reflectivity=0.5, color=np.array([1, 0, 0])),
        ShapeGenerator.generate_sphere(radius=0.1, center=glm.vec3(0.1, -0.3, 0), ambient=0.3, diffuse=0.7,
                                       specular=1, shininess=100, reflectivity=0.5, color=np.array([1, 0, 1])),
        ShapeGenerator.generate_sphere(radius=0.15, center=glm.vec3(-0.3, 0, 0), ambient=0.3, diffuse=0.6,
                                       specular=1, shininess=100, reflectivity=0.5, color=np.array([0, 1, 0])),
        ShapeGenerator.generate_plane(size=90, center=glm.vec3(0, -0.7, 0), ambient=0.3, diffuse=0.6,
                                      specular=1, shininess=100, reflectivity=0.5, color=np.array([0.6, 0.6, 0.6])),
        ShapeGenerator.generate_cuboid(width=0.1, height=0.1, depth=0.1, center=glm.vec3(0.75, 0.75, -1.5), ambient=0.4, diffuse=0.6,
                                       specular=1, shininess=100, reflectivity=0.4, color=np.array([1, 1, 1]))
    ]
    Render(light_pos=glm.vec3(5,5,5), camera=glm.vec3(0,5,10), width=300, height=200).run(objects, spl=3, output='image.png')

# 定位噪点问题，经过调试发现与视角有关，大概率修正视角后可以得到解决（可能某些取整的问题）