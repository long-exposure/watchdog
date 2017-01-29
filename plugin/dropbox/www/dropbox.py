# Watchdog - Building supervision with Raspberry Pi
# (C)2016  - Norbert Huffschmid - GNU GPL V3 

import ConfigParser
import dbus
import json
import time
import watchdog.config

CONFIG_FILE = '/etc/watchdog.conf'


def status(req):
    req.content_type = 'application/json; charset=UTF8'
    
    trialCount = 5
    errorMessage = ''
    while (trialCount > 0):
    
        try:
            bus = dbus.SystemBus()
            proxy = bus.get_object('net.longexposure.watchdog.plugin.dropbox', '/')
            broker = dbus.Interface(proxy, 'net.longexposure.watchdog.plugin.dropbox')
            status = broker.get_status()
            return json.dumps({ 'Result': 'OK', 'IsConnected': status['IsConnected'], 'Info': status['Info'], 'Files': status['Files'] })
    
        except dbus.DBusException, e:
            # plugin startup takes some time ==> make some trials before terminating with error
            time.sleep(5)
            trialCount = trialCount - 1
            errorMessage = str(e)

        except Exception, e:
            return json.dumps({ 'Result': 'ERROR', 'Message': 'Getting status failed: ' + str(e) })

    return json.dumps({ 'Result': 'ERROR', 'Message': 'Getting status failed after 5 trials: ' + errorMessage})


def authurl(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        
        bus = dbus.SystemBus()
        proxy = bus.get_object('net.longexposure.watchdog.plugin.dropbox', '/')
        broker = dbus.Interface(proxy, 'net.longexposure.watchdog.plugin.dropbox')
        url = broker.get_authorization_url()
        return json.dumps({ 'Result': 'OK', 'Url': url })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'authurl failed: ' + str(e) })


def authorize(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        
        # read POST parameter
        code = req.form.getfirst('code')

        bus = dbus.SystemBus()
        proxy = bus.get_object('net.longexposure.watchdog.plugin.dropbox', '/')
        broker = dbus.Interface(proxy, 'net.longexposure.watchdog.plugin.dropbox')
        success = broker.authorize(code)

        if (success):
            return json.dumps({ 'Result': 'OK' })
        else:
            return json.dumps({ 'Result': 'ERROR', 'Message': 'Authorization failed' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'authorize failed: ' + str(e) })


def disconnect(req):
    req.content_type = 'application/json; charset=UTF8'

    try:

        bus = dbus.SystemBus()
        proxy = bus.get_object('net.longexposure.watchdog.plugin.dropbox', '/')
        broker = dbus.Interface(proxy, 'net.longexposure.watchdog.plugin.dropbox')
        broker.disconnect()
        return json.dumps({ 'Result': 'OK' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'disconnect failed: ' + str(e) })


def delete_files(req):
    req.content_type = 'application/json; charset=UTF8'

    try:

        bus = dbus.SystemBus()
        proxy = bus.get_object('net.longexposure.watchdog.plugin.dropbox', '/')
        broker = dbus.Interface(proxy, 'net.longexposure.watchdog.plugin.dropbox')
        broker.delete_files()
        return json.dumps({ 'Result': 'OK' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'delete_files failed: ' + str(e) })
    
    
def get_upload_captures(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        return json.dumps({ 'Result': 'OK', 'Active': (watchdog.config.get_option('dropbox', 'active') == 'true') })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'get_upload_captures failed: ' + str(e) })


def set_config_data(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        watchdog.config.write_option('dropbox', 'active', req.form.getfirst('active'))
        return json.dumps({ 'Result': 'OK' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot set config data: ' + str(e) })
