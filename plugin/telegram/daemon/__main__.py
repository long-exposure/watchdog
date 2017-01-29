# Watchdog - Building supervision with Raspberry Pi
# (C)2017 - Norbert Huffschmid

# Telegram plugin daemon

import dbus
import dbus.mainloop.glib
import dbus.service
import gobject
import logging
import Queue
import os
import requests
import signal
import time
import watchdog.config

from threading import Event
from telegram_bot import TelegramBot, TelegramBotError
from subscription_handler import SubscriptionHandler


logger = logging.getLogger('watchdog.plugin.telegram') # __name__ is __main__


class TelegramPlugin(dbus.service.Object):

    def run(self):

        try:
                
            logger.info('Starting telegram plugin ...')

            self._capturesQueue = Queue.Queue()
            self._subscribeEvent = Event()

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
            
            # provide telegram dbus services
            telegramBus = dbus.service.BusName('net.longexposure.watchdog.plugin.telegram', bus)
            dbus.service.Object.__init__(self, telegramBus, '/')
            
            # init telegram bot api
            self._bot = TelegramBot()
            self._subscriptionHandler = SubscriptionHandler(self._bot, self._subscribeEvent)
            dbus.service.Object.__init__(self._subscriptionHandler, telegramBus, '/Subscribe')
            
            try:
                if (watchdog.config.has_option('telegram', 'token')):
                    token = watchdog.config.get_option('telegram', 'token')
                    self._bot.start_message_loop(token, self._bot_callback)

                    # send startup telegram
                    if (watchdog.config.get_option('telegram', 'verbose') == 'true'):
                        chatIds = self._subscriptionHandler.get_subscribed_chats()
                        for chatId in chatIds:
                            self._bot.send_message(int(chatId), watchdog.config.get_option('telegram', 'startup_message'))

            except TelegramBotError, e:
                logger.error(str(e))
            
            # register for SIGTERM
            signal.signal(signal.SIGTERM, lambda signum, frame: mainloop.quit())
                    
            mainloop.run()

            # send shutdown telegram
            if (self._bot.is_active()):
                if (watchdog.config.get_option('telegram', 'verbose') == 'true'):
                    chatIds = self._subscriptionHandler.get_subscribed_chats()
                    for chatId in chatIds:
                        self._bot.send_message(int(chatId), watchdog.config.get_option('telegram', 'shutdown_message'))

            logger.debug('Telegram plugin terminated.')

        except Exception, e:
            logger.error(str(e))


    @dbus.service.method(dbus_interface='net.longexposure.watchdog.plugin.telegram',
                         in_signature='', out_signature='a{sv}')
    def get_status(self):
        try:

            logger.debug('Starting to determine status ...')
            if (watchdog.config.has_option('telegram', 'token')):
                if (not self._bot.is_active()):
                    token = watchdog.config.get_option('telegram', 'token')
                    self._bot.start_message_loop(token, self._bot_callback)
                botName = self._bot.get_username()
                status = dbus.Dictionary({'Result': 'OK',
                                          'IsConnected': True,
                                          'Info': 'Bot: @' + botName,
                                          'BotName': botName,
                                          'SendImages': (watchdog.config.get_option('telegram', 'send_images') == 'true'),
                                          'Verbose': (watchdog.config.get_option('telegram', 'verbose') == 'true'),
                                          'StartupMessage': watchdog.config.get_option('telegram', 'startup_message'),
                                          'ShutdownMessage': watchdog.config.get_option('telegram', 'shutdown_message') },
                                          signature='sv')
            else:
                status = dbus.Dictionary({'Result': 'OK',
                                          'IsConnected': False,
                                          'Info': 'No bot token found'},
                                         signature='sv')
            logger.debug('Telegram status: ' + str(status))
            return status

        except Exception, e:
            logger.error(str(e))
            status = dbus.Dictionary({'IsConnected': False, 'Info': 'Not Connected'}, signature='sv')
            return status


    @dbus.service.method(dbus_interface='net.longexposure.watchdog.plugin.telegram',
                         in_signature='s', out_signature='b')
    def save_token(self, token):
        try:
            logger.debug('Saving token ' + token + ' in config')
            watchdog.config.write_option('telegram', 'token', token)
            return True

        except Exception, e:
            logger.error(str(e))
            return False


    @dbus.service.method(dbus_interface='net.longexposure.watchdog.plugin.telegram',
                         in_signature='', out_signature='')
    def disconnect(self):
        try:
            logger.debug('Starting to disconnect ...')
            watchdog.config.remove_option('telegram', 'token')
            self._bot.stop_message_loop()

        except Exception, e:
            logger.error(str(e))


    def _bot_callback(self, msg):
        try:
            helpText = """
You can control me by sending these commands:
/subscribe - Subscribe for alarm notifications
/unsubscribe - Unsubscribe from alarm notifications
/photo - Take a snapshot
/help - Show this help
"""
            if ('text' in msg):
                logger.info('Bot received message: ' + msg['text'])
                
                # handle /command@Bot syntax
                botName = '@' + self._bot.get_name()
                if (msg['text'].endswith(botName)):
                    msg['text'] = msg['text'][:-len(botName)]
                    logger.debug('Removed trailing bot name from message')
                botUsername = '@' + self._bot.get_username()
                if (msg['text'].endswith(botUsername)):
                    msg['text'] = msg['text'][:-len(botUsername)]
                    logger.debug('Removed trailing bot username from message')
                    
                if (msg['text'] == '/start'):
                    answer = 'Welcome, I can help you to protect your home.\n' + helpText
                elif (msg['text'] == '/help'):
                    answer = helpText
                elif (msg['text'] == '/subscribe'):
                    answer = self._subscriptionHandler.ask_for_subscription(msg['chat']['id'])
                elif (msg['text'] == '/unsubscribe'):
                    answer = self._subscriptionHandler.unsubscribe(msg['chat']['id'])
                elif (msg['text'] == '/photo'):
                    answer = self._make_snapshot(msg['chat']['id'])
                else:
                    answer = helpText
                
                if (answer != None):
                    logger.info('Bot answers: ' + answer)
                    self._bot.send_message(msg['chat']['id'], answer)
            else:
                logger.error('Bot message with unsupported message type received: ' + msg['content_type'])

        except Exception, e:
            logger.error(str(e))

    
    def _event_started(self):
        logger.info('Received event_started signal')
        self._send_captures()


    def _event_ended(self):
        logger.info('Received event_ended signal')
        self._send_captures()


    def _picture_saved(self, path):
        logger.debug('Received picture_saved signal: ' + path)
        self._capturesQueue.put(path)
        
        
    def _send_captures(self):
        try:
            while (not self._capturesQueue.empty()):
                captureFile = self._capturesQueue.get()
                if (self._bot.is_active()):
                    if (watchdog.config.get_option('telegram', 'send_images') == 'true'):
                        chatIds = self._subscriptionHandler.get_subscribed_chats()
                        if (len(chatIds) > 0):
                            logger.info('Sending image %s to telegram subscribers' % captureFile)
                            count = 1
                            for chatId in chatIds:
                                try:
                                    if (count == 1):
                                        # for the first receiver the photo has to be uploaded
                                        fileId = self._bot.upload_and_send_photo(int(chatId), captureFile)
                                    else:
                                        # all other receivers can reference the file ID
                                        self._bot.send_photo(int(chatId), fileId)
                                except TelegramBotError, e:
                                    # remove subscriber on 403 error (he already has left the chat)
                                    if (e.response.status_code == 403):
                                        self._subscriptionHandler.unsubscribe(chatId)
                                    else:
                                        raise e
                                count += 1
                        else:
                            logger.debug('No telegram subscribers currently registered')
                    else:
                        logger.debug('Sending of captures to telegram is deactivated')
                else:
                    logger.debug('Telegram bot is not active')
                
        except Exception, e:
            logger.error(str(e))


    def _make_snapshot(self, chatId):
        if str(chatId) in self._subscriptionHandler.get_subscribed_chats():
            requests.get('http://localhost:8080/0/action/snapshot')
            time.sleep(1) # wait for motion server to complete snapshot
            self._bot.upload_and_send_photo(chatId, '/var/lib/motion/lastsnap.jpg')
            return None
        else:
            return 'Nice try. Please subscribe for this service!'
        

if __name__ == '__main__':
    TelegramPlugin().run()
