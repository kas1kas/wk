#v5.1 with global dimming via readsensor with timer, no LUT: formula
#                 dimming starts in time_default with: wcd.readsensor()
import configparser
import time                                       #needed for tsl
from python_tsl2591 import tsl2591                #sensor
import fontdemo
import itertools
import logging
import os
from copy import deepcopy
from PIL import Image
from . import wiring
from time import sleep
from threading import Lock
import wordclock_plugins.time_default.time_bavarian as time_bavarian
import wordclock_plugins.time_default.time_dutch as time_dutch
import wordclock_plugins.time_default.time_english as time_english
import wordclock_plugins.time_default.time_french as time_french
import wordclock_plugins.time_default.time_german as time_german
import wordclock_plugins.time_default.time_german2 as time_german2
import wordclock_plugins.time_default.time_italian as time_italian
import wordclock_plugins.time_default.time_swabian as time_swabian
import wordclock_plugins.time_default.time_swabian2 as time_swabian2
import wordclock_plugins.time_default.time_swiss_german as time_swiss_german
import wordclock_plugins.time_default.time_swiss_german2 as time_swiss_german2
import wordclock_plugins.time_default.time_swedish as time_swedish
import wordclock_tools.wordclock_colors as wcc
import wordclock_tools.wordclock_screen as wordclock_screen
import colorsys
import threading

class wordclock_display:

    def __init__(self, config, wci):
        self.Helder=10
        self.wcl = wiring.wiring(config)
        self.wci = wci
        self.transition_cache_next = wordclock_screen.wordclock_screen(self)
        self.transition_cache_curr = wordclock_screen.wordclock_screen(self)

        self.config = config
        self.base_path = config.get('wordclock', 'base_path')
        self.mutex = Lock()
        self.setBrightness(config.getint('wordclock_display', 'brightness'))

        self.tsl = tsl2591()
