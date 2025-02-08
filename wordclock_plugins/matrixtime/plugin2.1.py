#v2.1 using global dimming
# Authored by Markus E.
# https://github.com/mrksngl

from datetime import datetime 
import logging
import os
import wordclock_tools.wordclock_colors as wcc
import random
import time
from datetime import datetime 

class plugin:

    def __init__(self, config):
        self.name = os.path.dirname(__file__).split('/')[-1]
        self.pretty_name = "Matrix time"
        self.description = "Glitches in the fabric"
        self.purist = config.getboolean('plugin_time_default', 'purist')
        self.bg_color = wcc.BLACK  # default background color
        self.word_color = wcc.WHITE  # default word color
        self.minute_color = wcc.WHITE  # default minute color
        self.threshold = 0.9
        self.brightness = 30 
           
        # Colors from black to green (and a bit gray-ish)
        self.colors = []
        for i in range(0, 8):
            self.colors.append(wcc.Color(0, int(255.0 / 10 * i), 0))
        self.colors.append(wcc.Color(50, 204, 30))
        self.colors.append(wcc.Color(50, 230, 30))
        self.colors.append(wcc.Color(80, 255, 60))
        

    def run(self, wcd, wci):
        rain = [20 for _ in range(0, 11)]
        while True:
            try:
                if datetime.datetime.now() > wcc.scrolldatetime:
                    wcd.showText(wcc.scrolltext)
                    wcc.scrolldatetime = wcc.scrolldatetime + datetime.timedelta(seconds = wcc.scrollrepeat)
                    print("Next scroll: ",wcc.scrolldatetime)
            except:
                pass

            if not(wcc.scrollactive):
                wcd.setColorToAll(self.bg_color, includeMinutes=True)
                now = datetime.now()
                taw_indices = wcd.taw.get_time(now, self.purist)
 
                for x, y in enumerate(rain):
                    if y == 20:
                        # reset y coordinate randomly
                        if random.random() > self.threshold:
                            rain[x] = 0
                    else:
                        # simple alpha blending using our predefined colors
                        y0 = max(y - 10, 0)
                        y1 = min(9, y)
                        ci = y0 - (y - 10)
                        for yi, yn in enumerate(range(y0, y1 + 1)):
                            color = self.colors[ci + yi]
                            wcd.setColorBy2DCoordinates(x, yn, color)
                        # advance y coordinate
                        rain[x] = y + 1
                wcd.setColorBy1DCoordinates(taw_indices, self.word_color)
                wcd.setMinutes(now, self.minute_color)
                wcd.show()

            event = wci.waitForEvent(0.1)
            if event == wci.EVENT_BUTTON_RETURN \
                    or event == wci.EVENT_EXIT_PLUGIN \
                    or event == wci.EVENT_NEXT_PLUGIN_REQUESTED:
                return
            elif event == wci.EVENT_BUTTON_LEFT:
                self.threshold = min(0.95, self.threshold + 0.05)
            elif event == wci.EVENT_BUTTON_RIGHT:
                self.threshold = max(0.7, self.threshold - 0.05)
