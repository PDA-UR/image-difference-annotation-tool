import sys
from matplotlib.backend_bases import MouseButton
from matplotlib import pyplot as plt
import numpy as np

KEY_SWAP = 'x'
KEY_QUALITY_GOOD = '1'
KEY_QUALITY_MEDIUM = '2'
KEY_QUALITY_BAD = '3'
KEY_FALSE_POSITIVE = 'w'
KEY_ANNOTATION_HIGHLIGHT = 'a'
KEY_ANNOTATION_NOTE = 's'
KEY_ANNOTATION_UNDERLINE = 'd'
KEY_ANNOTATION_STRIKETHROUGH = 'f'

labels = {}
labels[KEY_SWAP] = 'swap images'
labels[KEY_QUALITY_GOOD] = 'good quality'
labels[KEY_QUALITY_MEDIUM] = 'medium quality'
labels[KEY_QUALITY_BAD] = 'bad quality'
labels[KEY_FALSE_POSITIVE] = 'false positive'
labels[KEY_ANNOTATION_HIGHLIGHT] = 'highlight'
labels[KEY_ANNOTATION_NOTE] = 'note'
labels[KEY_ANNOTATION_UNDERLINE] = 'underline'
labels[KEY_ANNOTATION_STRIKETHROUGH] = 'strikethrough'

if(len(sys.argv) < 3):
    print('too few arguments')
    print('usage: python3 annotation_tool.py image1 image2')
    sys.exit(0)

path_img_1 = sys.argv[1]
path_img_2 = sys.argv[2]
img_1 = plt.imread(path_img_1)
img_2 = plt.imread(path_img_2)

annotation_coordinates_1 = []
annotation_coordinates_2 = []

coords = {}
coords['good'] = []
coords['medium'] = []
coords['bad'] = []
coords['false_positive'] = []

current_mode = 'good'
current_type = 'highlight'

def create_labels(ax):
    x_size = ax.get_xlim()[1]
    y_size = ax.get_ylim()[0]
    x_pos = -0.8 * x_size
    x_offset_key = x_pos
    x_offset_text = x_pos + (x_size / 15)
    y_pos = 0.1 * y_size

    for key, text in labels.items():
        color = 'black'
        # TODO update text on keypress to make this work
        #if(current_mode in text or current_type in text):
        #    color = 'blue'

        plt.text(x_offset_key, y_pos, f'{key}', fontsize=18, c=color)
        plt.text(x_offset_text, y_pos, f'{text}', fontsize=18, c=color)
        y_pos += (y_size / 20)

def update_plot():
    global annotation_plot
    for mode in coords.keys():
        if(len(coords[mode]) < 1):
            continue
        tmp = np.array(coords[mode])
        tmp = tmp.transpose()
        tmp = tmp.tolist()
        annotation_plot[mode].set_offsets(np.c_[tmp[0], tmp[1]])

def on_press(event):
    global current_mode
    if event.key == KEY_SWAP:
        img_handle_1.set_visible(not img_handle_1.get_visible())
        img_handle_2.set_visible(not img_handle_2.get_visible())
        fig.canvas.draw()
    elif event.key == KEY_QUALITY_GOOD:
        current_mode = 'good'
    elif event.key == KEY_QUALITY_MEDIUM:
        current_mode = 'medium'
    elif event.key == KEY_QUALITY_BAD:
        current_mode = 'bad'
    elif event.key == KEY_FALSE_POSITIVE:
        current_mode = 'false_positive'

def on_click(event):
    if fig.canvas.cursor().shape() != 0:
        # we are in zoom or pan mode as the cursor has no default shape
        return
    if event.button is MouseButton.LEFT:
        print(event.xdata, event.ydata)
        coords[current_mode].append([event.xdata, event.ydata])
        update_plot()
        fig.canvas.draw()

fig, ax = plt.subplots()

fig.canvas.mpl_connect('key_press_event', on_press)
plt.connect('button_press_event', on_click)

plt.rcParams['keymap.save'].remove('s')
plt.rcParams['keymap.fullscreen'].remove('f')

img_handle_1 = plt.imshow(img_1)
img_handle_2 = plt.imshow(img_2)
img_handle_2.set_visible(False)

annotation_plot = {}
annotation_plot['good'] = plt.scatter([], [], s=50, c='lime', edgecolors='black')
annotation_plot['medium'] = plt.scatter([], [], s=50, c='yellow', edgecolors='black')
annotation_plot['bad'] = plt.scatter([], [], s=50, c='red', edgecolors='black')
annotation_plot['false_positive'] = plt.scatter([], [], s=50, c='blue', edgecolors='black')

create_labels(ax)

plt.show()
