'''
Author: Wh_Xcjm
Date: 2025-01-05 14:20:45
LastEditor: Wh_Xcjm
LastEditTime: 2025-01-05 14:20:50
FilePath: \大作业\model\object.py
Description: 

Copyright (c) 2025 by WhXcjm, All Rights Reserved. 
Github: https://github.com/WhXcjm
'''
import numpy as np

class Hitable:
    def __init__(self, ambient, diffuse, specular, shininess, reflection, refraction):
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.reflection = reflection
        self.refraction = refraction

class Sphere(Hitable):
    def __init__(self, center, radius, ambient, diffuse, specular, shininess, reflection, refraction):
        super().__init__(ambient, diffuse, specular, shininess, reflection, refraction)
        self.center = center
        self.radius = radius

    def intersect(self, ray_origin, ray_direction):
        b = 2 * np.dot(ray_direction, ray_origin - self.center)
        c = np.linalg.norm(ray_origin - self.center) ** 2 - self.radius ** 2
        delta = b ** 2 - 4 * c
        if delta > 0:
            t1 = (-b + np.sqrt(delta)) / 2
            t2 = (-b - np.sqrt(delta)) / 2
            if t1 > 0 and t2 > 0:
                return min(t1, t2)
        return None

class Cuboid(Hitable):
    def __init__(self, min_point, max_point, ambient, diffuse, specular, shininess, reflection, refraction):
        super().__init__(ambient, diffuse, specular, shininess, reflection, refraction)
        self.min_point = min_point
        self.max_point = max_point

    def intersect(self, ray_origin, ray_direction):
        t_min = (self.min_point[0] - ray_origin[0]) / ray_direction[0]
        t_max = (self.max_point[0] - ray_origin[0]) / ray_direction[0]
        
        if t_min > t_max:
            t_min, t_max = t_max, t_min
        
        t_ymin = (self.min_point[1] - ray_origin[1]) / ray_direction[1]
        t_ymax = (self.max_point[1] - ray_origin[1]) / ray_direction[1]
        
        if t_ymin > t_ymax:
            t_ymin, t_ymax = t_ymax, t_ymin
        
        if t_min > t_ymax or t_ymin > t_max:
            return None
        
        if t_ymin > t_min:
            t_min = t_ymin
        if t_ymax < t_max:
            t_max = t_ymax
        
        t_zmin = (self.min_point[2] - ray_origin[2]) / ray_direction[2]
        t_zmax = (self.max_point[2] - ray_origin[2]) / ray_direction[2]
        
        if t_zmin > t_zmax:
            t_zmin, t_zmax = t_zmax, t_zmin
        
        if t_min > t_zmax or t_zmin > t_max:
            return None
        
        if t_zmin > t_min:
            t_min = t_zmin
        if t_zmax < t_max:
            t_max = t_zmax
        
        if t_min > 0:
            return t_min
        return None