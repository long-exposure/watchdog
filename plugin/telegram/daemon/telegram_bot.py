# Watchdog - Building supervision with Raspberry Pi
# (C)2017 - Norbert Huffschmid

# Telegram Bot

# After evaluating Telepot, we decided to implement our own bot
# Telepot was not able to stop a running message loop and appeared unstable
# see: https://github.com/nickoala/telepot/issues/205

import json
import logging
import requests
import time
from threading import Thread

logger = logging.getLogger(__file__)

LONGPOLL_TIMEOUT = 30


class TelegramBot(object):

    def __init__(self):
        self._token = None

        
    def is_active(self):
        return (self._token != None)
    
    
    def start_message_loop(self, token, callback):
        if (self._token != None):
            raise RuntimeError('Cannot start message loop if already running')
        
        logger.debug('Start message loop with token %s' % token)
        self._token = token
        self._callback = callback
        
        try:
            me = self._send_get_request('getMe')
            self._name = me['result']['first_name']
            self._username = me['result']['username']
            self._loopThread = Thread(target = self._message_loop)
            self._loopThread.start()
        except Exception, e:
            self._token = None
            raise e


    def stop_message_loop(self):
        if (self._token == None):
            raise RuntimeError('Cannot stop message loop on inactive Bot')
        
        self._token = None
        self._name = None
        self._username = None
        self._loopThread.join()
        logger.debug('Message loop terminated')


    def send_message(self, chatId, text):
        if (self._token == None):
            raise RuntimeError('Cannot send message on inactive Bot')
        
        self._send_get_request('sendMessage?chat_id=%i&text=%s' % (chatId, text))
    
    
    def upload_and_send_photo(self, chatId, path):
        if (self._token == None):
            raise RuntimeError('Cannot upload photo on inactive Bot')
        
        logger.debug('Upload photo as multi-part form post')
        response = requests.post('https://api.telegram.org/bot%s/sendPhoto' % self._token,
                                 files = { 'photo': open(path,'rb') },
                                 data =  { 'chat_id': str(chatId) })

        if (response.status_code != 200):
            raise TelegramBotError('Telegram bot api error: ' + str(response.text), response)

        logger.debug('Received telegram bot api response: %i - %s' % (response.status_code, response.text))
        
        fileId = response.json()['result']['photo'][-1]['file_id']
        logger.debug('Return file ID of greatest image: %s' % fileId)

        return fileId
    
    
    def send_photo(self, chatId, fileId):
        if (self._token == None):
            raise RuntimeError('Cannot send photo on inactive Bot')
        
        self._send_get_request('sendPhoto?chat_id=%i&photo=%s' % (chatId, fileId))
    
    
    def get_chat(self, chatId):
        if (self._token == None):
            raise RuntimeError('Cannot get chat info on inactive Bot')
        
        return self._send_get_request('getChat?chat_id=%i' % chatId)['result']


    def get_name(self):
        return self._name


    def get_username(self):
        return self._username


    def _send_get_request(self, methodName):
        logger.debug('Send get request via telegram bot api: %s' % methodName)
        response = requests.get('https://api.telegram.org/bot%s/%s' % (self._token, methodName))
        if (response.status_code != 200):
            raise TelegramBotError('Telegram bot api error: ' + str(response.text), response)
        
        logger.debug('Received telegram bot api response: %i - %s' % (response.status_code, response.text))
        return response.json()
        
        
    def _message_loop(self):
        offset = 0
        while True:
            logger.debug('Message loop is running ...')
            
            try:
                for update in self._send_get_request('getUpdates?offset=%i&timeout=%i' % (offset, LONGPOLL_TIMEOUT))['result']:
                    offset = update['update_id'] + 1
                    message = update['message']
                    logger.debug('Telegram message received: ' + str(message))
                    self._callback(message)
                    
            except Exception, e:
                logger.error(str(e))
                time.sleep(60) # do not flood telegram server in case of outage

            time.sleep(1) # emergency break in case that getUpdates returns immediately with 200
            
            if (self._token == None):
                break # terminate message loop
            
            
class TelegramBotError(Exception):

    def __init__(self, message, response):
        
        super(TelegramBotError, self).__init__(message)
        self.response = response
