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
from adafruit_mcp230xx.mcp23008 import MCP23008
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_text.label import Label
from channel import Channel
from button import Button

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

SCALE = 2

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

display = board.DISPLAY
display.rotation = 90

root = displayio.Group(max_size=10, scale=SCALE)
display.show(root)

normal_font = bitmap_font.load_font("/fonts/lemon.bdf")
normal_font.load_glyphs(b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.:/! ')

def load_icon(path):
    icon = adafruit_imageload.load(path, bitmap=displayio.Bitmap, palette=displayio.Palette)
    icon[1].make_transparent(0)
    return icon

rom_icon = load_icon("/icons/cartridge.bmp")
heart_on_icon = load_icon("/icons/heart-red.bmp")
heart_off_icon = load_icon("/icons/heart-grey.bmp")

header = displayio.Group(max_size=10)
root.append(header)

core_label = Label(normal_font, text="", max_glyphs=32, x=20, y=7, color=WHITE)
header.append(core_label)

rom_icon = adafruit_imageload.load("/icons/cartridge.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
rom_sprite = displayio.TileGrid(rom_icon[0], pixel_shader=rom_icon[1], x=0, y=18)
header.append(rom_sprite)

rom_label = Label(normal_font, text="", max_glyphs=32, x=20, y=25, color=WHITE)
header.append(rom_label)

rule_bitmap = displayio.Bitmap(160, 1, 1)
rule_palette = displayio.Palette(1)
rule_palette[0] = GREY
rule_sprite = displayio.TileGrid(rule_bitmap, pixel_shader=rule_palette, x=0, y=35)
header.append(rule_sprite)

body = displayio.Group(max_size=20)
root.append(body)

date_label = Label(normal_font, text="", max_glyphs=32, x=0, y=41, color=WHITE)
body.append(date_label)

fav = Button(
    id="fav",
    x=0,
    y=52,
    width=78,
    height=22,
    style=Button.RECT,
    fill_color=BUTTON1,
    selected_fill=BUTTON2,
    outline_color=WHITE,
    selected_outline=WHITE,
    label="Favorite",
    label_font=normal_font,
    label_color=WHITE,
    selected_label=WHITE,
    icon=heart_off_icon,
)
body.append(fav.group)

buttons = [fav]

# try:
#     dbf = open("mydb", "r+b")
# except OSError:
#     dbf = open("mydb", "w+b")

# db = btree.open(f)

# # The keys you add will be sorted internally in the database
# db[b"3"] = b"three"
# db[b"1"] = b"one"
# db[b"2"] = b"two"

# # Assume that any changes are cached in memory unless
# # explicitly flushed (or database closed). Flush database
# # at the end of each "transaction".
# db.flush()

# # Prints b'two'
# print(db[b"2"])

# # Iterate over sorted keys in the database, starting from b"2"
# # until the end of the database, returning only values.
# # Mind that arguments passed to values() method are *key* values.
# # Prints:
# #   b'two'
# #   b'three'
# for word in db.values(b"2"):
#     print(word)

# del db[b"2"]

# # No longer true, prints False
# print(b"2" in db)

# # Prints:
# #  b"1"
# #  b"3"
# for key in db:
#     print(key)

# db.close()

# # Don't forget to close the underlying stream!
# dbf.close()

# end_of_record = bytes([0x7f, 0x45, 0x4c, 0x46, 0x01, 0x01, 0x01, 0x00])

# try:
#     if hasattr(board, "TFT_BACKLIGHT"):
#         backlight = pwmio.PWMOut(
#             board.TFT_BACKLIGHT
#         )  # pylint: disable=no-member
#     elif hasattr(board, "TFT_LITE"):
#         self._backlight = pwmio.PWMOut(
#             board.TFT_LITE
#         )  # pylint: disable=no-member
# except ValueError:
#     self._backlight = None
# self.set_backlight(1.0)  # turn on backlight

## os.stat("/pyportal_startup.bmp")
## for i in range(100, -1, -1):  # dim down
##     self.set_backlight(i / 100)
##     time.sleep(0.005)

# button1 = digitalio.DigitalInOut(board.D3)
# button1.direction = digitalio.Direction.INPUT
# button1.pull = digitalio.Pull.UP

# button2 = digitalio.DigitalInOut(board.D4)
# button2.direction = digitalio.Direction.INPUT
# button2.pull = digitalio.Pull.UP

touch = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL,
    board.TOUCH_XR,
    board.TOUCH_YD,
    board.TOUCH_YU,
    calibration=((8000, 60000), (9000, 55000)),
    size=(480, 320),
)

channel = Channel(usb_cdc.serials[1])

# if True:
#     display = board.DISPLAY

#     root = displayio.Group(max_size=15)
#     display.show(root)

#     bg_file = open("pyportal_startup.bmp", "rb")
#     background = displayio.OnDiskBitmap(bg_file)
#     bg_sprite = displayio.TileGrid(
#         background,
#         pixel_shader=displayio.ColorConverter(),
#         x=0,
#         y=0,
#     )
#     root.append(bg_sprite)

# self.set_background("/pyportal_startup.bmp")
# try:
#     self.display.refresh(target_frames_per_second=60)
# except AttributeError:
#     self.display.wait_for_frame()
# for i in range(100):  # dim up
#     self.set_backlight(i / 100)
#     time.sleep(0.005)
# time.sleep(2)

core_name = "Menu"
rom_name = None
rom_fav = False
core_sprite = None
core_icon = None

def switch_core(new_name):
    global core_name, header, core_label, core_sprite, core_icon

    core_name = new_name
    core_label.text = core_name[:32] or "(none)"
    
    if core_sprite is not None:
        header.remove(core_sprite)
        del core_sprite
        del core_icon
        gc.collect()
    
    icon_path = "/icons/cores/" + core_name + ".bmp"
    if not file_exists(icon_path):
        icon_path = "/icons/generic.bmp"

    core_icon = adafruit_imageload.load(icon_path, bitmap=displayio.Bitmap, palette=displayio.Palette)
    core_sprite = displayio.TileGrid(core_icon[0], pixel_shader=core_icon[1], x=0, y=0)
    header.append(core_sprite)

def switch_rom(new_name, fav_check=True):
    global channel, core_name, rom_name, rom_label

    rom_name = new_name
    rom_label.text = rom_name[:32] or "(none)"

    if core_name and rom_name and fav_check:
        channel.write(["favchk", "dbchk", "fav/" + core_name, rom_name])

def switch_date(date):
    global date_label

    date_label.text = date[:32]

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
                channel.write(["favdel", "dbdel", "fav/" + core_name, rom_name])
                rom_fav = False
                fav.icon = heart_off_icon
            else:
                channel.write(["favput", "dbput", "fav/" + core_name, rom_name])
                rom_fav = True
                fav.icon = heart_on_icon
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
        # Touch point needs to be rotated, flipped vertically, and scaled by half
        point = (int(point[1] / SCALE), int((480 - point[0]) / SCALE))
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
            elif command[0] == "favchk":
                switch_date("Fav " + command[1])
                rom_fav = (command[1] == "1")
                fav.icon = heart_on_icon if rom_fav else heart_off_icon
    
    # tick_count += 1
    # if tick_count == 80:
    #     print("Tick")
    #     tick_count = 0
    
    time.sleep(0.05)

# # Set up where we'll be fetching data from
# DATA_SOURCE = "https://www.adafruit.com/api/quotes.php"
# QUOTE_LOCATION = [0, 'text']
# AUTHOR_LOCATION = [0, 'author']

# # the current working directory (where this file is)
# cwd = ("/"+__file__).rsplit('/', 1)[0]
# pyportal = PyPortal(url=DATA_SOURCE,
#                     json_path=(QUOTE_LOCATION, AUTHOR_LOCATION),
#                     status_neopixel=board.NEOPIXEL,
#                     default_bg=cwd+"/quote_background.bmp",
#                     text_font=cwd+"/fonts/Arial-ItalicMT-23.bdf",
#                     text_position=((20, 160),  # quote location
#                                    (5, 280)), # author location
#                     text_color=(0xFFFFFF,  # quote text color
#                                 0x8080FF), # author text color
#                     text_wrap=(40, # characters to wrap for quote
#                                0), # no wrap for author
#                     text_maxlen=(180, 30), # max text size for quote & author
#                    )

# # speed up projects with lots of text by preloading the font!
# pyportal.preload_font()

# while True:
#     try:
#         value = pyportal.fetch()
#         print("Response is", value)
#     except (ValueError, RuntimeError) as e:
#         print("Some error occured, retrying! -", e)
#     time.sleep(60)