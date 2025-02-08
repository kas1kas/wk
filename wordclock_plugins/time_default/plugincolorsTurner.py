# Kas v7.3
from datetime import datetime
import os
import wordclock_tools.wordclock_colors as wcc
import configparser

class plugin:
    def __init__(self, config):
        self.name = os.path.dirname(__file__).split('/')[-1]
        self.pretty_name = "Time"
        self.description = "tik tok 7.3"
        self.purist = False

        self.brightness = config.getint('wordclock_display', 'brightness')
        print(self.name + ":  max bright: ", self.brightness)

        self.Rainbow = False
        self.defWcolor = wcc.Color(255, 31, 23)
        self.defMcolor = wcc.Color(255, 31, 23)
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

    def run(self, wcd, wci):
        while True:
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
            if self.Sensor:
              wcd.dimbright()
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
                #after right click in browser, refresh and the values will show on screen
                self.description = ("Purist: %s,  Lux: %6.3f, Brightness: %3d"  %(self.purist,wcd.luxnow(), wcd.brightnow()) )
                print ("Purist: %s,  Lux: %6.3f, Brightness: %3d"  %(self.purist,wcd.luxnow(), wcd.brightnow()) )

                self.Rainbow = False
                self.word_color = self.defWcolor
                self.minute_color = self.defMcolor
                self.bg_color = self.defBcolor

