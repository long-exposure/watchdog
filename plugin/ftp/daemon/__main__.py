# Watchdog - Building supervision with Raspberry Pi
# (C)2017 - Norbert Huffschmid

# email plugin

import ConfigParser
import dbus
import dbus.mainloop.glib
import ftplib
import gobject
import logging
import os
import signal
import subprocess

logger = logging.getLogger('watchdog.plugin.ftp') # __name__ is __main__

CONFIG_FILE = '/etc/watchdog.conf'
CAPTURE_IMAGE_QUEUE = '/tmp/captures-ftp.list'

class FtpPlugin(object):

    def run(self):

        try:
                
            logger.info('Starting ftp plugin ...')
            
            # init dbus stuff
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            mainloop = gobject.MainLoop()
            gobject.threads_init()
            dbus.mainloop.glib.threads_init()
            
            # register for dbus signals
            bus = dbus.SystemBus()
            motionProxy = dbus.Interface(bus.get_object('net.longexposure.watchdog', '/Motion'), 'net.longexposure.watchdog')
            motionProxy.connect_to_signal('event_started', self._event_started)
            motionProxy.connect_to_signal('event_ended', self._event_ended)
            motionProxy.connect_to_signal('picture_saved', self._picture_saved)
            
            # register for SIGTERM
            signal.signal(signal.SIGTERM, lambda signum, frame: mainloop.quit())
                    
            mainloop.run()
    
            logger.debug('FTP plugin terminated.')

        except Exception, e:
            logger.error(str(e))


    def _event_started(self):
        logger.info('Received event_started signal')
        self._upload()


    def _event_ended(self):
        logger.info('Received event_ended signal')
        if (os.path.exists(CAPTURE_IMAGE_QUEUE)):
            self._upload()
        else:
            logger.debug('No further images to send')


    def _picture_saved(self, path):
        logger.debug('Received picture_saved signal: ' + path)
        with open(CAPTURE_IMAGE_QUEUE, 'a') as file:
            file.write(path + '\n')

        
    def _upload(self):
    
        try:
            with open(CAPTURE_IMAGE_QUEUE,'r') as file:
                captures = file.readlines()

            config = ConfigParser.SafeConfigParser()
            config.read(CONFIG_FILE)
          
            if (config.getboolean('ftp', 'active') == True):
                logger.info('Uploading images to ' + config.get('ftp', 'host') + ' ...')
                ftp = ftplib.FTP_TLS(config.get('ftp', 'host'))
                ftp.login(config.get('ftp', 'user'), config.get('ftp', 'password'))
                ftp.cwd(config.get('ftp', 'directory').strip('/'))
                for path in captures:
                    filename = os.path.basename(path.strip())
                    ftp.storbinary("STOR " + filename, open(path.strip(), "rb"))
                ftp.quit()
                logger.info('Upload of ' + str(len(captures)) + ' files completed.')                
            else:
                logger.debug('Uploading of captures is deactivated.')
          
            os.remove(CAPTURE_IMAGE_QUEUE)

        except Exception, e:
            logger.error(str(e))


if __name__ == '__main__':
    FtpPlugin().run()
