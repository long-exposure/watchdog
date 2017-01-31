# Watchdog - Building supervision with Raspberry Pi
# (C)2017 - Norbert Huffschmid

# email plugin

import ConfigParser
import dbus
import dbus.mainloop.glib
import gobject
import logging
import os
import signal
import subprocess

logger = logging.getLogger('watchdog.plugin.email') # __name__ is __main__

CONFIG_FILE = '/etc/watchdog.conf'
CAPTURE_IMAGE_QUEUE = '/tmp/captures-email.list'

class EmailPlugin(object):

    def run(self):

        try:
                
            logger.info('Starting email plugin ...')
            
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
    
            logger.debug('Email plugin terminated.')

        except Exception, e:
            logger.error(str(e))


    def _event_started(self):
        logger.info('Received event_started signal')
        self._send_email()


    def _event_ended(self):
        logger.info('Received event_ended signal')
        if (os.path.exists(CAPTURE_IMAGE_QUEUE)):
            self._send_email()
        else:
            logger.debug('No further images to send')


    def _picture_saved(self, path):
        logger.debug('Received picture_saved signal: ' + path)
        with open(CAPTURE_IMAGE_QUEUE, 'a') as file:
            file.write(path + '\n')

        
    def _send_email(self):
    
        try:
            with open(CAPTURE_IMAGE_QUEUE,'r') as file:
                captures = file.readlines()

            config = ConfigParser.SafeConfigParser()
            config.read(CONFIG_FILE)
          
            if (config.get('email', 'active') == 'true'):
                 
                command = 'sendemail'
                command += ' -f ' + config.get('email', 'user')
                command += ' -t ' + config.get('email', 'recipient')
                command += ' -u "' + config.get('email', 'subject') + '"'
                command += ' -m "' + config.get('email', 'message') + '"'
                command += ' -s ' + config.get('email', 'smtp')
                command += ' -xu ' + config.get('email', 'user')
                command += ' -xp ' + config.get('email', 'password')
            
                if (config.get('email', 'attach') == 'true'):
                    command += ' -a'
                    for file in captures:
                        command += ' ' + file.strip()
        
                logger.info('Sending email to: ' + config.get('email', 'recipient'))
                
                subprocess.Popen(command, shell=True)
                
            else:
                logger.debug('Sending of email is deactivated.')
          
            os.remove(CAPTURE_IMAGE_QUEUE)

        except Exception, e:
            logger.error(str(e))


if __name__ == '__main__':
    EmailPlugin().run()
