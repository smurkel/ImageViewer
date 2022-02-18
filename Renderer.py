from OpenGLClasses import *
from OpenGL.GL import *
from OpenGL.GLU import *
import config as cfg

screenShader = None
vertexArray = None

def Init():
    global screenShader, vertexArray, ViewProjectionMatrix
    screenShader = Shader("C:/Users/mgflast/PycharmProjects/ImageViewer/shaders/ImageToScreenShader.glsl")
    vertices = [-1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0, 1.0]
    indices = [0, 1, 2, 2, 0, 3]
    vertexBuffer = VertexBuffer(vertices)
    indexBuffer = IndexBuffer(indices)
    vertexArray = VertexArray(vertexBuffer, indexBuffer)

def RenderImage(texture_id, shape, translation = [0.0, 0.0], color = [1.0, 1.0, 1.0, 1.0]):
    ModelMatrix = np.matrix([
        [1.0, 0.0, 0.0, (2.0 * translation[0]) / (cfg.translation_ndc_per_pixel * shape[0])],
        [0.0, 1.0, 0.0, -(2.0 * translation[1]) / (cfg.translation_ndc_per_pixel * shape[1])],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]])
    ViewProjectionMatrix = GetViewProjectionMatrix()
    vertexArray.bind()
    screenShader.bind()
    screenShader.uniform4f("color", color)
    screenShader.uniform1f("contrast_min", float(cfg.contrast_min))
    screenShader.uniform1f("contrast_max", float(cfg.contrast_max))
    screenShader.uniformmat4("vpMat", ViewProjectionMatrix)
    screenShader.uniformmat4("mMat", ModelMatrix)
    screenShader.uniform1i("flipud", int(cfg.flip_ud))
    screenShader.uniform1i("fliplr", int(cfg.flip_lr))
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glDrawElements(GL_TRIANGLES, vertexArray.indexBuffer.getCount(), GL_UNSIGNED_SHORT, None)
    screenShader.unbind()
    vertexArray.unbind()
    glActiveTexture(GL_TEXTURE0)



def GetViewProjectionMatrix():
    def viewMatrix():
        zoom = cfg.base_zoom * cfg.zoom
        vmat = np.matrix([[zoom, 0.0, 0.0, zoom * cfg.camera_position[0]],
                          [0.0, zoom, 0.0, zoom * cfg.camera_position[1]],
                          [0.0, 0.0,  1.0, 0.0],
                          [0.0, 0.0,  0.0, 1.0]])
        return vmat
    def orthographicProjectionMatrix(l, r, b, t, n, f):
        dx = r - l
        dy = t - b
        dz = f - n
        rx = -(r + l) / (r - l)
        ry = -(t + b) / (t - b)
        rz = -(f + n) / (f - n)
        return np.matrix([[2.0 / dx, 0, 0, rx],
                          [0, 2.0 / dy, 0, ry],
                          [0, 0, -2.0 / dz, rz],
                          [0, 0, 0, 1]])

    vmat = viewMatrix()
    pmat = orthographicProjectionMatrix(-cfg.width, cfg.width, -cfg.height, cfg.height, -100, 100)
    return np.matmul(pmat, vmat)