#       lookup table for brightness, adapt to your liking
        self.inp = [0.1,  1,  2,  3,  4, 10,  15,  20,  30]    #lux in
        self.uit = [  3,  7, 14, 22, 29, 75, 120, 160, 180]    #brightness out

        if config.getboolean('wordclock', 'developer_mode'):
            import wordclock_tools.wordclock_strip_wx as wcs_wx
            self.strip = wcs_wx.WxStrip(wci)
        else:
            import wordclock_tools.wordclock_strip_neopixel as wcs_neo
            self.strip = wcs_neo.wordclock_strip_neopixel(self.wcl)

        if config.get('wordclock_display', 'default_font') == 'wcfont':
            self.default_font =  self.base_path + '/wcfont.ttf'
        else:
            self.default_font = os.path.join('/usr/share/fonts/truetype/freefont/', config.get('wordclock_display', 'default_font') + '.ttf')

        self.strip.begin()
        fgcolor = ''.join(config.get('plugin_time_default', 'default_fg_color'))

        if fgcolor == 'BLACK':
            self.default_fg_color = wcc.BLACK
        elif fgcolor == 'WHITE':
            self.default_fg_color = wcc.WHITE
        elif fgcolor == 'WWHITE':
            self.default_fg_color = wcc.WWHITE
        elif fgcolor == 'RED':
            self.default_fg_color = wcc.RED
        elif fgcolor == 'YELLOW':
            self.default_fg_color = wcc.YELLOW
        elif fgcolor == 'LIME':
            self.default_fg_color = wcc.LIME
        elif fgcolor == 'GREEN':
            self.default_fg_color = wcc.GREEN
        elif fgcolor == 'BLUE':
            self.default_fg_color = wcc.BLUE
        else:
            print('Could not detect default_fg_color: ' + fgcolor + '.')
            print('Choosing default: warm white')
            self.default_fg_color = wcc.WWHITE
        bgcolor = ''.join(config.get('plugin_time_default', 'default_bg_color')) 
        if bgcolor == 'BLACK':
            self.default_bg_color = wcc.BLACK
        elif bgcolor == 'WHITE':
            self.default_bg_color = wcc.WHITE
        elif bgcolor == 'WWHITE':
            self.default_bg_color = wcc.WWHITE
        elif bgcolor == 'RED':
            self.default_bg_color = wcc.RED
        elif bgcolor == 'YELLOW':
            self.default_bg_color = wcc.YELLOW
        elif bgcolor == 'LIME':
            self.default_bg_color = wcc.LIME
        elif bgcolor == 'GREEN':
            self.default_bg_color = wcc.GREEN
        elif bgcolor == 'BLUE':
            self.default_bg_color = wcc.BLUE
        else:
            print('Could not detect default_bg_color: ' + bgcolor + '.')
            print('Choosing default: black')
            self.default_bg_color = wcc.BLACK

        # For backward compatibility
        try:
            dialect = ''.join(config.get('wordclock_display', 'dialect'))
        except:
            # For backward compatibility
            dialect = ''.join(config.get('wordclock_display', 'language'))
        logging.info('Setting dialect to ' + dialect + '.')
        if dialect == 'bavarian':
            self.taw = time_bavarian.time_bavarian()
        elif dialect == 'dutch':
            self.taw = time_dutch.time_dutch()
        elif dialect == 'english':
            self.taw = time_english.time_english()
        elif dialect == 'french':
            self.taw = time_french.time_french()
        elif dialect == 'german':
            self.taw = time_german.time_german()
        elif dialect == 'german2':
            self.taw = time_german2.time_german2()
        elif dialect == 'italian':
            self.taw = time_italian.time_italian()
        elif dialect == 'swabian':
            self.taw = time_swabian.time_swabian()
        elif dialect == 'swabian2':
            self.taw = time_swabian2.time_swabian2()
        elif dialect == 'swiss_german':
            self.taw = time_swiss_german.time_swiss_german()
        elif dialect == 'swiss_german2':
            self.taw = time_swiss_german2.time_swiss_german2()
        elif language == 'swedish':
            self.taw = time_swedish.time_swedish()
        else:
            logging.error('Could not detect dialect: ' + dialect + '.')
            logging.info('Choosing default: dutch')
            self.taw = time_german.time_dutch()

        self.fps = self.config.getint('wordclock', 'animation_fps')

    def getBrightness(self):
        return self.brightness

    def setBrightness(self, brightness):
        self.brightness = max(min(brightness, 255), 0)

    def setBrightnessAndShow(self, brightness):
        with self.mutex:
            self.setBrightness(brightness)
        self.show()

    def setColorBy1DCoordinates(self, ledCoordinates, color):
        for i in ledCoordinates:
            self.setColorBy2DCoordinates(i % self.get_wca_width(), i // self.get_wca_width(), color)

    def setColorBy2DCoordinates(self, x, y, color):
        self.transition_cache_next.matrix[x][y] = color

    def setColorByMinute(self, min, color):
        if min >= 0 and min < 4:
            self.transition_cache_next.minutes[min] = color

    def get_wca_height(self):
        return self.wcl.WCA_HEIGHT

    def get_wca_width(self):
        return self.wcl.WCA_WIDTH

    def get_led_count(self):
        return self.wcl.LED_COUNT

    def dispRes(self):
        return str(self.wcl.WCA_WIDTH) + 'x' + str(self.wcl.WCA_HEIGHT)

    def setColorToAll(self, color, includeMinutes=True):
        for x in range(self.get_wca_width()):
            for y in range(self.get_wca_height()):
                self.transition_cache_next.matrix[x][y] = color
        if includeMinutes:
            for m in range(4):
                self.transition_cache_next.minutes[m] = color

    def setColorTemperatureToAll(self, temperature, includeMinutes=True):
        self.setColorToAll(wcc.color_temperature_to_rgb(temperature), includeMinutes)

    def resetDisplay(self):
        self.setColorToAll(wcc.BLACK, True)

    def showIcon(self, plugin, iconName):
        self.setImage(
            self.base_path + '/wordclock_plugins/' + plugin + '/icons/' + self.dispRes() + '/' + iconName + '.png')

    def setImage(self, absPathToImage):
        img = Image.open(absPathToImage)
        width, height = img.size
        for x in range(0, width):
            for y in range(0, height):
                rgb_img = img.convert('RGB')
                r, g, b = rgb_img.getpixel((x, y))
                self.setColorBy2DCoordinates(x, y, wcc.Color(r, g, b))
        self.show()

    def animate(self, plugin, animationName, fps=10, count=1, invert=False):
        animation_dir = self.base_path + '/wordclock_plugins/' + plugin + '/animations/' + self.dispRes() + '/' + animationName + '/'
        num_of_frames = len([file_count for file_count in os.listdir(animation_dir)])

        if invert:
            animation_range = list(range(num_of_frames - 1, -1, -1))
        else:
            animation_range = list(range(0, num_of_frames))

        for _ in range(count):
            for i in animation_range:
                self.setImage(animation_dir + str(i).zfill(3) + '.png')
                if self.wci.waitForExit(1.0 / fps):
                    return

    def showText(self, text, font=None, fg_color=None, bg_color=None, fps=10, count=1):
        if font is None:
            font = self.default_font
        if fg_color is None:
            fg_color = self.default_fg_color
        if bg_color is None:
            bg_color = self.default_bg_color

        text = '    ' + text + '    '
        fnt = fontdemo.Font(font, self.wcl.WCA_HEIGHT)
        text_width, text_height, text_max_descent = fnt.text_dimensions(text)
        text_as_pixel = fnt.render_text(text)
        for i in range(count):
            self.setColorToAll(bg_color, includeMinutes=True)
            render_range = self.wcl.WCA_WIDTH if self.wcl.WCA_WIDTH < text_width else text_width
            for y in range(text_height):
                for x in range(render_range):
                    self.setColorBy2DCoordinates(x, y, fg_color if text_as_pixel.pixels[y * text_width + x] else bg_color)
            self.show()
            if self.wci.waitForExit(0.5):
                return
            # Shift text from left to right to show all.
            for cur_offset in range(text_width - self.wcl.WCA_WIDTH + 1):
                for y in range(text_height):
                    for x in range(self.wcl.WCA_WIDTH):
                        self.setColorBy2DCoordinates(x, y, fg_color if text_as_pixel.pixels[y * text_width + x + cur_offset] else bg_color)
                self.show()
                if self.wci.waitForExit(1.0 / fps):
                    return

    def setMinutes(self, time, color):
        if time.minute % 5 != 0:
            for i in range(0, time.minute % 5):
                self.transition_cache_next.minutes[i] = color

    def apply_brightness(self, color):
        [h, s, v] = colorsys.rgb_to_hsv(color.r/255.0, color.g/255.0, color.b/255.0)
        [r, g, b] = colorsys.hsv_to_rgb(h, s, v * self.brightness/255.0)
        return wcc.Color(int(r*255.0), int(g*255.0), int(b*255.0))

    def render_transition_step(self, transition_cache_step):
        for x in range(self.get_wca_width()):
            for y in range(self.get_wca_height()):
                self.wcl.setColorBy2DCoordinates(self.strip, x, y, self.apply_brightness(transition_cache_step.matrix[x][y]))
        for m in range(4):
            self.wcl.setColorToMinute(self.strip, m + 1, self.apply_brightness(transition_cache_step.minutes[m]))
        self.strip.show()

    def show(self, animation = None, animation_speed = 5):
        animation = None if self.fps == 0 else animation
        if animation == 'typewriter':
            transition_cache = wordclock_screen.wordclock_screen(self)
            for y in range(self.get_wca_height()):
                for x in range(self.get_wca_width()):
                    if self.transition_cache_next.matrix[x][y] is not wcc.BLACK:
                        transition_cache.matrix[x][y] = self.transition_cache_next.matrix[x][y]
                        self.render_transition_step(transition_cache)
                        sleep(1.0/animation_speed)
            self.transition_cache_curr = deepcopy(self.transition_cache_next)
            self.render_transition_step(self.transition_cache_curr)
        elif animation == 'fadeOutIn':
            with self.mutex:
                brightness = self.getBrightness()
                while self.getBrightness() > 0:
                    self.setBrightness(self.getBrightness() - animation_speed)
                    self.render_transition_step(self.transition_cache_curr)
                    sleep(1.0/self.fps)
                self.transition_cache_curr = deepcopy(self.transition_cache_next)
                while self.getBrightness() < brightness:
                    self.setBrightness(self.getBrightness() + animation_speed)
                    self.render_transition_step(self.transition_cache_curr)
                    sleep(1.0/self.fps)
        else: # no animation
            self.transition_cache_curr = deepcopy(self.transition_cache_next)
            self.render_transition_step(self.transition_cache_curr)

    def readsensor(self):
        threading.Timer(4.0, self.readsensor).start()
#        self.setBrightness (BrightViaLUT(self))
        self.setBrightness (BrightViaFormula(self))

    def luxnow(self):                          #returns lux value of sensor
        return(readlux(self))

    def brightnow(self):                       #returns the average brightness
#        return(BrightViaLUT(self))
        return(BrightViaFormula(self))

def readlux(self):
  full, ir = self.tsl.get_full_luminosity()    # Read raw values (full spectrum and infared spectrum).
  return (self.tsl.calculate_lux(full, ir))    # Convert raw values to Lux.

def lut(self, inval):                          #change lookup table with inp[ , , , ] and uit[ , , , ]
    if inval <self.inp[0]:
      uitval = self.uit[0]
    elif inval <self.inp[1]:
      uitval = self.uit[1]
    elif inval <self.inp[2]:
      uitval = self.uit[2]
    elif inval <self.inp[3]:
      uitval = self.uit[3]
    elif inval <self.inp[4]:
      uitval = self.uit[4]
    elif inval <self.inp[5]:
      uitval = self.uit[5]
    elif inval <self.inp[6]:
      uitval = self.uit[6]
    elif inval <self.inp[7]:
      uitval = self.uit[7]
    elif inval <self.inp[8]:
      uitval = self.uit[8]
    else:
      uitval = 220
    return (uitval)

def BrightViaLUT(self):                        #get brightness via lookup table
    return (lut(self,readlux(self)))

def BrightViaFormula(self):
    br= int(pow(readlux(self),0.566)*self.Helder+0.4)
#    print(br)
    return(br)
