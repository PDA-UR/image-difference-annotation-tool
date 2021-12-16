import sys
from matplotlib.backend_bases import MouseButton
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

KEY_SWAP = 'x'
KEY_QUALITY_GOOD = '1'
KEY_QUALITY_MEDIUM = '2'
KEY_QUALITY_BAD = '3'
KEY_FALSE_POSITIVE = 'w'
KEY_ANNOTATION_HIGHLIGHT = 'a'
KEY_ANNOTATION_NOTE = 's'
KEY_ANNOTATION_UNDERLINE = 'd'
KEY_ANNOTATION_STRIKETHROUGH = 'f'

ui_text = {}
ui_text[KEY_SWAP] = 'swap images'
ui_text[KEY_QUALITY_GOOD] = 'good quality'
ui_text[KEY_QUALITY_MEDIUM] = 'medium quality'
ui_text[KEY_QUALITY_BAD] = 'bad quality'
ui_text[KEY_FALSE_POSITIVE] = 'false positive'
ui_text[KEY_ANNOTATION_HIGHLIGHT] = 'highlight'
ui_text[KEY_ANNOTATION_NOTE] = 'note'
ui_text[KEY_ANNOTATION_UNDERLINE] = 'underline'
ui_text[KEY_ANNOTATION_STRIKETHROUGH] = 'strikethrough'

if(len(sys.argv) < 3):
    print('too few arguments')
    print('usage: python3 annotation_tool.py image1 image2')
    sys.exit(0)

path_img_1 = sys.argv[1]
path_img_2 = sys.argv[2]
img_1 = plt.imread(path_img_1)
img_2 = plt.imread(path_img_2)

coords = {}
coords['good'] = []
coords['medium'] = []
coords['bad'] = []
coords['false_positive'] = []

current_mode = 'good'
current_type = 'highlight'

annotations = pd.DataFrame(columns=['x', 'y', 'type', 'quality'])

def create_annotation(x, y, t, q):
    global annotations
    annotations = annotations.append({'x' : x, 'y' : y, 'type' : t, 'quality' : q}, ignore_index=True)

def create_description(ax):
    x_size = ax.get_xlim()[1]
    y_size = ax.get_ylim()[0]

    x_pos = -0.8 * x_size
    x_offset_key = x_pos
    x_offset_text = x_pos + (x_size / 15)
    x_offset_indicator = x_pos + (x_size * 0.4)

    y_pos = 0.1 * y_size

    for key, text in ui_text.items():
        color = 'black'

        plt.text(x_offset_key, y_pos, f'{key}', fontsize=18, c=color)
        plt.text(x_offset_text, y_pos, f'{text}', fontsize=18, c=color)

        y_pos += (y_size / 20)

    y_pos += (y_size / 20)
    plt.text(x_offset_key, y_pos, 'current quality:', fontsize=18, c=color)
    mode_label = plt.text(x_offset_indicator, y_pos, f'{current_mode}', fontsize=18, c=color)

    y_pos += (y_size / 20)
    plt.text(x_offset_key, y_pos, 'current mode:', fontsize=18, c=color)
    type_label = plt.text(x_offset_indicator, y_pos, f'{current_type}', fontsize=18, c=color)

    return mode_label, type_label

def update_plot():
    global annotation_plot, annotations
    for mode in coords.keys():
        df = annotations[annotations['quality'] == mode]
        x_values = list(df['x'])
        y_values = list(df['y'])

        if(len(x_values) < 1):
            continue
        annotation_plot[mode].set_offsets(np.c_[x_values, y_values])

def on_press(event):
    global current_mode
    global current_type
    global mode_label
    global type_label

    if event.key == KEY_SWAP:
        img_handle_1.set_visible(not img_handle_1.get_visible())
        img_handle_2.set_visible(not img_handle_2.get_visible())
    elif event.key == KEY_QUALITY_GOOD:
        current_mode = 'good'
    elif event.key == KEY_QUALITY_MEDIUM:
        current_mode = 'medium'
    elif event.key == KEY_QUALITY_BAD:
        current_mode = 'bad'
    elif event.key == KEY_FALSE_POSITIVE:
        current_mode = 'false_positive'
    elif event.key == KEY_ANNOTATION_HIGHLIGHT:
        current_type = 'highlight'
    elif event.key == KEY_ANNOTATION_NOTE:
        current_type = 'note'
    elif event.key == KEY_ANNOTATION_UNDERLINE:
        current_type = 'underline'
    elif event.key == KEY_ANNOTATION_STRIKETHROUGH:
        current_type = 'strikethrough'

    mode_label.set_text(current_mode)
    type_label.set_text(current_type)
    fig.canvas.draw()

def on_click(event):
    if fig.canvas.cursor().shape() != 0:
        # we are in zoom or pan mode as the cursor has no default shape
        return
    if event.button is MouseButton.LEFT:
        print(event.xdata, event.ydata)
        #coords[current_mode].append([event.xdata, event.ydata])
        create_annotation(event.xdata, event.ydata, current_type, current_mode)
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

#new_plot = sns.scatterplot(data=annotations, x='x', y='y', hue='quality', axes=ax)

mode_label, type_label = create_description(ax)

plt.show()
