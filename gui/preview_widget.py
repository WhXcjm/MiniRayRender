from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt, QTimer, QPoint
from OpenGL.GL import *
from OpenGL.GLU import *
import glm
import numpy as np
from OpenGL.GL import shaders
from utils.logger import logger


class PreviewWidget(QOpenGLWidget):
    """
    负责渲染场景的 OpenGL Widget
    """
    def __init__(self, parent=None, light_pos=glm.vec3(-1.0, 3.0, -2.0), eye=glm.vec3(0, 5, 10), center=glm.vec3(0, 0, 0), up=glm.vec3(0, 1, 0), fov=60.0, near=0.1, far=100.0):
        super().__init__(parent)
        self.shader_program = None
        self.object_list = []
        self.light_pos = light_pos  # 默认光源位置
        self.fixed_light_pos = light_pos  # 固定光源位置

        self.auto_eye = self.original_eye = self.last_eye = self.eye = eye
        self.original_center = self.last_center = self.center = center
        self.view = glm.lookAt(eye, center, up)  # 默认视图矩阵
        self.fov = fov
        self.proj_func = lambda width, height: glm.perspective(glm.radians(60.0), width/height, near, far)  # 投影矩阵函数

        self.is_rotating = False  # 默认不旋转
        self.auto_rotation_angle = 0.0  # 初始旋转角度
        self.auto_rotation_speed = 0.6  # 旋转速度

        # 设置定时器用于更新旋转
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.update_auto_rotation)

        self.is_dragging = False  # 鼠标拖拽状态
        self.last_mouse_pos = QPoint()  # 上一次鼠标位置
        self.rotation_speed = 0.3  # 旋转灵敏度
        self.translation_speed = 0.045  # 平移灵敏度
        self.scale_factor = 1.1  # 缩放灵敏度

    def initializeGL(self):
        """
        初始化 OpenGL 环境
        """
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)

        # 编译着色器
        self.shader_program = self.compile_shaders()

    def calculate_mvp(self, transform):
        """
        计算模型-视图-投影矩阵
        """
        proj = self.proj_func(self.width, self.height)
        view = self.view
        mvp = proj * view * transform
        return mvp

    def resizeGL(self, width, height):
        """
        调整视口大小
        """
        glViewport(0, 0, width, height)
        self.width = width
        self.height = height
        logger.info(f"Resized to {width}x{height}")

    def paintGL(self):
        """
        渲染场景
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader_program)

        # 设置光源位置和颜色
        light_pos_loc = glGetUniformLocation(self.shader_program, "lightPos")
        glUniform3f(light_pos_loc, *self.fixed_light_pos)
        
        # 设置光照强度
        glUniform1f(glGetUniformLocation(self.shader_program, "ambientStrength"), 0.35)
        glUniform1f(glGetUniformLocation(self.shader_program, "diffuseStrength"), 0.9)
        glUniform1f(glGetUniformLocation(self.shader_program, "specularStrength"), 0.25)

        light_color_loc = glGetUniformLocation(
            self.shader_program, "lightColor")
        glUniform3f(light_color_loc, 1.0, 1.0, 1.0)  # 默认白光

        # 设置观察者位置（eye）
        view_pos_loc = glGetUniformLocation(self.shader_program, "viewPos")
        glUniform3f(view_pos_loc, *self.eye)
        
        # 渲染物体列表
        texture_unit = 0  # 初始化纹理单元计数
        for obj in self.object_list:
            vertices = obj.vertices
            normals = obj.normals
            indices = obj.indices
            texcoords = obj.texcoords
            transform = obj.transform

            use_texture_loc = glGetUniformLocation(
                self.shader_program, "useTexture")
            # 设置纹理或颜色
            if obj.texture:
                img_data = obj.get_texture_data()

                # 绑定纹理
                glActiveTexture(GL_TEXTURE0 + texture_unit)
                texture = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, texture)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_data.shape[1], img_data.shape[0], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

                glUniform1i(use_texture_loc, 1)

                glGenerateMipmap(GL_TEXTURE_2D)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
                glTexParameteri(
                    GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
                glTexParameteri(
                    GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glBindTexture(GL_TEXTURE_2D, texture)
                tex_loc = glGetUniformLocation(self.shader_program, "texture1")
                glUniform1i(tex_loc, texture_unit)
                texture_unit += 1  # 分配下一个纹理单元
            else:
                glUniform1i(use_texture_loc, 0)
                color_loc = glGetUniformLocation(
                    self.shader_program, "objectColor")
                color = obj.color  # 默认白色
                glUniform3f(color_loc, *color)

            # 动态创建 VAO 和 VBO
            VAO = glGenVertexArrays(1)
            glBindVertexArray(VAO)

            # 创建 VBO 并上传顶点和纹理数据
            VBO = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, VBO)
            data = np.hstack((vertices, normals, texcoords)).astype(np.float32)
            glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

            # 配置顶点属性
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                                  8 * 4, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)

            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE,
                                  8 * 4, ctypes.c_void_p(12))
            glEnableVertexAttribArray(1)

            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE,
                                  8 * 4, ctypes.c_void_p(24))
            glEnableVertexAttribArray(2)

            # 创建 EBO 并上传索引数据
            EBO = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                         indices.nbytes, indices, GL_STATIC_DRAW)

            # 设置着色器中的 uniform
            mvp_loc = glGetUniformLocation(self.shader_program, "MVP")
            model_loc = glGetUniformLocation(self.shader_program, "model")

            mvp = self.calculate_mvp(transform)
            glUniformMatrix4fv(mvp_loc, 1, GL_FALSE, glm.value_ptr(mvp))
            glUniformMatrix4fv(model_loc, 1, GL_FALSE,
                               glm.value_ptr(transform))

            # 绘制
            glDrawElements(GL_TRIANGLES, 3 * len(indices), GL_UNSIGNED_INT, None)

            # 清理 VAO 和 VBO
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)
            glDeleteBuffers(1, [VBO, EBO])
            glDeleteVertexArrays(1, [VAO])

        glUseProgram(0)

    def update_objects(self, objects):
        """
        更新物体列表并重新渲染
        """
        self.object_list = objects
        self.update_view()  # 触发重新渲染

    def compile_shaders(self):
        """
        编译顶点和片段着色器
        """
        vertex_shader = """
        #version 430 core
        layout(location = 0) in vec3 position;
        layout(location = 1) in vec3 normal;
        layout(location = 2) in vec2 texcoord;

        uniform mat4 MVP;
        uniform mat4 model;

        out vec3 FragPos;     // 片段的世界坐标
        out vec3 Normal;      // 片段的法线
        out vec2 TexCoord;    // 片段的纹理坐标

        void main() {
            gl_Position = MVP * vec4(position, 1.0);
            FragPos = vec3(model * vec4(position, 1.0));
            Normal = mat3(transpose(inverse(model))) * normal; // 转换法线到世界坐标
            TexCoord = texcoord;  // 传递纹理坐标
        }

        """

        fragment_shader = """
        #version 430 core
        in vec3 FragPos;
        in vec3 Normal;
        in vec2 TexCoord;

        uniform vec3 lightPos;        // 光源位置
        uniform vec3 lightColor;      // 光源颜色
        uniform vec3 objectColor;     // 对象颜色
        uniform sampler2D texture1;   // 主纹理
        uniform bool useTexture;      // 是否使用纹理
        uniform vec3 viewPos;         // 观察者位置
        uniform float ambientStrength;  // 环境光强度
        uniform float diffuseStrength;  // 漫反射强度
        uniform float specularStrength; // 镜面反射强度

        out vec4 FragColor;

        void main() {
            // 环境光
            vec3 ambient = ambientStrength * lightColor;

            // 漫反射
            vec3 norm = normalize(Normal);
            vec3 lightDir = normalize(lightPos - FragPos);
            float diff = max(dot(norm, lightDir), 0.0);
            vec3 diffuse = diff * lightColor * diffuseStrength;

            // 镜面反射 (Blinn-Phong 模型)
            float shininess = 8.0;  // 可调节的高光度（越大，反射越小）
            
            // 计算视角方向（从片段指向观察者）
            vec3 viewDir = normalize(viewPos - FragPos); 

            // Blinn-Phong模型：halfDir 是视角方向和光照方向的中间方向
            vec3 halfDir = normalize(lightDir + viewDir);
            
            // 计算镜面反射分量
            float spec = pow(max(dot(norm, halfDir), 0.0), shininess);
            vec3 specular = specularStrength * spec * lightColor;

            // 最终光照结果
            vec3 lighting = ambient + diffuse + specular;

            // 选择纹理或颜色
            vec4 texColor = texture(texture1, TexCoord);
            vec3 finalColor = useTexture ? texColor.rgb : objectColor;

            FragColor = vec4(finalColor * lighting, 1.0);
        }
        """

        # 编译着色器
        vs = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
        fs = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
        program = shaders.compileProgram(vs, fs)

        return program

    def start_rotation(self):
        """
        启动旋转
        """
        self.is_rotating = True
        self.rotation_timer.start(10)  # 每10ms更新一次，约100帧每秒

    def stop_rotation(self):
        """
        停止旋转
        """
        self.is_rotating = False
        self.rotation_timer.stop()

    def reset_view(self):
        """
        重置视图
        """
        self.stop_rotation()
        self.auto_rotation_angle = 0.0
        self.fixed_light_pos = self.light_pos

        self.auto_eye = self.last_eye = self.eye = self.original_eye
        self.last_center = self.center = self.original_center
        self.view = glm.lookAt(self.eye, self.center, glm.vec3(0, 1, 0))

        self.update_view()

    def update_view(self):
        # 水平旋转视角
        horizontal_auto_rotation = glm.rotate(glm.mat4(1.0), glm.radians(self.auto_rotation_angle), glm.vec3(0.0, 1.0, 0.0))
        self.auto_eye = self.center + glm.vec3(horizontal_auto_rotation * glm.vec4(self.eye - self.center, 1.0))

        self.view = glm.lookAt(self.auto_eye, self.center, glm.vec3(0, 1, 0))
        self.update()  # 强制刷新重绘

    def update_auto_rotation(self):
        """
        更新旋转角度
        """
        if self.is_rotating:
            self.auto_rotation_angle += self.auto_rotation_speed
        if self.auto_rotation_angle >= 360.0:
            self.auto_rotation_angle -= 360.0 
        self.update_view()

    def mousePressEvent(self, event: QMouseEvent):
        """
        捕获鼠标按下事件。
        """
        logger.info(f"Mouse {'left' if event.button() == Qt.LeftButton else 'right'} button pressed at {event.pos()}")
        if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
            self.is_dragging = True
            self.last_mouse_pos = event.pos()
            self.last_eye = self.eye
            self.last_center = self.center

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        捕获鼠标移动事件，执行旋转或平移。
        """
        logger.debug(f"Mouse moved to {event.pos()}")
        if not self.is_dragging:
            return

        current_mouse_pos = event.pos()
        delta = current_mouse_pos - self.last_mouse_pos  # 鼠标移动增量

        if event.buttons() & Qt.LeftButton:  # 左键拖动，旋转
            self.rotate_view(delta)

        elif event.buttons() & Qt.RightButton:  # 右键拖动，平移
            self.translate_view(delta)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        捕获鼠标释放事件。
        """
        logger.info(f"Mouse {'left' if event.button() == Qt.LeftButton else 'right'} button released at {event.pos()}")
        if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
            self.is_dragging = False
        
    def wheelEvent(self, event):
        """
        捕获滚轮事件，调节 eye 和 center 之间的距离来实现缩放。
        """
        # 获取滚轮的增量，滚动向上为正，向下为负
        delta = event.angleDelta().y()

        # 获取 eye 和 center 之间的距离
        direction = self.eye - self.center
        distance = glm.length(direction)

        # 缩放因子：每次滚动增加/减少一定比例
        scale_factor = 1.1  # 比例因子

        if delta > 0:
            # 缩小：eye 离 center 更近
            new_distance = distance / scale_factor
        else:
            # 放大：eye 离 center 更远
            new_distance = distance * scale_factor

        # 更新 eye 的位置
        direction_normalized = glm.normalize(direction)
        self.eye = self.center + direction_normalized * new_distance

        self.update_view()

    def rotate_view(self, delta):
        angle_x = -delta.x() * self.rotation_speed * self.width / self.height
        angle_y = delta.y() * self.rotation_speed * self.width / self.height

        direction = self.last_eye - self.center

        # 计算水平旋转（绕 Y 轴）
        horizontal_rotation = glm.rotate(glm.mat4(1.0), glm.radians(angle_x), glm.vec3(0.0, 1.0, 0.0))
        direction = glm.vec3(horizontal_rotation * glm.vec4(direction, 1.0))  # 更新方向

        # 计算垂直旋转（绕 direction 与 up 的叉乘轴）
        right = glm.normalize(glm.cross(direction, glm.vec3(0.0, 1.0, 0.0)))  # 计算旋转轴
        vertical_rotation = glm.rotate(glm.mat4(1.0), glm.radians(angle_y), right)
        direction = glm.vec3(vertical_rotation * glm.vec4(direction, 1.0))  # 更新方向

        # 更新 eye 位置
        self.eye = self.center + direction

        self.update_view()

    def translate_view(self, delta):
        """
        根据鼠标增量执行视图平移，平移 eye 和 center 在它们连线的垂直平面内。
        """
        translate_x = delta.x() * self.translation_speed * self.width / self.height
        translate_y = delta.y() * self.translation_speed * self.width / self.height

        # 计算 eye 和 center 之间的方向向量
        direction = self.last_eye - self.last_center
        # 计算水平方向（左右平移的方向）与视差向量的垂直方向
        horizontal_auto_rotation = glm.rotate(glm.mat4(1.0), glm.radians(self.auto_rotation_angle), glm.vec3(0.0, 1.0, 0.0))
        auto_rotated_direction = glm.vec3(horizontal_auto_rotation * glm.vec4(direction, 1.0))
        right = glm.normalize(glm.cross(auto_rotated_direction, glm.vec3(0.0, 1.0, 0.0)))  # 右方向（视角平面内的垂直向量）
        # 计算上下方向（平移垂直方向）与视差向量的垂直方向
        up = glm.normalize(glm.cross(right, auto_rotated_direction))  # 上方向

        # 水平平移：沿右方向平移 eye 和 center
        horizontal_translation = right * translate_x
        self.eye = self.last_eye + horizontal_translation
        self.center = self.last_center + horizontal_translation

        # 垂直平移：沿上方向平移 eye 和 center
        vertical_translation = up * translate_y
        self.eye = self.eye + vertical_translation
        self.center = self.center +  vertical_translation

        self.update_view()

# __name__ = "__main__"
def generate_plane(size=5.0):
    vertices = np.array([
        [-size, 0, -size], [size, 0, -size],
        [-size, 0, size], [size, 0, size]
    ], dtype=np.float32)

    normals = np.array([
        [0, 1, 0], [0, 1, 0], [0, 1, 0],
        [0, 1, 0]
    ], dtype=np.float32)

    texcoords = np.array([
        [0, 0], [1, 0],
        [0, 1], [1, 1],
    ], dtype=np.float32)

    indices = np.array([0, 1, 2, 1, 2, 3], dtype=np.uint32)

    return {
        "vertices": vertices,
        "normals": normals,
        "indices": indices,
        "texcoords": texcoords,
        "texture": "assets/chessboard.jpg",
        "transform": glm.mat4(1.0)
    }


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QMainWindow
    import sys

    app = QApplication(sys.argv)
    window = QMainWindow()
    widget = PreviewWidget()
    plane = generate_plane()
    widget.update_objects([plane])
    window.setCentralWidget(widget)
    window.show()
    sys.exit(app.exec())
