import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
# ImageViewer class needs.....
# an FBO.
from OpenGLClasses import *
from itertools import count

test_window = None
test_window_size = (1280, 800)

def create_test_window(window_size, window_title = "ImageViewer window", fullscreen = False):
    global test_window, test_window_size
    window_size = window_size
    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    if fullscreen:
        test_window = glfw.create_window(window_size[0], window_size[1], window_title, glfw.get_primary_monitor(), None)
    else:
        test_window = glfw.create_window(window_size[0], window_size[1], window_title, None, None)
    glfw.make_context_current(test_window)
    if not test_window:
        glfw.terminate()
        print("Could not initialize window")
        exit(1)

class ImageViewer:
    """
    Constructor:
    string format = "ru16" or "rgba32f"

    """
    def __init__(self, format = "ru16", max_width = 2048, max_height = 2048):
        self.format = format
        self.max_width = max_width
        self.max_height = max_height
        self.channel_shader = Shader("channelshader"+format+".glsl")
        self.screen_shader = Shader("screenshader.glsl")
        self.channels = list()
        self.fbo_a = FrameBuffer(self.max_width, self.max_height)
        self.fbo_b = FrameBuffer(self.max_width, self.max_height)
        self.fbo_pingpong = 0
        self.clear_color = (0.0, 0.0, 0.0, 1.0)
        self.viewport = (0, max_width, 0, max_height)

        _vertices = [-1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0, 1.0]
        _indices = [0, 1, 2, 2, 0, 3]
        _vertexbuffer = VertexBuffer(_vertices)
        _indexbuffer = IndexBuffer(_indices)
        self.vertex_array = VertexArray(_vertexbuffer, _indexbuffer)
        self.camera = Camera(self.viewport)

    def set_channel_color(self, channel_idx, color):
        self.channels[channel_idx].color = color

    def set_channel_image(self, channel_idx, image):
        self.channels[channel_idx].texture.update(image)

    def add_channel(self):
        new_channel = ImageChannel(self.format)
        self.channels.append(new_channel)
        return new_channel

    def remove_channel(self, channel):
        if isinstance(channel, ImageChannel):
            self.channels.remove(channel)
        elif isinstance(channel, int):
            if channel in range(0, len(self.channels)):
                self.channels.pop(channel)

    def set_clear_color(self, clear_color):
        """clear_color: a tuple of rgba values, e.g, (1.0, 1.0, 1.0, 1.0) for white. Default is opaque black."""
        self.clear_color = clear_color

    def set_viewport(self, viewport):
        """viewport: a tuple of integers (left, top, right, bottom). Default is (0, 0, max_width = 2048, max_height = 2048)"""
        self.viewport = viewport

    def new_frame(self):
        glClearColor(*self.clear_color)
        glClear(GL_COLOR_BUFFER_BIT)
        glfw.poll_events()
        self.fbo_a.clear(self.clear_color)
        self.fbo_b.clear(self.clear_color)
        self.fbo_pingpong = 0

    def render(self):
        def render_channel(channel):
            render_fbo = self.fbo_a
            sample_fbo = self.fbo_b
            if self.fbo_pingpong == 1:
                render_fbo = self.fbo_b
                sample_fbo = self.fbo_a
                self.fbo_pingpong = 0
            else:
                self.fbo_pingpong = 1

            render_fbo.bind()
            self.vertex_array.bind()
            self.channel_shader.bind()
            self.channel_shader.uniform1f("constrast_min", float(channel.contrast_limits[0]))
            self.channel_shader.uniform1f("constrast_max", float(channel.contrast_limits[1]))
            self.channel_shader.uniform3f("channel_color", channel.color)
            channel.texture.bind(0)
            sample_fbo.texture.bind(1)
            glDrawElements(GL_TRIANGLES, self.vertex_array.indexBuffer.getCount(), GL_UNSIGNED_SHORT, None)
            self.channel_shader.unbind()
            self.vertex_array.unbind()
            render_fbo.unbind()
            glActiveTexture(GL_TEXTURE0)

        def render_screen():
            final_fbo = self.fbo_a
            if self.fbo_pingpong == 0:
                final_fbo = self.fbo_b

            self.vertex_array.bind()
            self.screen_shader.bind()
            view_matrix = self.camera.get_view_matrix()
            projection_matrix = self.camera.get_projection_matrix()
            self.screen_shader.uniformmat4("vp_mat", np.matmul(projection_matrix, view_matrix))
            final_fbo.texture.bind(0)
            glDrawElements(GL_TRIANGLES, self.vertex_array.indexBuffer.getCount(), GL_UNSIGNED_SHORT, None)
            self.screen_shader.unbind()
            self.vertex_array.unbind()
            glActiveTexture(GL_TEXTURE0)

        glViewport(0, 0, self.max_width, self.max_height)
        for channel in self.channels:
            render_channel(channel)

        glViewport(*self.viewport)
        render_screen()

    def end_frame(self):
        glfw.swap_buffers(test_window)

class ImageChannel:
    id_generator = count()
    def __init__(self, format):
        self.id = next(ImageChannel.id_generator)
        self.texture = Texture(format = format)
        self.color = (1.0, 1.0, 1.0)
        self.contrast_limits = [0.0, 256.0]

    def __eq__(self, other):
        if isinstance(other, ImageChannel):
            return self.id == other.id
        return False

    def set_image(self, pixeldata):
        self.texture.update(pixeldata)

class Camera:
    """An orthographic projection camera with adjustable zoom and position."""
    def __init__(self, clip_limits):
        self.position = [0.0, 0.0, 0.0]
        self.zoom = 100.0
        self.clip_limits = (*clip_limits, -1.0, 1.0)


    def get_view_matrix(self):
        return np.matrix([[self.zoom, 0.0, 0.0, self.zoom * self.position[0]],
                          [0.0, self.zoom, 0.0, self.zoom * self.position[1]],
                          [0.0, 0.0, 1.0, 0.0],
                          [0.0, 0.0, 0.0, 1.0]])

    def get_projection_matrix(self):
        dx = self.clip_limits[1] - self.clip_limits[0]
        dy = self.clip_limits[3] - self.clip_limits[2]
        dz = self.clip_limits[5] - self.clip_limits[4]
        rx = -(self.clip_limits[1] + self.clip_limits[0]) / dx
        ry = -(self.clip_limits[3] + self.clip_limits[2]) / dy
        rz = -(self.clip_limits[5] + self.clip_limits[4]) / dz
        return np.matrix([[2.0 / dx, 0, 0, rx],
                          [0, 2.0 / dy, 0, ry],
                          [0, 0, -2.0 / dz, rz],
                          [0, 0, 0, 1]])

