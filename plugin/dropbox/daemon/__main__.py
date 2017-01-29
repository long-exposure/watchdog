# Watchdog - Building supervision with Raspberry Pi
# (C)2016 - Norbert Huffschmid

# dropbox plugin

import ConfigParser
import dbus
import dbus.mainloop.glib
import dbus.service
import dropbox
import gobject
import logging
import Queue
import os
import signal
import subprocess

logger = logging.getLogger('watchdog.plugin.dropbox') # __name__ is __main__

CONFIG_FILE = '/etc/watchdog.conf'

class DropboxPlugin(dbus.service.Object):

    def run(self):

        try:
                
            logger.info('Starting dropbox plugin ...')

            self._capturesQueue = Queue.Queue()

            # init dbus stuff
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            mainloop = gobject.MainLoop()
            gobject.threads_init()
            dbus.mainloop.glib.threads_init()
            
            # register for watchdog dbus signals
            bus = dbus.SystemBus()
            motionProxy = dbus.Interface(bus.get_object('net.longexposure.watchdog', '/Motion'), 'net.longexposure.watchdog')
            motionProxy.connect_to_signal('event_started', self._event_started)
            motionProxy.connect_to_signal('event_ended', self._event_ended)
            motionProxy.connect_to_signal('picture_saved', self._picture_saved)
            
            # provide dropbox dbus services
            dropboxBus = dbus.service.BusName('net.longexposure.watchdog.plugin.dropbox', bus)
            dbus.service.Object.__init__(self, dropboxBus, '/')
            
            # init dropbox api
            self._token = self._read_token_from_config()
            self._flow = None
            
            # register for SIGTERM
            signal.signal(signal.SIGTERM, lambda signum, frame: mainloop.quit())
                    
            mainloop.run()
    
            logger.debug('Dropbox plugin terminated.')

        except Exception, e:
            logger.error(str(e))


    @dbus.service.method(dbus_interface='net.longexposure.watchdog.plugin.dropbox',
                         in_signature='', out_signature='a{sv}')
    def get_status(self):
        try:

            logger.debug('Starting to determine status ...')
            self._token = self._read_token_from_config()
            if (self._token == None):
                status = dbus.Dictionary({'IsConnected': False, 'Info': 'Not Connected', 'Files': 0}, signature='sv')
            else:
                dbx = dropbox.Dropbox(self._token)
                displayName = dbx.users_get_current_account().name.display_name;
                fileCount = len(dbx.files_list_folder('').entries)
                status = dbus.Dictionary({'IsConnected': True, 'Info': 'Connected: ' + displayName, 'Files': fileCount},
                                         signature='sv')
            logger.debug('Dropbox status: ' + str(status))
            return status

        except dropbox.exceptions.AuthError, e:
            logger.error(str(e))
            self._remove_token_from_config()
            self._token = None
            status = dbus.Dictionary({'IsConnected': False, 'Info': 'Not Connected'}, signature='sv')
            return status

        except Exception, e:
            logger.error(str(e))
            status = dbus.Dictionary({'IsConnected': False, 'Info': 'Not Connected'}, signature='sv')
            return status


    @dbus.service.method(dbus_interface='net.longexposure.watchdog.plugin.dropbox',
                         in_signature='', out_signature='s')
    def get_authorization_url(self):
        try:
            logger.debug('Starting to determine authorization url ...')
            self._flow = dropbox.DropboxOAuth2FlowNoRedirect('5qxoh57bhigtes8', 'mvvcxya3ifpjg83')
            authorize_url = self._flow.start()
            logger.debug('Url: ' + authorize_url)
            return authorize_url

        except Exception, e:
            logger.error(str(e))
            return 'ERROR: Cannot determine authorization url (see logfile for details)'


    @dbus.service.method(dbus_interface='net.longexposure.watchdog.plugin.dropbox',
                         in_signature='s', out_signature='b')
    def authorize(self, code):
        try:
            if (self._flow == None):
                logger.debug('No authorization flow started! Skip authorization request with code ' + code)
                return False
            
            logger.debug('Trying to authorize with code ' + code + ' ...')
            access_token = self._flow.finish(code.strip()).access_token # Example in dropbox api docu is wrong!!!
            logger.debug('Received access token: ' + access_token)
            
            self._write_token_to_config(access_token)

            self._token = access_token
            self._flow = None

            return True

        except Exception, e:
            logger.error(str(e))
            return False


    @dbus.service.method(dbus_interface='net.longexposure.watchdog.plugin.dropbox',
                         in_signature='', out_signature='')
    def disconnect(self):
        try:
            logger.debug('Starting to disconnect ...')
            self._remove_token_from_config()
            self._token = None

        except Exception, e:
            logger.error(str(e))


    @dbus.service.method(dbus_interface='net.longexposure.watchdog.plugin.dropbox',
                         in_signature='', out_signature='')
    def delete_files(self):
        try:
            logger.debug('Starting to delete all files ...')
            dbx = dropbox.Dropbox(self._token)
            for entry in dbx.files_list_folder('').entries:
                dbx.files_delete('/' + entry.name)

        except Exception, e:
            logger.error(str(e))


    def _read_token_from_config(self):
        logger.debug('Trying to read token from config ...')
        config = ConfigParser.SafeConfigParser()
        config.read(CONFIG_FILE)
        if (config.has_option('dropbox', 'access_token')):
            token = config.get('dropbox', 'access_token')
            logger.debug('Token read from config: ' + token)
        else:
            token = None
            logger.debug('No token found in config')
        return token
        

    def _write_token_to_config(self, token):
        logger.debug('Trying to store token in config')
        config = ConfigParser.SafeConfigParser()
        config.read(CONFIG_FILE)
        config.set('dropbox', 'access_token', token)
        with open(CONFIG_FILE, 'wb') as configfile:
            config.write(configfile)
        logger.debug('Config file updated successfully')
        

    def _remove_token_from_config(self):
        logger.debug('Trying to remove token from config')
        config = ConfigParser.SafeConfigParser()
        config.read(CONFIG_FILE)
        config.remove_option('dropbox', 'access_token')
        with open(CONFIG_FILE, 'wb') as configfile:
            config.write(configfile)
        logger.debug('Config file updated successfully')


    def _event_started(self):
        logger.info('Received event_started signal')
        self._upload_captures()


    def _event_ended(self):
        logger.info('Received event_ended signal')
        self._upload_captures()


    def _picture_saved(self, path):
        logger.debug('Received picture_saved signal: ' + path)
        self._capturesQueue.put(path)
        
        
    def _upload_captures(self):
        try:
            while (not self._capturesQueue.empty()):
                captureFile = self._capturesQueue.get()
                if (self._token == None):
                    logger.debug('No dropbox token available - Cannot upload captures')
                else:
                    config = ConfigParser.SafeConfigParser()
                    config.read(CONFIG_FILE)
                    if (config.get('dropbox', 'active') == 'true'):
                        dbx = dropbox.Dropbox(self._token)
                        logger.debug('Uploading file %s to dropbox' % captureFile)
                        with open(captureFile, 'rb') as f: 
                            data = f.read()
                        result = dbx.files_upload(data, '/' + os.path.basename(captureFile))
                        logger.debug('Result: ' + str(result))
                    else:
                        logger.debug('Uploading of captures to dropbox is deactivated')

        except Exception, e:
            logger.error(str(e))


if __name__ == '__main__':
    DropboxPlugin().run()
