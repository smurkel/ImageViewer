import glfw
window = None
mouse_pos = [0.0, 0.0]
mouse_delta = [0.0, 0.0]
scroll_delta = [0.0, 0.0]

def Init(glfwwindow):
    global window
    window = glfwwindow
    glfw.set_scroll_callback(window, scroll_callback)

def OnUpdate():
    global mouse_pos, mouse_delta, scroll_delta
    scroll_delta = [0.0, 0.0]
    glfw.poll_events()
    new_mouse_pos = glfw.get_cursor_pos(window)
    mouse_delta = [new_mouse_pos[0] - mouse_pos[0], new_mouse_pos[1] - mouse_pos[1]]
    mouse_pos = new_mouse_pos
def getMousePressed(button):
    state = glfw.get_mouse_button(window, button)
    if state == glfw.PRESS:
        return True
    return False

def getMouseMoved():
    return mouse_delta

def getMouseScrolled():
    return scroll_delta

def scroll_callback(window, deltax, deltay):
    global scroll_delta
    scroll_delta = [deltax, deltay]