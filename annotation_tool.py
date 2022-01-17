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
KEY_HOME = 't'
KEY_QUALITY_GOOD = '1'
KEY_QUALITY_MEDIUM = '2'
KEY_QUALITY_BAD = '3'
KEY_FALSE_POSITIVE = 'w'
KEY_ANNOTATION_HIGHLIGHT = 'a'
KEY_ANNOTATION_NOTE = 's'
KEY_ANNOTATION_UNDERLINE = 'd'
KEY_ANNOTATION_STRIKETHROUGH = 'f'
KEY_ANNOTATION_INLINE = 'g'
KEY_ANNOTATION_ARROW = 'h'
KEY_ANNOTATION_OTHER = 'j'
KEY_PEN_HIGHLIGHTER = 'c'
KEY_PEN_SHARPIE = 'v'
KEY_PEN_BALLHEAD = 'b'

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
ui_text[KEY_ANNOTATION_OTHER] = 'other'

if(len(sys.argv) < 3):
    print('too few arguments')
    print('usage: python3 annotation_tool.py image1 image2')
    sys.exit(0)

# read images from paths
path_img_1 = sys.argv[1]
path_img_2 = sys.argv[2]
img_1 = plt.imread(path_img_1)
img_2 = plt.imread(path_img_2)

# if no path for the result csv was passed, generate it from image paths
if(len(sys.argv) > 3):
    scan_id = sys.argv[3]
else:
    scan_id = path_img_1.split('/')[-1].split('.')[0]
    scan_id = scan_id.replace('_RGB', '').replace('_annotation', '')

# quality levels, annotation types, pen types and colors
qualities = ['good', 'medium', 'bad', 'false_positive']
types = ['highlight', 'note', 'underline', 'strikethrough', 'inline', 'arrow', 'other']
pens = ['highlighter', 'sharpie', 'ballhead']
pen_colors = dict()
pen_colors['highlighter'] = ['yellow', 'pink', 'green', 'blue']
pen_colors['sharpie'] = ['black', 'blue', 'green', 'red']
pen_colors['ballhead'] = ['black', 'blue']

# initial values
current_quality = qualities[0]
current_type = types[0]
current_pen = pens[0]
pen_color_index = 0

# data frames to store annotations and undo stack
annotations = pd.DataFrame(columns=['x', 'y', 'type', 'quality', 'pen'])
annotations_undo_stack = pd.DataFrame(columns=['x', 'y', 'type', 'quality', 'pen'])

# add annotation to data frame
def create_annotation(x, y, t, q, p):
    global annotations
    annotations = annotations.append({'x' : x, 'y' : y, 'type' : t, 'quality' : q, 'pen' : p}, ignore_index=True)

# save result to csv
def save_annotations():
    annotations['scan_id'] = scan_id
    annotations.to_csv(sys.stdout, index_label='id')

# creates UI on the left hand side
def create_description(ax):
    x_size = 1
    y_size = 1

    x_pos = 0.1
    x_offset_key = x_pos
    x_offset_text = x_pos + (x_size / 15)
    x_offset_indicator = x_pos + (x_size * 0.4)

    y_pos = 0.1 * y_size
    y_margin_constant = 25

    # functions + shortcut
    for key, text in ui_text.items():
        color = 'black'

        ax.text(x_offset_key, y_pos, f'{key}', fontsize=18, c=color)
        ax.text(x_offset_text, y_pos, f'{text}', fontsize=18, c=color)

        y_pos += (y_size / y_margin_constant)

    # current state
    y_pos += (y_size / y_margin_constant)
    ax.text(x_offset_key, y_pos, 'current selection:', fontsize=18, c=color)

    y_pos += (y_size / y_margin_constant)
    quality_label = ax.text(x_offset_key, y_pos, f'{current_quality} quality', fontsize=18, c=color, bbox=dict(facecolor='white', linewidth=0, alpha=1))

    y_pos += (y_size / y_margin_constant)
    type_label = ax.text(x_offset_key, y_pos, f'{current_type}', fontsize=18, c=color, bbox=dict(facecolor='white', linewidth=0, alpha=1))

    y_pos += (y_size / y_margin_constant)
    ax.text(x_offset_key, y_pos, 'current pen:', fontsize=18, c=color)

    y_pos += (y_size / y_margin_constant)
    pen_label = ax.text(x_offset_key, y_pos, f'{current_pen}, {pen_colors[current_pen][pen_color_index]}', fontsize=18, c=color, bbox=dict(facecolor='white', linewidth=0, alpha=1))

    # return references to UI elements so they can be updated later
    return quality_label, type_label, pen_label

def update_plot():
    global annotation_plot, annotations, qualities

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

