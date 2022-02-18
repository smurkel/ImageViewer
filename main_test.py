import ImageViewer
from Util import *


if __name__ == "__main__":
    ImageViewer.create_test_window((1280, 800))
    view = ImageViewer.ImageViewer()
    view.set_clear_color((1.0, 1.0, 0.2, 1.0))
    channel_a = view.add_channel()
    channel_a.set_image(Load("C:/Users/mgflast/Desktop/stitch test/xidx_0_yidx_0.tif"))
    channel_a.color = (1.0, 0.0, 0.0, 1.0)
    channel_b = view.add_channel()
    channel_b.set_image(Load("C:/Users/mgflast/Desktop/stitch test/xidx_0_yidx_1.tif"))
    channel_b.color = (0.0, 1.0, 0.0, 1.0)
    view.set_viewport((0, 0, 1280, 800))
    while True:
        view.new_frame()
        view.render()
        view.end_frame()