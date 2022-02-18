import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer
import Input
import Renderer
import config as cfg
from OverviewMap import OverviewMap


def impl_glfw_init():
    width, height = cfg.width, cfg.height

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    if cfg.fullscreen:
        window = glfw.create_window(int(width), int(height), cfg.windowname, glfw.get_primary_monitor(), None)
    else:
        window = glfw.create_window(int(width), int(height), cfg.windowname, None, None)

    glfw.make_context_current(window)
    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window

def main():
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)
    last_frame_time = glfw.get_time()
    Renderer.Init()
    Input.Init(window)
    overviewmap = OverviewMap("C:/Users/mgflast/Desktop/stitch test/")
    overviewmap.overlap = 0.22
    overviewmap.register()

    while not glfw.window_should_close(window):
        new_time = glfw.get_time()
        dt = new_time - last_frame_time
        last_frame_time = new_time
        impl.process_inputs()
        Input.OnUpdate()
        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("Exit", True):
                exitConfirmed, _ = imgui.menu_item("Confirm exit")
                if exitConfirmed:
                    exit(1)
                imgui.end_menu()
            imgui.end_main_menu_bar()

        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        overviewmap.render()
        if not imgui.get_io().want_capture_mouse:
            if Input.getMousePressed(0):
                cursorDelta = Input.getMouseMoved()
                cfg.camera_position[0] += cursorDelta[0] * cfg.camera_pan_speed / cfg.base_zoom / cfg.zoom
                cfg.camera_position[1] -= cursorDelta[1] * cfg.camera_pan_speed / cfg.base_zoom / cfg.zoom
            scroll_delta = Input.getMouseScrolled()
            cfg.zoom += scroll_delta[1] * cfg.camera_zoom_speed
        imgui.begin("abc")
        _, cfg.zoom = imgui.slider_float("zoom", cfg.zoom, 0.1, 10.0)
        _, cfg.contrast_min = imgui.slider_float("min", cfg.contrast_min, 0.0, 65535.0)
        _, cfg.contrast_max = imgui.slider_float("max", cfg.contrast_max, 0.0, 65535.0)
        _, cfg.translation_ndc_per_pixel = imgui.slider_float("ndc to px", cfg.translation_ndc_per_pixel, -1.5, 0.8)
        if cfg.translation_ndc_per_pixel == 0.0:
            cfg.translation_ndc_per_pixel = 0.1
        imgui.end()
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    main()