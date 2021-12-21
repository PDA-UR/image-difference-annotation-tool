import sys
from matplotlib.backend_bases import MouseButton
from matplotlib import pyplot as plt
from matplotlib import patches as patches
import numpy as np
import pandas as pd

# key bindings
KEY_SWAP = 'x'
KEY_UNDO = 'u'
KEY_REDO = 'r'
#KEY_LABELS = 'l'
KEY_QUIT = 'q'
KEY_HOME = 'h'
KEY_QUALITY_GOOD = '1'
KEY_QUALITY_MEDIUM = '2'
KEY_QUALITY_BAD = '3'
KEY_FALSE_POSITIVE = 'w'
KEY_ANNOTATION_HIGHLIGHT = 'a'
KEY_ANNOTATION_NOTE = 's'
KEY_ANNOTATION_UNDERLINE = 'd'
KEY_ANNOTATION_STRIKETHROUGH = 'f'

# UI labels
ui_text = {}
ui_text[KEY_SWAP] = 'swap images'
ui_text[KEY_UNDO] = 'undo last annotation'
ui_text[KEY_REDO] = 'redo last undo'
#ui_text[KEY_LABELS] = 'show labels'
ui_text[KEY_HOME] = 'reset zoom'
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

qualities = ['good', 'medium', 'bad', 'false_positive']
types = ['highlight', 'note', 'underline', 'strikethrough']

current_quality = qualities[0]
current_type = types[0]
#show_labels = True

annotations = pd.DataFrame(columns=['x', 'y', 'type', 'quality'])
annotations_undo_stack = pd.DataFrame(columns=['x', 'y', 'type', 'quality'])

def create_annotation(x, y, t, q):
    global annotations
    annotations = annotations.append({'x' : x, 'y' : y, 'type' : t, 'quality' : q}, ignore_index=True)

def save_annotations():
    annotations.to_csv(sys.stdout, index_label='id')

def create_description_old(ax):
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
    quality_label = ax.text(x_offset_indicator, y_pos, f'{current_quality}', fontsize=18, c=color, bbox=dict(facecolor='white', linewidth=0, alpha=1))

    y_pos += (y_size / 20)
    plt.text(x_offset_key, y_pos, 'current quality:', fontsize=18, c=color)
    type_label = ax.text(x_offset_indicator, y_pos, f'{current_type}', fontsize=18, c=color, bbox=dict(facecolor='white', linewidth=0, alpha=1))


    return quality_label, type_label

def create_description(ax):
    x_size = 1
    y_size = 1

    x_pos = 0.1
    x_offset_key = x_pos
    x_offset_text = x_pos + (x_size / 15)
    x_offset_indicator = x_pos + (x_size * 0.4)

    y_pos = 0.1 * y_size

    for key, text in ui_text.items():
        color = 'black'

        ax.text(x_offset_key, y_pos, f'{key}', fontsize=18, c=color)
        ax.text(x_offset_text, y_pos, f'{text}', fontsize=18, c=color)

        y_pos += (y_size / 20)

    y_pos += (y_size / 20)

    ax.text(x_offset_key, y_pos, 'quality:', fontsize=18, c=color)
    quality_label = ax.text(x_offset_indicator, y_pos, f'{current_quality}', fontsize=18, c=color, bbox=dict(facecolor='white', linewidth=0, alpha=1))

    y_pos += (y_size / 20)
    ax.text(x_offset_key, y_pos, 'type:', fontsize=18, c=color)
    type_label = ax.text(x_offset_indicator, y_pos, f'{current_type}', fontsize=18, c=color, bbox=dict(facecolor='white', linewidth=0, alpha=1))


    return quality_label, type_label

def update_plot():
    global annotation_plot, annotations, qualities #, show_labels

    #x_size = ax.get_xlim()[1]
    #y_size = ax.get_ylim()[0]
    #x_offset_label = x_size * 0.02
    #y_offset_label = y_size * 0.02

    for quality in qualities:
        df = annotations[annotations['quality'] == quality]
        x_values = list(df['x'])
        y_values = list(df['y'])

        if(len(x_values) < 1):
            continue
        annotation_plot[quality].set_offsets(np.c_[x_values, y_values])
        ax_image.draw_artist(annotation_plot[quality])

    # ax.draw_artist() and fig.canvas.update() is WAY faster than fig.canvas.draw()
    # source: https://bastibe.de/2013-05-30-speeding-up-matplotlib.html
    fig.canvas.update()
    fig.canvas.flush_events()

    # annotations disabled for now, as they get redrawn over and over again
    #if(show_labels):
    #    for index, row in annotations.iterrows():
    #        ax.annotate(row['type'], xy=(row['x'], row['y']), xytext=(row['x'] + x_offset_label, row['y'] + y_offset_label))

