from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
import glm
import numpy as np
from OpenGL.GL import shaders
from PIL import Image


class PreviewWidget(QOpenGLWidget):
    """
    负责渲染场景的 OpenGL Widget
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shader_program = None
        self.object_list = []
        self.light_pos = glm.vec3(-1.0, 3.0, -2.0)  # 默认光源位置
        self.texture = None

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
        proj = glm.perspective(glm.radians(60.0), self.width / self.height, 0.1, 100.0)
        view = glm.lookAt(glm.vec3(0, 5, 10), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
        mvp = proj * view * transform
        return mvp
    
    def resizeGL(self, width, height):
        """
        调整视口大小
        """
        glViewport(0, 0, width, height)
        self.width = width
        self.height = height

    def paintGL(self):
        """
        渲染场景
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader_program)

        # 设置光源位置和颜色
        light_pos_loc = glGetUniformLocation(self.shader_program, "lightPos")
        glUniform3f(light_pos_loc, *self.light_pos)

        light_color_loc = glGetUniformLocation(self.shader_program, "lightColor")
        glUniform3f(light_color_loc, 1.0, 1.0, 1.0)  # 默认白光

        # 渲染物体列表
        texture_unit = 0  # 初始化纹理单元计数
        for obj in self.object_list:
            vertices = obj["vertices"]
            normals = obj["normals"]
            indices = obj["indices"]
            texcoords = obj["texcoords"]
            transform = obj["transform"]

            use_texture_loc = glGetUniformLocation(self.shader_program, "useTexture")
            # 设置纹理或颜色
            if "texture" in obj:
                img = Image.open(obj["texture"])
                img_data = np.array(img, dtype=np.uint8)

                self.texture = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, self.texture)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
                
                glUniform1i(use_texture_loc, 1)

                glGenerateMipmap(GL_TEXTURE_2D)
                glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
                glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

                # 绑定纹理
                glActiveTexture(GL_TEXTURE0 + texture_unit)
                glBindTexture(GL_TEXTURE_2D, self.texture)
                tex_loc = glGetUniformLocation(self.shader_program, "texture1")
                glUniform1i(tex_loc, texture_unit)
                texture_unit += 1  # 分配下一个纹理单元
            else:
                glUniform1i(use_texture_loc, 0)
                color_loc = glGetUniformLocation(self.shader_program, "objectColor")
                color = obj.get("color", (1.0, 1.0, 1.0))  # 默认白色
                glUniform3f(color_loc, *color)

            # 动态创建 VAO 和 VBO
            VAO = glGenVertexArrays(1)
            glBindVertexArray(VAO)

            # 创建 VBO 并上传顶点和纹理数据
            VBO = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, VBO)
            data = np.hstack((vertices, normals, texcoords)).astype(np.float32)
            glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

            # 创建 EBO 并上传索引数据
            EBO = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

            # 配置顶点属性
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)

            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(12))
            glEnableVertexAttribArray(1)

            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(24))
            glEnableVertexAttribArray(2)

            # 设置着色器中的 uniform
            mvp_loc = glGetUniformLocation(self.shader_program, "MVP")
            model_loc = glGetUniformLocation(self.shader_program, "model")

            mvp = self.calculate_mvp(transform)
            glUniformMatrix4fv(mvp_loc, 1, GL_FALSE, glm.value_ptr(mvp))
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(transform))

            # 绘制
            glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

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
        self.update()  # 触发重新渲染

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

        out vec4 FragColor;

        void main() {
            // 环境光
            float ambientStrength = 0.1;
            vec3 ambient = ambientStrength * lightColor;

            // 漫反射
            vec3 norm = normalize(Normal);
            vec3 lightDir = normalize(lightPos - FragPos);
            float diff = max(dot(norm, lightDir), 0.0);
            vec3 diffuse = diff * lightColor;

            // 镜面反射 (Blinn-Phong 模型)
            float specularStrength = 0.5;
            vec3 viewDir = normalize(-FragPos); // 假设观察者在 (0, 0, 0)
            vec3 halfDir = normalize(lightDir + viewDir);
            float spec = pow(max(dot(norm, halfDir), 0.0), 32);
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
        "texture": "chessboard.jpg",
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