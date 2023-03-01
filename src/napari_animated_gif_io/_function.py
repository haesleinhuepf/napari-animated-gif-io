import napari
import numpy as np
from napari_plugin_engine import napari_hook_implementation
from napari_tools_menu import register_action, register_function


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


@register_action(menu="File Import/Export > Open animated gif")
def load_animated_gif_menu(viewer):
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


@register_function(menu="File Import/Export > Save animated 3D view as gif")
def save_3d_view(
        tilt_axis : int = 1,
        angle_step : float = 2,
        min_max_angle : float = 20,
        frames_per_second: int = 15,
        canvas_only : bool = True,
        filename : "magicgui.types.PathLike" = "video.gif",
        viewer : napari.Viewer = None):
    filename = str(filename)
    if len(filename) > 0:
        from skimage.data import cells3d

        from microfilm.microanim import Microanim
        print('Started generating gif...')
        original_angles = np.asarray(viewer.camera.angles)

        images = []
        modified_angles = np.asarray([0, 0, 0])
        for angle in list(np.arange(-min_max_angle, min_max_angle, angle_step)) + list(
                np.arange(min_max_angle, -min_max_angle, -angle_step)):
            modified_angles[tilt_axis] = angle
            _set_view_angle(viewer, modified_angles + original_angles)
            screenshot = viewer.screenshot(canvas_only=canvas_only, flash=False)
            images.append(screenshot)

        # reset viewer
        _set_view_angle(viewer, original_angles)

        # turn RGBA into RGB
        image_stack = np.asarray(images)[..., 0:3]

        # reorganize to CTYX stack
        swapped = np.swapaxes(np.swapaxes(np.swapaxes(image_stack, 1, 0), 0, 3), 2, 3)

        # save image
        microanim = Microanim(data=swapped, cmaps=['pure_red', 'pure_green', 'pure_blue'], fig_scaling=10)
        microanim.save_movie(filename, fps=frames_per_second)

        print("Saving gif done.")

@register_function(menu="File Import/Export > Save animated 2D view as gif")
def save_2d_view(
        start_slice : int = 0,
        end_slice : int = 1,
        step : int = 1,
        frames_per_second: int = 15,
        canvas_only : bool = True,
        filename : "magicgui.types.PathLike" = "video.gif",
        viewer : napari.Viewer = None):
    filename = str(filename)
    if len(filename) > 0:
        if canvas_only:
            layer_types = [str(type(layer)).split('.')[-1][:-2] for layer in viewer.layers]
            if 'Labels' in layer_types:
                print('[WARNING]: canvas-only screenshots of images with label layers have color issues because of a napari bug.')
                print('If you want to make sure that colors are correct, make a gif of the whole viewer (de-select canvasonly)')
        print('Started generating gif...')
        from microfilm.microanim import Microanim
        
        axis = viewer.dims.order[0]
        end_slice = end_slice if end_slice < viewer.dims.nsteps[axis] else viewer.dims.nsteps[axis]

        original_step = viewer.dims.current_step[axis]
        images = []
        for slice in range(start_slice, end_slice, step):
            viewer.dims.set_current_step(axis, slice)
            
            screenshot = viewer.screenshot(canvas_only=canvas_only, flash=False)
            # turn RGBA into RGB
            images.append(screenshot[..., 0:3])
            print(f'\rProcessed slice {int(slice/step)}/{int((end_slice-start_slice-1)/step)}', end='')
        print('\nGenerating gif from slices...')

        # reset viewer
        viewer.dims.set_current_step(axis, original_step)

        # reorganize to CTYX stack
        swapped = np.swapaxes(np.swapaxes(np.swapaxes(images, 1, 0), 0, 3), 2, 3)

        # save image
        microanim = Microanim(data=swapped, cmaps=['pure_red', 'pure_green', 'pure_blue'], fig_scaling=10, alpha=1)
        microanim.save_movie(filename, fps=frames_per_second)
        print("Saving gif done.")
    

def _set_view_angle(viewer, angle):
    viewer.camera.angles = angle
    viewer.camera.update(viewer.camera)