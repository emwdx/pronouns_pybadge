"""
This code is adapted from the Conference Badge at https://learn.adafruit.com/pybadge-conference-badge-multi-language-unicode-fonts/overview
The code is modified to change the displayed pronoun every second.
Pronouns are set on line 31. Enter the pronoun with the most letters _first_.
"""

import time
from math import sqrt, cos, sin, radians
import board
from micropython import const
import displayio
import digitalio
import neopixel
from gamepadshift import GamePadShift
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

# Button Constants
BUTTON_LEFT = const(128)
BUTTON_UP = const(64)
BUTTON_DOWN = const(32)
BUTTON_RIGHT = const(16)
BUTTON_SEL = const(8)
BUTTON_START = const(4)
BUTTON_A = const(2)
BUTTON_B = const(1)

# Always enter the pronoun with the largest number of letters first. This is to initialize the label correctly.
# Someone else will show me a better way to make sure this works :)
PRONOUNS = ["HIS","HIM","HE"]

# To fit THEIRS on the screen, use a smaller font.
if(len(PRONOUNS[0]) == 6):
    FONTNAME = "/fonts/OpenSans-Bold-44.bdf"
else:
    FONTNAME = "/fonts/OpenSans-Bold-60.bdf"

NEOPIXEL_COUNT = 5
BACKGROUND_COLOR = 0x000000
FOREGROUND_TEXT_COLOR = 0xFFFFFF

# Default Values
brightness = 0.2
direction = 1
speed = 1

# Define the NeoPixel and Game Pad Objects
neopixels = neopixel.NeoPixel(board.NEOPIXEL, NEOPIXEL_COUNT, brightness=brightness,
                              auto_write=False, pixel_order=neopixel.GRB)

pad = GamePadShift(digitalio.DigitalInOut(board.BUTTON_CLOCK),
                   digitalio.DigitalInOut(board.BUTTON_OUT),
                   digitalio.DigitalInOut(board.BUTTON_LATCH))

# Make the Display Background
splash = displayio.Group(max_size=60)
board.DISPLAY.show(splash)

color_bitmap = displayio.Bitmap(160, 128, 1)
color_palette = displayio.Palette(1)
color_palette[0] = BACKGROUND_COLOR

bg_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette,
                               x=0, y=0)
splash.append(bg_sprite)


# Load the Name font
pronoun_font_name = FONTNAME
pronoun_font = bitmap_font.load_font(pronoun_font_name)
pronoun_font.load_glyphs(PRONOUNS[0].encode('utf-8'))

# Setup and Center the Pronoun Label
name_label = Label(pronoun_font, text=PRONOUNS[0], line_spacing=0.75)
(x, y, w, h) = name_label.bounding_box
name_label.x = (80 - w // 2)
name_label.y = 65
name_label.color = FOREGROUND_TEXT_COLOR
splash.append(name_label)

# Remap the calculated rotation to 0 - 255
def remap(vector):
    return int(((255 * vector + 85) * 0.75) + 0.5)

# Calculate the Hue rotation starting with Red as 0 degrees
def rotate(degrees):
    cosA = cos(radians(degrees))
    sinA = sin(radians(degrees))
    red = cosA + (1.0 - cosA) / 3.0
    green = 1./3. * (1.0 - cosA) + sqrt(1./3.) * sinA
    blue = 1./3. * (1.0 - cosA) - sqrt(1./3.) * sinA
    return (remap(red), remap(green), remap(blue))

palette = []
pixels = []

# Generate a rainbow palette
for degree in range(0, 360):
    color = rotate(degree)
    palette.append(color[0] << 16 | color[1] << 8 | color[2])

# Create the Pattern
for x in range(0, NEOPIXEL_COUNT):
    pixels.append(x * 360 // NEOPIXEL_COUNT)

pronoun_index = 0
pronoun_loop_timer = time.monotonic()
PRONOUN_SWITCH_TIME = 1.0

# Main Loop
current_buttons = pad.get_pressed()
last_read = 0
while True:
    #Switch the pronoun on the screen after PRONOUN_SWITCH_TIME seconds have passed.
    if(time.monotonic() - pronoun_loop_timer > PRONOUN_SWITCH_TIME):
        if(pronoun_index == len(PRONOUNS) - 1):
            pronoun_index = 0
        else:
            pronoun_index += 1
        pronoun_loop_timer = time.monotonic()

        name_label.text = PRONOUNS[pronoun_index]

    for color in range(0, 360, speed):
        for index in range(0, NEOPIXEL_COUNT):
            palette_index = pixels[index] + color * direction
            if palette_index >= 360:
                palette_index -= 360
            elif palette_index < 0:
                palette_index += 360
            neopixels[index] = palette[palette_index]
        neopixels.show()
        neopixels.brightness = brightness
        # Reading buttons too fast returns 0
        if (last_read + 0.1) < time.monotonic():
            buttons = pad.get_pressed()
            last_read = time.monotonic()
        if current_buttons != buttons:
            # Respond to the buttons
            if (buttons & BUTTON_RIGHT) > 0:
                direction = -1
            elif (buttons & BUTTON_LEFT) > 0:
                direction = 1
            elif (buttons & BUTTON_UP) > 0 and speed < 10:
                speed += 1
            elif (buttons & BUTTON_DOWN) > 0 and speed > 1:
                speed -= 1
            elif (buttons & BUTTON_A) > 0 and brightness < 0.5:
                brightness += 0.025
            elif (buttons & BUTTON_B) > 0 and brightness > 0.025:
                brightness -= 0.025
            current_buttons = buttons
