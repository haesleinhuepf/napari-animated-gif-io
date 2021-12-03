"""
This module is an example of a barebones writer plugin for napari

It implements the ``napari_get_writer`` and ``napari_write_image`` hook specifications.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs
"""

from napari_plugin_engine import napari_hook_implementation

# some parts of the code here were taken from
# https://github.com/DragaDoncila/napari-compressed-labels-io/blob/master/napari_compressed_labels_io/_writer.py#L60
# Licensed MIT by Draga Doncila Pop
# https://github.com/DragaDoncila/napari-compressed-labels-io/blob/master/LICENSE

@napari_hook_implementation
def napari_get_writer(path, layer_types):
    print("A")
    if isinstance(path, str):
        path = [path]

    print("B")
    if not all([pth.endswith('.gif') for pth in path]):
        return None

    print("C")
    if not all([layer == 'image' for layer in layer_types]):
        return None

    print("D")
    if not all([len(layer.shape) == 3 or (len(layer.shape) == 4 and layer.shape[1] == 1) for layer in layer_types]):
        return None

    print("E")
    return napari_write_image


@napari_hook_implementation
def napari_write_image(path, data, meta, duration=0.5):
    import imageio
    with imageio.get_writer(path, mode='I', duration=duration) as writer:
        for i in range(data.shape[0]):
            image = data[i]
            if len(image.shape) == 3:
                image = image[0]
            writer.append_data(image)