def undo():
    global annotations, annotations_undo_stack
    annotations_undo_stack = annotations_undo_stack.append(annotations[-1:])
    annotations = annotations[:-1]
    update_plot()
    fig.canvas.draw_idle()

def redo():
    global annotations, annotations_undo_stack
    annotations = annotations.append(annotations_undo_stack[-1:])
    annotations_undo_stack = annotations_undo_stack[:-1]
    update_plot()

def on_press(event):
    global current_quality
    global current_type
    global quality_label
    global type_label
    global show_labels

    if event.key == KEY_SWAP:
        img_handle_1.set_visible(not img_handle_1.get_visible())
        img_handle_2.set_visible(not img_handle_2.get_visible())
        ax_image.draw_artist(img_handle_1)
        ax_image.draw_artist(img_handle_2)
        #fig.canvas.draw()
    elif event.key == KEY_UNDO:
        undo()
    elif event.key == KEY_REDO:
        redo()
    #elif event.key == KEY_LABELS:
    #    show_labels = not show_labels
    #    update_plot()
    elif event.key == KEY_QUIT:
        save_annotations()
        sys.exit(0)
    elif event.key == KEY_QUALITY_GOOD:
        current_quality = 'good'
    elif event.key == KEY_QUALITY_MEDIUM:
        current_quality = 'medium'
    elif event.key == KEY_QUALITY_BAD:
        current_quality = 'bad'
    elif event.key == KEY_FALSE_POSITIVE:
        current_quality = 'false_positive'
    elif event.key == KEY_ANNOTATION_HIGHLIGHT:
        current_type = 'highlight'
    elif event.key == KEY_ANNOTATION_NOTE:
        current_type = 'note'
    elif event.key == KEY_ANNOTATION_UNDERLINE:
        current_type = 'underline'
    elif event.key == KEY_ANNOTATION_STRIKETHROUGH:
        current_type = 'strikethrough'

    # wow that's hacky!
    # add spaces so bounding boxes cover the old text
    quality_label.set_text(f'{current_quality}        ')
    type_label.set_text(f'{current_type}        ')

    ax_description.draw_artist(quality_label)
    ax_description.draw_artist(type_label)
    fig.canvas.update()
    fig.canvas.flush_events()

def on_click(event):
    if fig.canvas.cursor().shape() != 0:
        # we are in zoom or pan quality as the cursor has no default shape
        return
    if event.button is MouseButton.LEFT:
        # clear undo stack when new annotation is made
        annotations_undo_stack.drop(annotations_undo_stack.index, inplace=True)

        create_annotation(event.xdata, event.ydata, current_type, current_quality)
        update_plot()
        #fig.canvas.draw()

fig, axes = plt.subplots(1, 2, gridspec_kw={'width_ratios': [1, 2.5]})
ax = axes[1]
ax_description = axes[0]
ax_description.invert_yaxis()
ax_image = axes[1]

fig.canvas.mpl_connect('key_press_event', on_press)
plt.connect('button_press_event', on_click)

plt.rcParams['keymap.save'].remove('s')
plt.rcParams['keymap.fullscreen'].remove('f')
plt.rcParams['keymap.yscale'].remove('l')
plt.rcParams['keymap.quit'].remove('q')
plt.rcParams['keymap.home'].remove('r')

img_handle_1 = axes[1].imshow(img_1)
img_handle_2 = axes[1].imshow(img_2)
img_handle_2.set_visible(False)

annotation_plot = {}
annotation_plot['good'] = ax_image.scatter([], [], s=50, c='lime', edgecolors='black')
annotation_plot['medium'] = ax_image.scatter([], [], s=50, c='yellow', edgecolors='black')
annotation_plot['bad'] = ax_image.scatter([], [], s=50, c='red', edgecolors='black')
annotation_plot['false_positive'] = ax_image.scatter([], [], s=50, c='blue', edgecolors='black')

quality_label, type_label = create_description(ax_description)

plt.show()