# undo last annotation
def undo():
    global annotations, annotations_undo_stack
    annotations_undo_stack = annotations_undo_stack.append(annotations[-1:])
    annotations = annotations[:-1]
    update_plot()
    fig.canvas.draw_idle()

# redo last undone annotation
def redo():
    global annotations, annotations_undo_stack
    annotations = annotations.append(annotations_undo_stack[-1:])
    annotations_undo_stack = annotations_undo_stack[:-1]
    update_plot()

def on_press(event):
    global current_quality, current_type, current_pen
    global pen_colors, pen_color_index
    global quality_label, type_label, pen_label
    global ax_image

    if event.key == KEY_SWAP:
        # swap between both images
        img_handle_1.set_visible(not img_handle_1.get_visible())
        img_handle_2.set_visible(not img_handle_2.get_visible())
        fig.canvas.draw()
    elif event.key == KEY_UNDO:
        undo()
    elif event.key == KEY_REDO:
        redo()
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
    elif event.key == KEY_ANNOTATION_INLINE:
        current_type = 'inline'
    elif event.key == KEY_ANNOTATION_ARROW:
        current_type = 'arrow'
    elif event.key == KEY_ANNOTATION_OTHER:
        current_type = 'other'
    elif event.key == KEY_PEN_HIGHLIGHTER:
        # swap between colors if key for already selected pen is pressed
        if current_pen == 'highlighter':
            pen_color_index = (pen_color_index + 1) % len(pen_colors[current_pen])
        else:
            current_pen = 'highlighter'
            pen_color_index = 0
    elif event.key == KEY_PEN_SHARPIE:
        if current_pen == 'sharpie':
            pen_color_index = (pen_color_index + 1) % len(pen_colors[current_pen])
        else:
            current_pen = 'sharpie'
            pen_color_index = 0
    elif event.key == KEY_PEN_BALLHEAD:
        if current_pen == 'ballhead':
            pen_color_index = (pen_color_index + 1) % len(pen_colors[current_pen])
        else:
            current_pen = 'ballhead'
            pen_color_index = 0

    # wow that's hacky!
    # add spaces so bounding boxes cover the old text
    quality_label.set_text(f'{current_quality} quality       ')
    type_label.set_text(f'{current_type}        ')
    pen_label.set_text(f'{current_pen}, {pen_colors[current_pen][pen_color_index]}           ')

    ax_description.draw_artist(quality_label)
    ax_description.draw_artist(type_label)
    ax_description.draw_artist(pen_label)
    fig.canvas.update()
    fig.canvas.flush_events()

def on_click(event):
    if fig.canvas.cursor().shape() != 0:
        # we are in zoom or pan quality as the cursor has no default shape
        return
    if event.button is MouseButton.LEFT:
        # clear undo stack when new annotation is made
        annotations_undo_stack.drop(annotations_undo_stack.index, inplace=True)

        create_annotation(event.xdata, event.ydata, current_type, current_quality, f'{current_pen}_{pen_colors[current_pen][pen_color_index]}')
        update_plot()
        #fig.canvas.draw()

# left: UI, right: image
fig, axes = plt.subplots(1, 2, gridspec_kw={'width_ratios': [1, 2.5]})
plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

# 0/0 is top left
ax_description = axes[0]
ax_description.invert_yaxis()
ax_description.axis('off')

ax_image = axes[1]
ax_image.axis('off')

# add event handlers
fig.canvas.mpl_connect('key_press_event', on_press)
plt.connect('button_press_event', on_click)

# remove pyplot keybindings that are used in the application
plt.rcParams['keymap.save'].remove('s')
plt.rcParams['keymap.fullscreen'].remove('f')
plt.rcParams['keymap.yscale'].remove('l')
plt.rcParams['keymap.quit'].remove('q')
plt.rcParams['keymap.home'].remove('r')
plt.rcParams['keymap.home'].remove('h')
plt.rcParams['keymap.back'].remove('c')
plt.rcParams['keymap.forward'].remove('v')
plt.rcParams['keymap.grid'].remove('g')

# one image is always shown, the other one is always hidden
img_handle_1 = axes[1].imshow(img_1)
img_handle_2 = axes[1].imshow(img_2)
img_handle_2.set_visible(False)

# dots for annotations
annotation_plot = {}
annotation_plot['good'] = ax_image.scatter([], [], s=50, c='lime', edgecolors='black')
annotation_plot['medium'] = ax_image.scatter([], [], s=50, c='yellow', edgecolors='black')
annotation_plot['bad'] = ax_image.scatter([], [], s=50, c='red', edgecolors='black')
annotation_plot['false_positive'] = ax_image.scatter([], [], s=50, c='blue', edgecolors='black')

quality_label, type_label, pen_label = create_description(ax_description)

plt.show()
