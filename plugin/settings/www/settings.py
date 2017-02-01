# Watchdog - Building supervision with Raspberry Pi
# (C)2017  - Norbert Huffschmid - GNU GPL V3 

import ConfigParser
import dbus
import json
import os
import re
import subprocess
import urllib2
import uuid
import time

CONFIG_FILE = '/etc/watchdog.conf'


def get_settings(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        result = { 'Result': 'OK'}

        response = urllib2.urlopen("http://localhost:8080/0/config/get?query=rotate").read()
        m = re.match(r'^rotate = (\d+)', response)
        if m:
            result['Rotate'] = m.groups()[0]
        else:
            return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot read rotate value:\n\n' + response})

        response = urllib2.urlopen("http://localhost:8080/0/config/get?query=width").read()
        m = re.match(r'^width = (\d+)', response)
        if m:
            result['Width'] = m.groups()[0]
        else:
            return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot read width value:\n\n' + response})

        response = urllib2.urlopen("http://localhost:8080/0/config/get?query=height").read()
        m = re.match(r'^height = (\d+)', response)
        if m:
            result['Height'] = m.groups()[0]
        else:
            return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot read height value:\n\n' + response})

        config = ConfigParser.SafeConfigParser()
        config.read(CONFIG_FILE)
        result['Sensitivity'] = int(config.get('motion', 'sensitivity'))
        
        return json.dumps(result)

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot get settings: ' + str(e) })


def set_settings(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        # read current plugin state
        plugins = _get_plugins()
        
        # read POST parameters 
        activePlugins = req.form.getfirst('activePlugins')
        inactivePlugins = req.form.getfirst('inactivePlugins')
        rotate = req.form.getfirst('rotate')
        width = req.form.getfirst('width')
        height = req.form.getfirst('height')
        sensitivity = req.form.getfirst('sensitivity')

        # motion only accepts modulo8 values for width and height
        width = str((int(width) / 8) * 8)
        height = str((int(height) / 8) * 8)

        # determine motion threshold
        totalPixels = int(width) * int(height)
        thresholdMax = totalPixels / 7
        thresholdMin = thresholdMax / 100
        threshold = str((thresholdMin - thresholdMax) / 100 * int(sensitivity) + thresholdMax)
        
        config = ConfigParser.SafeConfigParser()
        config.read(CONFIG_FILE)
        config.set('plugins', 'active', activePlugins)
        config.set('plugins', 'inactive', inactivePlugins)
        with open(CONFIG_FILE, 'wb') as configfile:
            config.write(configfile)

        # check if plugins have to be (re-)activated
        for activePlugin in activePlugins.split(','):
            for plugin in plugins:
                if ((activePlugin == plugin['Name']) and (plugin['Active'] == False)):
                    bus = dbus.SystemBus()
                    pluginProxy = dbus.Interface(bus.get_object('net.longexposure.watchdog', '/Plugin'), 'net.longexposure.watchdog')
                    pluginProxy.add_daemon('watchdog-plugin-' + activePlugin)


        # check if plugins have to be deactivated
        for inactivePlugin in inactivePlugins.split(','):
            for plugin in plugins:
                if ((inactivePlugin == plugin['Name']) and (plugin['Active'] == True)):
                    bus = dbus.SystemBus()
                    pluginProxy = dbus.Interface(bus.get_object('net.longexposure.watchdog', '/Plugin'), 'net.longexposure.watchdog')
                    pluginProxy.remove_daemon('watchdog-plugin-' + inactivePlugin)

        urllib2.urlopen("http://localhost:8080/0/config/set?rotate=" + rotate).read()
        urllib2.urlopen("http://localhost:8080/0/config/set?width=" + width).read()
        urllib2.urlopen("http://localhost:8080/0/config/set?height=" + height).read()
        urllib2.urlopen("http://localhost:8080/0/config/set?threshold=" + threshold).read()
        urllib2.urlopen("http://localhost:8080/0/config/writeyes").read()

        config = ConfigParser.SafeConfigParser()
        config.read(CONFIG_FILE)
        config.set('motion', 'sensitivity', sensitivity)
        with open(CONFIG_FILE, 'wb') as configfile:
            config.write(configfile)

        _restart_motion()

        return json.dumps({ 'Result': 'OK' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot set settings: ' + str(e) })


def get_plugins(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        plugins = _get_plugins()
        return json.dumps({ 'Result': 'OK', 'Plugins': plugins })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot determine plugins: ' + str(e) })


def _get_plugins():
    
    # init plugin list with mandatory entries
    plugins = [{ 'Name': 'settings', 'Active': True, 'Optional': False },
               { 'Name': 'about',    'Active': True, 'Optional': False }
               ]

    config = ConfigParser.SafeConfigParser()
    config.read(CONFIG_FILE)
    activePlugins = config.get('plugins', 'active').split(',')
    inactivePlugins = config.get('plugins', 'inactive').split(',')
    pluginPath = os.path.dirname(os.path.realpath(__file__)) + '/../../../www/plugin'
    pluginDirs = [d for d in os.listdir(pluginPath) if os.path.isdir(d)]

    for activePlugin in activePlugins:
        if ((activePlugin == 'settings') or (activePlugin == 'about')):
            continue # already defined
        plugin = {}
        plugin['Name'] = activePlugin
        plugin['Optional'] = True;
        plugin['Active'] = True;
        plugins.append(plugin)
        
    for inactivePlugin in inactivePlugins:
        if (inactivePlugin == ''):
            continue # no inactive plugin found
        plugin = {}
        plugin['Name'] = inactivePlugin
        plugin['Optional'] = True;
        plugin['Active'] = False;
        plugins.append(plugin)
        
    for pluginDir in pluginDirs:
        if ((pluginDir in activePlugins) or (pluginDir in inactivePlugins)):
            continue # already handled
         
        # add new detected plugin (that is not yet defined in config)
        plugin = {}
        plugin['Name'] = pluginDir
        plugin['Optional'] = True;
        plugin['Active'] = True;
        plugins.append(plugin)

    return plugins

    
def _restart_motion():
    subprocess.call(['sudo', 'service', 'motion', 'restart'])
    time.sleep(2) # wait for motion restart
