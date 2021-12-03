from typing import TYPE_CHECKING

import numpy as np
from napari_plugin_engine import napari_hook_implementation

if TYPE_CHECKING:
    import napari

@napari_hook_implementation
def napari_experimental_provide_function():
    return [save_as_animated_gif]


def save_as_animated_gif(data: "napari.types.ImageData", filename : str, duration: float = 0.1):
    from ._writer import napari_write_image
    napari_write_image(filename, data, None, duration)

def load_animated_gif(filename : str) -> "napari.types.ImageData":
    import imageio
    import numpy
    im = imageio.get_reader(filename)

    return numpy.asarray([frame for frame in im])

from napari_tools_menu import register_action

@register_action(menu="File Import/Export > Open animated gif")
def load_animated_gif_menu(viewer):
    print(viewer)
    import os
    from qtpy.QtWidgets import QFileDialog
    filename, _ = QFileDialog.getOpenFileName(parent=viewer.window._qt_window, filter="*.gif")
    if os.path.isfile(filename):
        data = load_animated_gif(filename)
        viewer.add_image(data, name=filename.replace('\\', '/').split("/")[-1])


@register_action(menu="File Import/Export > Save animated gif")
def save_animated_gif_menu(viewer):
    from qtpy.QtWidgets import QFileDialog
    filename, _ = QFileDialog.getSaveFileName(parent=viewer.window._qt_window, filter="*.gif")

    if isinstance(filename, str) and len(filename) > 0:
        save_as_animated_gif(list(viewer.layers.selection)[0].data.astype(np.uint8), filename)