# Watchdog - Building supervision with Raspberry Pi
# (C)2016 - Norbert Huffschmid

# Main program

import dbus
import dbus.service
import logging
import sys
import time

DELAY_TIME = 30

logger = logging.getLogger('watchdog.motion_proxy')


class MotionProxy(dbus.service.Object):

    def __init__(self):
        try:
            logger.debug('Initiating MotionProxy')
            busName = dbus.service.BusName('net.longexposure.watchdog', bus = dbus.SystemBus())
            dbus.service.Object.__init__(self, busName, '/Motion')
        except Exception, e:
            logger.error(str(e))


    @dbus.service.method(dbus_interface='net.longexposure.watchdog', in_signature='', out_signature='')
    def handle_event_started(self):
        self.event_started()


    @dbus.service.signal(dbus_interface='net.longexposure.watchdog', signature='')
    def event_started(self):
        logger.debug('Emit dbus signal event_started')
        pass


    @dbus.service.method(dbus_interface='net.longexposure.watchdog', in_signature='', out_signature='')
    def handle_event_ended(self):
        self.event_ended()


    @dbus.service.signal(dbus_interface='net.longexposure.watchdog', signature='')
    def event_ended(self):
        logger.debug('Emit dbus signal event_ended')
        pass


    @dbus.service.method(dbus_interface='net.longexposure.watchdog', in_signature='s', out_signature='')
    def handle_picture_saved(self, path):
        if (not path.endswith('snapshot.jpg')):
            self.picture_saved(path)


    @dbus.service.signal(dbus_interface='net.longexposure.watchdog', signature='s')
    def picture_saved(self, path):
        logger.debug('Emit dbus signal picture_saved: ' + path)
        pass


if __name__ == "__main__":
    
    try:

        bus = dbus.SystemBus()
        motionProxy = dbus.Interface(bus.get_object('net.longexposure.watchdog', '/Motion'), 'net.longexposure.watchdog')
        
        if (sys.argv[1] == 'event_start'):
            time.sleep(DELAY_TIME)
            motionProxy.handle_event_started()
        elif (sys.argv[1] == 'event_end'):
            time.sleep(DELAY_TIME)
            motionProxy.handle_event_ended()
        elif (sys.argv[1] == 'picture_save'):
            if (len(sys.argv) <= 2):
                logger.error('Missing file argument')
                sys.exit(1)
            motionProxy.handle_picture_saved(sys.argv[2])
        else:
            logger.error('Invalid command line argument: ' + sys.argv[1])
            sys.exit(1)
    
    except Exception, e:
        logger.error(str(e))
