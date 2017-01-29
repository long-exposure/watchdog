# Watchdog - Building supervision with Raspberry Pi
# (C)2017 - Norbert Huffschmid

# Subscription handler

import dbus.service
import logging
import watchdog.config

from threading import Event


logger = logging.getLogger(__file__)


class SubscriptionHandler(dbus.service.Object):

    def __init__(self, bot, subscribeEvent):
        self._bot = bot
        self._chat = None
        self._confirmEvent = Event()
        
        
    def ask_for_subscription(self, chatId):
        self._chat = self._bot.get_chat(chatId)
        logger.debug('Subscribe request received' + str(self._chat))
        
        # test if already subscribed
        subscribedChatIds = watchdog.config.get_option('telegram', 'subscribers').split(',')
        if (str(chatId) in subscribedChatIds):
            logger.debug('Chat ID already subscribed')
            return 'You are already subscribed!'
        
        # wait for web user reaction
        self._confirmEvent.clear()
        if (self._confirmEvent.wait(30) == True): # returns False in case of timeout
            if (self._confirmedChatId == chatId):
                subscribedChatIds.append(str(chatId))
                watchdog.config.write_option('telegram', 'subscribers', ','.join(subscribedChatIds))
                answer = 'Welcome, you have successfully subscribed.'
            else:
                answer = 'Ooops, something went wrong ...'
                logger.error('Chat ID mismatch: %i was requested and %i has been confirmed' % (chatId, self._confirmedChatId))
        else:   
            answer = 'Sorry, you are not allowed to subscribe here :('
    
        self._chat = None
        self._confirmedChatId = 0
        
        return answer
    

    def unsubscribe(self, chatId):
        # test if subscribed
        subscribedChatIds = watchdog.config.get_option('telegram', 'subscribers').split(',')
        if (not str(chatId) in subscribedChatIds):
            logger.debug('Chat ID not subscribed at all')
            return 'Who are you?'
        
        # remove chat ID from config file
        subscribedChatIds.remove(str(chatId))
        watchdog.config.write_option('telegram', 'subscribers', ','.join(subscribedChatIds))
        return 'Good bye!'
    
    
    def get_subscribed_chats(self):
        subscribedChatIds = watchdog.config.get_option('telegram', 'subscribers').split(',')
        if ('' in subscribedChatIds):
            subscribedChatIds.remove('')
        return subscribedChatIds


    @dbus.service.method(dbus_interface='net.longexposure.watchdog.plugin.telegram',
                         in_signature='', out_signature='a{sv}')
    def check_subscribe(self):
        try:
            #logger.debug('Check for a received subscriber request ...')

            if (self._chat != None):
                if (self._chat['type'] == 'private'):
                    return dbus.Dictionary( { 'Found': True, 'Name': self._chat['first_name'] + ' ' + self._chat['last_name'],
                                              'ChatId': self._chat['id'] }, signature='sv')
                elif (self._chat['type'] == 'group'):
                    return dbus.Dictionary( { 'Found': True, 'Name': self._chat['title'],
                                              'ChatId': self._chat['id'] }, signature='sv')
                else:
                    logger.error('Unsupported chat type: ' + self._chat['type'])
            else:
                return dbus.Dictionary( { 'Found': False } , signature='sv')

        except Exception, e:
            logger.error(str(e))


    @dbus.service.method(dbus_interface='net.longexposure.watchdog.plugin.telegram',
                         in_signature='i', out_signature='')
    def confirm_subscribe(self, chatId):
        try:
            logger.debug('Web user has confirmed subscription')
            
            # trigger positive telegram response
            self._confirmedChatId = chatId
            self._confirmEvent.set()
            
        except Exception, e:
            logger.error(str(e))


    @dbus.service.method(dbus_interface='net.longexposure.watchdog.plugin.telegram',
                         in_signature='', out_signature='aa{sv}')
    def list_subscribers(self):
        try:

            logger.debug('Starting to determine subscriber list ...')
            
            subscribedChatIds = watchdog.config.get_option('telegram', 'subscribers').split(',')
            subscribers = []
            for chatId in self.get_subscribed_chats():
                chat = self._bot.get_chat(int(chatId))
                logger.debug('Found subscribed chat: ' + str(chat))
                if (chat['type'] == 'private'):
                    subscriber = { 'ChatId': chat['id'], 'Name': chat['first_name'] + ' ' + chat['last_name'], 'Type': chat['type'] }
                elif (chat['type'] == 'group'):
                    subscriber = { 'ChatId': chat['id'], 'Name': chat['title'], 'Type': chat['type'] }
                else:
                    logger.error('Unsupported chat type: ' + chat['type'])
                    continue
                subscribers.append(dbus.Dictionary(subscriber, signature='sv'))
                    
            return dbus.Array(subscribers, signature='a{sv}')

        except Exception, e:
            logger.error(str(e))


    @dbus.service.method(dbus_interface='net.longexposure.watchdog.plugin.telegram',
                         in_signature='i', out_signature='')
    def delete_subscriber(self, chatId):
        try:
            logger.debug('Remove subscriber with chat id %i on web admins request ...' % chatId)
            
            # test if subscribed
            subscribedChatIds = watchdog.config.get_option('telegram', 'subscribers').split(',')
            if (not str(chatId) in subscribedChatIds):
                logger.error('Chat ID not subscribed at all')
                return
            
            # remove chat ID from config file
            subscribedChatIds.remove(str(chatId))
            watchdog.config.write_option('telegram', 'subscribers', ','.join(subscribedChatIds))
            
            logger.info('Removed chat ID % i from subscriber list' % chatId)
            self._bot.send_message(chatId, 'Good bye!')

        except Exception, e:
            logger.error(str(e))
