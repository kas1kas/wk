#v1.3
import os
import time


class plugin:
    """
    A class to restart the RPI
    """

    def __init__(self, config):
        """
        Initializations for the startup of the current wordclock plugin
        """
        # Get plugin name (according to the folder, it is contained in)
        self.name = os.path.dirname(__file__).split('/')[-1]
        self.pretty_name = "Restart in English"
        self.description = "Use the English letterplate"

    def run(self, wcd, wci):
        """
        Restart wordclock
        """
        wcd.showText("English...    ")
        wcd.showIcon(plugin=self.name, iconName='logo')
        os.system("sed -i 's/.*dialect =.*/dialect = english/' /home/pi/rpi_wordclock/wordclock_config/wordclock_config.cfg")
        os.system("sed -i 's/.*language =.*/language = english/' /home/pi/rpi_wordclock/wordclock_config/wordclock_config.cfg")
        time.sleep(1) 
        os.system("sudo reboot")
        time.sleep(10)
        return
