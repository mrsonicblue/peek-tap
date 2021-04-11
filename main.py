import os
import sys
import gc
import time
import pwmio
import board
import busio
import digitalio
import displayio
import supervisor
import adafruit_imageload
import adafruit_touchscreen
import usb_cdc
import usb_hid
import storage
import sdcardio
import render_bdf
from adafruit_mcp230xx.mcp23008 import MCP23008
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from channel import Channel
from button import Button
from label import Label

# spi = board.SPI()
# sd_cs = board.SD_CS
# sdcard = None

# try:
#     sdcard = sdcardio.SDCard(spi, sd_cs)
#     vfs = storage.VfsFat(sdcard)
#     storage.mount(vfs, "/sd")
# except OSError as error:
#     print("No SD card found:", error)

# while True:
#     time.sleep(1)

WHITE = 0xFFFFFF
GREY = 0x888888
BLACK = 0x000000
BUTTON1 = 0x3D1810
BUTTON2 = 0x7F3122

i2c = busio.I2C(board.SCL, board.SDA)
try:
    mcp = MCP23008(i2c)
except:
    mcp = None

def file_exists(path):
    try:
        stat = os.stat(path)
        #TODO: return stat.S_ISREG(stat[state.ST_MODE])
        return True
    except OSError:
        return False

def setup_pin(mcp, index):
    pin = mcp.get_pin(index)
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.UP
    return pin

if mcp is not None:
    pins = []
    pin_states = []
    pin_count = 8
    for pin in range(pin_count):
        pins.append(setup_pin(mcp, pin))
        pin_states.append(True)

    pin_keys = [
        [Keycode.F12],
        [Keycode.RIGHT_ARROW],
        [Keycode.UP_ARROW],
        [Keycode.DOWN_ARROW],
        [Keycode.LEFT_ARROW],
        [Keycode.ENTER],
        [Keycode.ESCAPE],
        [Keycode.ALT, Keycode.F12],
    ]

    kbd = Keyboard(usb_hid.devices)

def wrap(s, max_chars, indent=0):
    s = s.replace('\n', '').replace('\r', '')
    words = s.split(' ')
    lines = []
    line = []
    count = 0
    for w in words:
        w = w[:max_chars]
        wl = len(w)
        if count + wl > max_chars:
            lines.append(line)
            line = []
            count = 0
        line.append(w)
        count += wl + 1
    lines.append(line)
    lines = list(map(lambda w: (" " * indent) + " ".join(w), lines))
    return '\n'.join(lines)

display = board.DISPLAY
display.rotation = 90

root = displayio.Group(max_size=10)
display.show(root)

palette_white = displayio.Palette(2)
palette_white.make_transparent(0)
palette_white[1] = WHITE

palette_grey = displayio.Palette(2)
palette_white.make_transparent(0)
palette_grey[1] = GREY

GLYPH_COUNT = 160
GLYPH_WIDTH = 8
GLYPH_HEIGHT = 17
glyphs = displayio.Bitmap(GLYPH_COUNT * GLYPH_WIDTH, GLYPH_HEIGHT, 2)

glyph_list = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.:/!() '
normal_map = render_bdf.render_bdf("/fonts/gohufont-14.bdf", glyph_list, glyphs, GLYPH_WIDTH, GLYPH_HEIGHT, 1)
bold_map = render_bdf.render_bdf("/fonts/gohufont-14b.bdf", glyph_list, glyphs, GLYPH_WIDTH, GLYPH_HEIGHT, len(normal_map) + 1)
font_maps = [normal_map, bold_map]

def label(text, x, y, width, height, palette=palette_white):
    global glyphs, font_maps, GLYPH_WIDTH, GLYPH_HEIGHT
    return Label(glyphs, pixel_shader=palette, font_maps=font_maps, text=text, width=width, height=height, tile_width=GLYPH_WIDTH, tile_height=GLYPH_HEIGHT, x=x, y=y)

icons = adafruit_imageload.load("icons.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
icons[1].make_transparent(0)

ICON_WIDTH = 18
ICON_HEIGHT = 16
icon_list = ['box','cartridge','generic','heart-grey','heart-red','GAMEBOY', "GBA",'Genesis','MENU','NES','SNES','ATARI2600']
icon_lookup = {k: v for v, k in enumerate(icon_list)}

def icon_sprite(name, x=0, y=0):
    global icons, icon_lookup, ICON_WIDTH, ICON_HEIGHT
    tile = icon_lookup[name]
    return displayio.TileGrid(icons[0], pixel_shader=icons[1], default_tile=tile, x=x, y=y, tile_width=ICON_WIDTH, tile_height=ICON_HEIGHT)

doubler = displayio.Group(max_size=10, scale=2)
root.append(doubler)

header = displayio.Group(max_size=10)
root.append(header)

core_sprite = icon_sprite("MENU", x=0, y=1)
doubler.append(core_sprite)

core_label = label("", x=19, y=0, width=17, height=1)
doubler.append(core_label)

rom_sprite = icon_sprite("cartridge", x=0, y=18)
doubler.append(rom_sprite)

rom_label = label("", x=38, y=34, width=35, height=2)
header.append(rom_label)

rule_bitmap = displayio.Bitmap(320, 1, 1)
rule_palette = displayio.Palette(1)
rule_palette[0] = GREY
rule_sprite = displayio.TileGrid(rule_bitmap, pixel_shader=rule_palette, x=0, y=76)
header.append(rule_sprite)

body = displayio.Group(max_size=20)
root.append(body)

date_label = label("", x=0, y=80, width=40, height=1)
body.append(date_label)

details_label = label("", x=0, y=100, width=40, height=18)
body.append(details_label)

fav_button = Button(
    id="fav",
    x=0,
    y=206,
    width=34,
    height=34,
    style=Button.RECT,
    fill_color=BUTTON1,
    selected_fill=BUTTON2,
    outline_color=WHITE,
    selected_outline=WHITE,
    icon = icon_sprite("heart-grey")
)
doubler.append(fav_button.group)

buttons = [fav_button]

touch = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL,
    board.TOUCH_XR,
    board.TOUCH_YD,
    board.TOUCH_YU,
    calibration=((8000, 60000), (9000, 55000)),
    size=(480, 320),
)

