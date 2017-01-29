# Watchdog - Building supervision with Raspberry Pi
# (C)2017  - Norbert Huffschmid - GNU GPL V3 

import dbus
import json
import watchdog.config


def status(req):
    req.content_type = 'application/json; charset=UTF8'
    
    try:
        bus = dbus.SystemBus()
        proxy = bus.get_object('net.longexposure.watchdog.plugin.telegram', '/')
        broker = dbus.Interface(proxy, 'net.longexposure.watchdog.plugin.telegram')
        status = broker.get_status()
        return json.dumps(status)

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Getting status failed: ' + str(e) })


def save_token(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        
        # read POST parameter
        token = req.form.getfirst('token')

        bus = dbus.SystemBus()
        proxy = bus.get_object('net.longexposure.watchdog.plugin.telegram', '/')
        broker = dbus.Interface(proxy, 'net.longexposure.watchdog.plugin.telegram')
        success = broker.save_token(token)

        if (success):
            return json.dumps({ 'Result': 'OK' })
        else:
            return json.dumps({ 'Result': 'ERROR', 'Message': 'Invalid token!' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'save_token failed: ' + str(e) })


def disconnect(req):
    req.content_type = 'application/json; charset=UTF8'

    try:

        bus = dbus.SystemBus()
        proxy = bus.get_object('net.longexposure.watchdog.plugin.telegram', '/')
        broker = dbus.Interface(proxy, 'net.longexposure.watchdog.plugin.telegram')
        broker.disconnect()
        return json.dumps({ 'Result': 'OK' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'disconnect failed: ' + str(e) })


def set_config_data(req):
    req.content_type = 'application/json; charset=UTF8'

    try:

        watchdog.config.write_option('telegram', 'send_images', req.form.getfirst('send_images'))
        watchdog.config.write_option('telegram', 'verbose', req.form.getfirst('verbose'))
        watchdog.config.write_option('telegram', 'startup_message', req.form.getfirst('startup_message'))
        watchdog.config.write_option('telegram', 'shutdown_message', req.form.getfirst('shutdown_message'))
        return json.dumps({ 'Result': 'OK' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot set config data: ' + str(e) })


def check_subscribe(req):
    req.content_type = 'application/json; charset=UTF8'

    try:

        bus = dbus.SystemBus()
        proxy = bus.get_object('net.longexposure.watchdog.plugin.telegram', '/Subscribe')
        broker = dbus.Interface(proxy, 'net.longexposure.watchdog.plugin.telegram')
        subscriber = broker.check_subscribe()
        return json.dumps({ 'Result': 'OK', 'Subscriber': subscriber })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'check_subscribe failed: ' + str(e) })


def subscribe(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        chatId = int(req.form.getfirst('chat_id'))

        bus = dbus.SystemBus()
        proxy = bus.get_object('net.longexposure.watchdog.plugin.telegram', '/Subscribe')
        broker = dbus.Interface(proxy, 'net.longexposure.watchdog.plugin.telegram')
        broker.confirm_subscribe(chatId)
        return json.dumps({ 'Result': 'OK' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'subscribe failed: ' + str(e) })


def list_subscribers(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        bus = dbus.SystemBus()
        proxy = bus.get_object('net.longexposure.watchdog.plugin.telegram', '/Subscribe')
        broker = dbus.Interface(proxy, 'net.longexposure.watchdog.plugin.telegram')
        subscribers = broker.list_subscribers()
        
        return json.dumps({ 'Result': 'OK', 'Records': subscribers })
    
    except Exception, e:
        return json.dumps({ 'Result': 'Error', 'Message': 'list_subscribers failed: ' + str(e) })


def delete_subscriber(req):
    req.content_type = 'application/json; charset=UTF8'
    
    try:
        # read POST parameter
        chatId = int(req.form.getfirst('ChatId'))

        bus = dbus.SystemBus()
        proxy = bus.get_object('net.longexposure.watchdog.plugin.telegram', '/Subscribe')
        broker = dbus.Interface(proxy, 'net.longexposure.watchdog.plugin.telegram')
        subscribers = broker.delete_subscriber(chatId)

        return json.dumps({ "Result": "OK" })

    except Exception, e:
        return json.dumps({ 'Result': 'Error', 'Message': 'list_subscribers failed: ' + str(e) })
