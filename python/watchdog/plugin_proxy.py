# Watchdog - Building supervision with Raspberry Pi
# (C)2016 - Norbert Huffschmid

# Plugin install/uninstall proxy

import dbus
import dbus.service
import logging
import os
import sys

logger = logging.getLogger('watchdog.plugin_proxy')


class PluginProxy(dbus.service.Object):

    def __init__(self):
        try:
            logger.debug('Initiating PluginProxy')
            busName = dbus.service.BusName('net.longexposure.watchdog', bus = dbus.SystemBus())
            dbus.service.Object.__init__(self, busName, '/Plugin')
        except Exception, e:
            logger.error(str(e))


    @dbus.service.method(dbus_interface='net.longexposure.watchdog', in_signature='s', out_signature='')
    def add_daemon(self, daemon):
        initScriptFile = '/etc/init.d/' + daemon
        if (os.path.exists(initScriptFile)):
            logger.debug('Activating and starting daemon ' + daemon + ' ...')
            os.system('update-rc.d ' + daemon + ' defaults')
            os.system('/etc/init.d/' + daemon + ' start')
            logger.debug('Daemon ' + daemon + ' started.')


    @dbus.service.method(dbus_interface='net.longexposure.watchdog', in_signature='s', out_signature='')
    def remove_daemon(self, daemon):
        initScriptFile = '/etc/init.d/' + daemon
        if (os.path.exists(initScriptFile)):
            logger.debug('Stopping and removing daemon ' + daemon + ' ...')
            os.system('/etc/init.d/' + daemon + ' stop')
            os.system('update-rc.d ' + daemon + ' remove')            
            logger.debug('Daemon ' + daemon + ' removed.')


if __name__ == "__main__":
    
    try:

        bus = dbus.SystemBus()
        pluginProxy = dbus.Interface(bus.get_object('net.longexposure.watchdog', '/Plugin'), 'net.longexposure.watchdog')
        
        if (sys.argv[1] == 'add'):
            if (len(sys.argv) <= 2):
                logger.error('Missing daemon argument')
                sys.exit(1)
            pluginProxy.add_daemon(sys.argv[2])
        elif (sys.argv[1] == 'remove'):
            if (len(sys.argv) <= 2):
                logger.error('Missing daemon argument')
                sys.exit(1)
            pluginProxy.remove_daemon(sys.argv[2])
        else:
            logger.error('Invalid command line argument: ' + sys.argv[1])
            sys.exit(1)
    
    except Exception, e:
        logger.error(str(e))
