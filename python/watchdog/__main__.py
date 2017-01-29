# Watchdog - Building supervision with Raspberry Pi
# (C)2016 - Norbert Huffschmid

# Main program

import dbus
import dbus.mainloop.glib
import dbus.service
import gobject
import logging
import signal

from watchdog.motion_proxy import MotionProxy
from watchdog.plugin_proxy import PluginProxy

logger = logging.getLogger('watchdog') # __name__ is __main__


class Watchdog(object):

    def run(self):
        
        try:
            
            logger.info('Starting watchdog ...')
            
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

            MotionProxy()
            PluginProxy()
            
            self._loop = gobject.MainLoop()
            gobject.threads_init()
            dbus.mainloop.glib.threads_init()

            # register for SIGTERM
            signal.signal(signal.SIGTERM, lambda signum, frame: self._loop.quit())

            self._loop.run()
            
            logger.info('Watchdog terminated.')

        except Exception, e:
            logger.error(str(e))


if __name__ == '__main__':
    Watchdog().run()
