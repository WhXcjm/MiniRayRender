'''
Author: Wh_Xcjm
Date: 2024-11-30 20:01:40
LastEditor: Wh_Xcjm
LastEditTime: 2025-01-06 12:52:56
FilePath: \大作业\gui\shader.py
Description: 

Copyright (c) 2024 by WhXcjm, All Rights Reserved. 
Github: https://github.com/WhXcjm
'''
import numpy as np
from PIL import Image  # pip install pillow
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sphere

from OpenGL.arrays import vbo
from OpenGL.GL import shaders

import glm  # pip install PyGLM


VERTEX_SHADER = """
#version 430
 
layout(location = 0) in vec4 position;
layout(location = 1) in vec2 texcoord;
layout(location = 2) in vec3 norm;

uniform mat4 MVP;
uniform mat4 M; //法线变换矩阵

out vec2 TexCoord;
out vec3 fragPos;

void main() {
    gl_Position = MVP * position;
    TexCoord = texcoord;
    fragPos = (M * position).xyz;
} 
"""

FRAGMENT_SHADER = """
#version 430

uniform mat4 M; //法线变换矩阵

in vec3 fragPos;
in vec2 TexCoord;
uniform vec3 lightPos;     // 光源位置
uniform vec3 lightColor;   // 光源颜色
uniform vec3 viewPos;      // 观察者位置
uniform sampler2D texture1;   // 主纹理

out vec4 FragColor;

void main() {
    // 获取纹理颜色
    vec3 kd = texture(texture1, TexCoord).rgb;  // 获取纹理的颜色

    // 计算法向量
    vec3 norm = normalize(fragPos);  // 因为球面上点的世界坐标与法向量同向，故归一化后即可使用

    // 计算环境光
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lightColor;

    // 计算漫反射光
    vec3 lightDir = normalize(lightPos - fragPos); // 光源方向
    float diff = max(dot(norm, lightDir), 0.0);    // 漫反射的强度
    vec3 diffuse = diff * lightColor;

    // 计算镜面反射光（Blinn-Phong模型）
    vec3 viewDir = normalize(viewPos - fragPos);  // 观察者方向
    vec3 halfDir = normalize(lightDir + viewDir); // 半程向量
    float spec = pow(max(dot(norm, halfDir), 0.0), 32.0); // 高光指数32.0
    vec3 specular = 1 * spec * lightColor;   // 镜面反射光

    // 计算最终的片段颜色（环境光 + 漫反射光 + 镜面反射光）
    vec3 color = ambient + diffuse  + specular;

    FragColor = vec4(color* kd, 1.0); // 输出颜色
}
"""

shaderProgram = None
VAO = None
Num_T = 0

time_count = 0


def initliaze():
    global VERTEXT_SHADER
    global FRAGMEN_SHADER
    global shaderProgram
    global VAO
    global Num_T

    vertexshader = shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
    fragmentshader = shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)

    shaderProgram = shaders.compileProgram(vertexshader, fragmentshader)

    points, texcoords, norms = sphere.sphere(
        longitudeStep=15, latitudeStep=15, radius=1)  # tetrahedron()
    Num_T = points.shape[0]
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, points.nbytes +
                 texcoords.nbytes+norms.nbytes, None, GL_STATIC_DRAW)
    glBufferSubData(GL_ARRAY_BUFFER, 0, points.nbytes, points)
    glBufferSubData(GL_ARRAY_BUFFER, points.nbytes,
                    texcoords.nbytes, texcoords)
    glBufferSubData(GL_ARRAY_BUFFER, points.nbytes +
                    texcoords.nbytes, norms.nbytes, norms)

    glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 16, None)
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8,
                          ctypes.c_void_p(points.nbytes))
    glEnableVertexAttribArray(1)

    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 12,
                          ctypes.c_void_p(points.nbytes+texcoords.nbytes))
    glEnableVertexAttribArray(2)

    tex = glGenTextures(1)
    img = np.array(Image.open('earthmap.jpg'))

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                 img.shape[1], img.shape[0], 0, GL_RGB, GL_UNSIGNED_BYTE, img)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


def calc_mvp(width, height):
    proj = glm.perspective(glm.radians(60.0), float(
        width)/float(height), 0.1, 20.0)
    view = glm.lookAt(glm.vec3(0.0, 0.0, 3.0),
                      glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))

    model = glm.mat4(1.0)
    model = glm.rotate(model, glm.radians(time_count * 5), glm.vec3(0, 1, 0))

    mvp = proj * view * model

    return model, mvp


def render():
    global shaderProgram
    global VAO
    global Num_T

    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    # glEnable(GL_CULL_FACE)

    glUseProgram(shaderProgram)

    mvp_loc = glGetUniformLocation(shaderProgram, "MVP")
    m_loc = glGetUniformLocation(shaderProgram, "M")
    m_mat, mvp_mat = calc_mvp(640, 480)
    glUniformMatrix4fv(mvp_loc, 1, GL_FALSE, glm.value_ptr(mvp_mat))
    glUniformMatrix4fv(m_loc, 1, GL_FALSE, glm.value_ptr(m_mat))

    lightPos = np.array([0.0, 0.0, 3.0], np.float32)  # 设置光源位置
    lightColor = np.array([2.0, 2.0, 2.0], np.float32)  # 设置光源亮度
    viewPos = np.array([0.0, 0.0, 3.0], np.float32)       # 观察者位置
    glUniform3f(glGetUniformLocation(shaderProgram, "lightPos"),
                lightPos[0], lightPos[1], lightPos[2])
    glUniform3f(glGetUniformLocation(shaderProgram, "lightColor"),
                lightColor[0], lightColor[1], lightColor[2])
    glUniform3f(glGetUniformLocation(shaderProgram, "viewPos"),
                viewPos[0], viewPos[1], viewPos[2])

    glActiveTexture(GL_TEXTURE0)
    glUniform1i(glGetUniformLocation(shaderProgram, "texture1"), 0)

    glBindVertexArray(VAO)
    glDrawArrays(GL_TRIANGLES, 0, Num_T)

    glUseProgram(0)

    glutSwapBuffers()


delay = 20
movement = 5


def animate(value):
    global time_count

    glutPostRedisplay()

    glutTimerFunc(delay, animate, 0)

    time_count = time_count+movement * delay / 1000


def main():

    glutInit([])
    glutSetOption(GLUT_MULTISAMPLE, 8)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize(640, 480)
    glutCreateWindow(b"test window")
    initliaze()
    glutDisplayFunc(render)

    glutTimerFunc(delay, animate, 0)
    glutMainLoop()


if __name__ == '__main__':
    main()
