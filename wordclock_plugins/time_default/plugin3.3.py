# Kas v3.3
from datetime import datetime
import time                                        #needed for tsl
import os
import wordclock_tools.wordclock_colors as wcc
from python_tsl2591 import tsl2591                #sensor
import configparser

class plugin:
    def __init__(self, config):
        self.name = os.path.dirname(__file__).split('/')[-1]
        self.pretty_name = "Time"
        self.description = "tik tok"
        self.purist = False

        self.brightness = config.getint('wordclock_display', 'brightness')
        print(self.name + ":  max bright: ", self.brightness)

        self.Rainbow = False
        self.defWcolor = wcc.ORANGE
        self.defMcolor = wcc.RED
        self.defBcolor = wcc.BLACK
        self.word_color = self.defWcolor
        self.minute_color = self.defMcolor
        self.bg_color = self.defBcolor
        self.rb_pos = 0

        try:
            self.use_brightness_sensor = config.getboolean('wordclock_display', 'use_brightness_sensor')
        except:
            self.use_brightness_sensor = False
        print((self.name + ' : Using brigtness sensor : ' + str(self.use_brightness_sensor)))
        self.Sensor = self.use_brightness_sensor
        if self.Sensor:
            self.tsl = tsl2591()  # initialize
        self.prevTime = datetime.now()
        self.BrightI = self.brightness
        self.jitter = 5

    def lux(self):
      full, ir = self.tsl.get_full_luminosity()    # Read raw values (full spectrum and infared spectrum).
      return (self.tsl.calculate_lux(full, ir))    # Convert raw values to Lux.

    def lut(self, inval):
        if inval <0.1:
          uitval = 3
#       elif inval <1:
#         uitval = 20
        elif inval <2:
          uitval = 30
        elif inval <3:
          uitval = 40
        elif inval <5:
          uitval = 80
        elif inval <10:
          uitval = 150
        else:
          uitval = 250
        return (uitval)

    def run(self, wcd, wci):
        newBrightness = self.brightness
        self.prevTime = datetime.now()
        self.BrightI = self.brightness

        while True:
            if self.Sensor:
                BrightN = self.lut(self.lux())
                if BrightN != self.BrightI:                  #delay (jitter) to prevent flashing
                    timed = datetime.now() - self.prevTime
                    sec = timed.total_seconds()
                    #print (BrightN, sec)
                    if sec > self.jitter:
                        newBrightness = BrightN
                        self.prevTime = datetime.now()
                        self.BrightI = BrightN
                        #print("We have a new brightness setting")

            # BEGIN: Rainbow generation as done in rpi_ws281x strandtest example! Thanks to Tony DiCola for providing :)
            if self.Rainbow:
                if self.rb_pos < 85:
                    self.word_color = self.minute_color = wcc.Color(3 * self.rb_pos, 255 - 3 * self.rb_pos, 0)
                elif self.rb_pos < 170:
                    self.word_color = self.minute_color = wcc.Color(255 - 3 * (self.rb_pos - 85), 0, 3 * (self.rb_pos - 85))
                else:
                    self.word_color = self.minute_color = wcc.Color(0, 3 * (self.rb_pos - 170), 255 - 3 * (self.rb_pos - 170))

            wcd.setColorToAll(self.bg_color, includeMinutes=True)  #do not change to False

            now = datetime.now()
            taw_indices = wcd.taw.get_time(now, self.purist)
            wcd.setColorBy1DCoordinates(taw_indices, self.word_color)
            wcd.setMinutes(now, self.minute_color)
            wcd.setBrightness(newBrightness)
            wcd.show()
            self.rb_pos += 1
            if self.rb_pos == 256: self.rb_pos = 0

            event = wci.waitForEvent(0.1)
            if event == wci.EVENT_BUTTON_RETURN \
                    or event == wci.EVENT_EXIT_PLUGIN \
                    or event == wci.EVENT_NEXT_PLUGIN_REQUESTED:
                return
            elif event == wci.EVENT_BUTTON_LEFT:
                if self.Rainbow:
                    self.Rainbow = False
                else:
                    self.Rainbow = True
                print (self.name + " rainbow ", self.Rainbow)
            elif event == wci.EVENT_BUTTON_RIGHT:
                if self.purist:
                    self.purist = False
                else:
                    self.purist = True
                print (self.name + " purist ", self.purist)

                self.Rainbow = False
                self.word_color = self.defWcolor
                self.minute_color = self.defMcolor
                self.bg_color = self.defBcolor

