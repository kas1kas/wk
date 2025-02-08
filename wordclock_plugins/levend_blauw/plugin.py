#v8.3 with global dimming
import os
import datetime
import random
import time
import wordclock_tools.wordclock_colors as wcc 

class plugin:

    def __init__(self, config):
        self.name = os.path.dirname(__file__).split('/')[-1]
        self.pretty_name = "Levend Blauw"
        self.description = "Blauw 8.3"

        self.bg_color = wcc.BLACK
        self.word_color = wcc.WHITE
        self.minute_color = wcc.WHITE
        self.purist = config.getboolean('plugin_time_default', 'purist')

    def run(self, wcd, wci):
        while True:
            for x in range(0,4):
                wcd.setColorByMinute(x, wcc.Color(0, 0, 0))
            now = datetime.datetime.now()
            taw_indices = wcd.taw.get_time(now, self.purist)
            wcd.setMinutes(now, self.minute_color)
            for t in range(random.randint(60,180)):
                wcd.setColorBy2DCoordinates(random.randint(0,10), random.randint(0,9), \
                    wcc.Color(random.randint(1,29),random.randint(2,31),random.randint(35,85)))
#                    wcc.Color(random.randint(29,69),random.randint(31,71),random.randint(105,245)))
                wcd.setColorBy1DCoordinates(taw_indices, self.word_color)    
                wcd.show()
            event = wci.waitForEvent(0.1)
            if event == wci.EVENT_BUTTON_RETURN \
                    or event == wci.EVENT_EXIT_PLUGIN \
                    or event == wci.EVENT_NEXT_PLUGIN_REQUESTED:
                return