channel = Channel(usb_cdc.serials[1])

core_name = "MENU"
rom_name = None
rom_fav = False

def switch_core(new_name):
    global core_name, header, core_label, core_sprite, icon_lookup

    core_name = new_name
    core_label.text = '\1' + (core_name or "(none)")
    core_sprite[0] = icon_lookup[core_name] if core_name in icon_lookup else icon_lookup["generic"]

def switch_rom(new_name, fav_check=True):
    global channel, core_name, rom_name, rom_label

    rom_name = new_name
    rom_label.text = wrap(rom_name or "(none)", 35)
    details_label.text = ""

    if core_name and rom_name and fav_check:
        channel.write(["rom_keys", "dbkeys", rom_name])

def switch_date(date):
    global date_label

    date_label.text = date

def process_keys(keys):
    global core_name, fav_button, icon_lookup, rom_fav, details_label

    has_key = "has/" + core_name + "/"
    hases = {}

    fav_key = "fav/" + core_name
    fav = False

    for key in keys:
        if key == fav_key:
            fav = True
        elif key.startswith(has_key):
            bits = key[len(has_key):].split("/")
            if len(bits) >= 2:
                if bits[0] not in hases:
                    hases[bits[0]] = []
                hases[bits[0]].append(bits[1])
    
    rom_fav = fav
    fav_button.set_icon_tile(icon_lookup["heart-red" if fav else "heart-grey"])

    details = []
    for key, value in hases.items():
        details.append("\1" + key)
        details.append("\0" + wrap(", ".join(value), 38, 2))

    details_label.text = "\n".join(details)

switch_core("MENU")
switch_rom("", False)

had_point = False

tick_count = 0

def handle_button_press(id):
    global channel, rom_name, rom_fav, fav

    if id is None:
        return

    if id == "fav":
        if rom_name:
            if rom_fav:
                channel.write(["fav_del", "dbdel", "fav/" + core_name, rom_name])
                rom_fav = False
                fav_button.set_icon_tile(icon_lookup["heart-grey"])
            else:
                channel.write(["fav_put", "dbput", "fav/" + core_name, rom_name])
                rom_fav = True
                fav_button.set_icon_tile(icon_lookup["heart-red"])
    # elif id == "get":
    #     # channel.write(["date", "proc", "date"])
    #     channel.write(["dbget", "dbget", "TESTING"])
    # elif id == "put":
    #     # channel.write(["", "bproc", "./test.sh"])
    #     channel.write(["dbput", "dbput", "TESTING", "FROMPORTAL"])
    #     # channel.write(["dbput", "dbput", "TESTING", "TIME:" + str(time.time())])
    # elif id == "chk":
    #     channel.write(["dbchk", "dbchk", "TESTING", "FROMPORTAL"])
    # elif id == "chk2":
    #     channel.write(["dbchk", "dbchk", "TESTING", "FROMPORTALLL"])

while True:
    # if button1_pressed:
    #     if button1.value:
    #         #print("Button 1 released!")
    #         button1_pressed = False
    # else:
    #     if not button1.value:
    #         #print("Button 1 pressed!")
    #         # channel.write(["date", "proc", "date"])
    #         channel.write(["dbget", "dbget", "TESTING"])
    #         button1_pressed = True

    # if button2_pressed:
    #     if button2.value:
    #         #print("Button 2 released!")
    #         button2_pressed = False
    # else:
    #     if not button2.value:
    #         #print("Button 2 pressed!")
    #         # channel.write(["", "bproc", "./test.sh"])
    #         channel.write(["dbput", "dbput", "TESTING", "FROMPORTAL"])
    #         channel.write(["dbput", "dbput", "TESTING", "TIME:" + str(time.time())])
    #         button2_pressed = True

    if mcp is not None:
        for i in range(pin_count):
            value = pins[i].value
            if value != pin_states[i]:
                # print("Pin " + str(i) + " is " + str(value))
                pin_states[i] = value
                if not value:
                    kbd.press(*pin_keys[i])
                else:
                    kbd.release(*pin_keys[i])
    
    point = touch.touch_point
    if point:
        # Touch point needs to be rotated, flipped vertically, and halved
        point = (point[1] // 2), ((480 - point[0]) // 2)
        for button in buttons:
            if button.contains(point):
                button.selected = True
            elif button.selected:
                button.selected = False
        had_point = True
    elif had_point:
        for button in buttons:
            if button.selected:
                date_label.text = "button " + button.id + " was pressed"
                handle_button_press(button.id)
                button.selected = False

    commands = channel.read()
    for command in commands:
        print("RECEIVED: " + str(command))

        if len(command) > 1:
            if command[0] == "core":
                switch_core(command[1])
            elif command[0] == "rom":
                switch_rom(command[1])
            elif command[0] == "date":
                switch_date(command[1])
            elif command[0] == "dbget":
                switch_date("Got " + str(len(command) - 1) + " records")
            elif command[0] == "dbchk":
                switch_date("Got " + command[1])
            elif command[0] == "rom_keys":
                process_keys(command[1:])
    
    time.sleep(0.05)