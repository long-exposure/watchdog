# Watchdog - Building supervision with Raspberry Pi
# (C)2017 - Norbert Huffschmid

# Plugin installer

import ConfigParser
import argparse
import dbus
import grp
import os
import shutil
import sys

CONFIG_FILE = '/etc/watchdog.conf'


def install(plugin, verbose=False):
    
        pluginDir = os.path.dirname(__file__) + '/../../../plugin/' + plugin
        if (not os.path.isdir(pluginDir)):
            raise RuntimeError('Plugin ' + plugin + ' not found in watchdog file tree')
        if (not os.path.isdir(pluginDir + '/www')):
            raise RuntimeError('No www directory found in plugin')
    
        if (verbose):
            print('Installing plugin ' + plugin + ' ...')
            print('Plugin directory is: ' + pluginDir)
            
        # perform custom install actions
        installScript = pluginDir + '/install'
        if (os.path.exists(installScript)):
            if (verbose):
                print('Running custom install script')
            os.chmod(installScript, 0755) # make executable
            os.system(installScript)

        # link web files into webspace
        webDir = os.path.dirname(__file__) + '/../../../www/plugin/' + plugin
        if (verbose):
            print('Linking web files to ' + webDir)
        os.symlink(pluginDir + '/www', webDir)
        print('Web files linked.')
        
        # install config
        if (os.path.exists(pluginDir + '/config')):
            config = ConfigParser.SafeConfigParser()
            config.read(CONFIG_FILE)
            if (config.has_section(plugin)):
                if (verbose):
                    print('Config section ' + plugin + ' already exists and will not be overwritten')
            else:
                if (verbose):
                    print('Appending ' + plugin + ' section to config file')
                with open(CONFIG_FILE, 'a') as configFile:
                    configFile.write('\n[' + plugin + ']\n')
                    with open(pluginDir + '/config') as pluginConfigFile:
                        configFile.write(pluginConfigFile.read())

        # install and start daemon
        if (os.path.isdir(pluginDir + '/daemon')):
            if (not os.path.exists(pluginDir + '/daemon/__main__.py')):
                raise RuntimeError('Missing __main__.py in daemon directory')
            if (not os.path.exists(pluginDir + '/daemon/__init__.py')):
                raise RuntimeError('Missing __init__.py in daemon directory')
            daemon = 'watchdog-plugin-' + plugin
            daemonDir = os.path.dirname(__file__) + '/../../../python/watchdog/plugin/' + plugin
            if (verbose):
                print('Installing daemon ' + daemon)
            os.symlink(pluginDir + '/daemon', daemonDir)
            templateFile = os.path.dirname(__file__) + '/daemon.template'
            with open(templateFile, 'r') as file:
                initScript=file.read()
            initScript = initScript.replace('<PLUGIN>', plugin)
            initScriptFile = '/etc/init.d/' + daemon
            with open(initScriptFile, 'w') as file:
                file.write(initScript)
            os.chmod(initScriptFile, 0755) # make executable
            if (verbose):
                print('Activating and starting daemon ' + daemon)
            bus = dbus.SystemBus()
            pluginProxy = dbus.Interface(bus.get_object('net.longexposure.watchdog', '/Plugin'), 'net.longexposure.watchdog')
            pluginProxy.add_daemon(daemon)
            
        if (verbose):
            print('Installation of plugin ' + plugin + ' completed.')


def uninstall(plugin, verbose=False):
    
        if (verbose):
            print('Uninstalling plugin ' + plugin + ' ...')

        pluginDir = os.path.dirname(__file__) + '/../../../plugin/' + plugin

        # stop and remove daemon
        daemon = 'watchdog-plugin-' + plugin
        if (os.path.exists('/etc/init.d/' + daemon)):
            if (verbose):
                print('Stopping and removing daemon ' + daemon)
            bus = dbus.SystemBus()
            pluginProxy = dbus.Interface(bus.get_object('net.longexposure.watchdog', '/Plugin'), 'net.longexposure.watchdog')
            pluginProxy.remove_daemon(daemon)
            daemonDir = os.path.dirname(__file__) + '/../../../python/watchdog/plugin/' + plugin
            os.remove(daemonDir)
            os.remove('/etc/init.d/' + daemon)
        
        # uninstall config (do nothing, we don't want to loose config changes here)

        # remove web files from webspace
        webDir = os.path.dirname(__file__) + '/../../../www/plugin/' + plugin
        if (verbose):
            print('Removing web files from ' + webDir)
        os.remove(webDir)

        # perform custom uninstall actions
        uninstallScript = pluginDir + '/uninstall'
        if (os.path.exists(uninstallScript)):
            if (verbose):
                print('Running custom uninstall script')
            os.chmod(uninstallScript, 0755) # make executable
            os.system(uninstallScript)

        if (verbose):
            print('Uninstallation of plugin ' + plugin + ' completed.')
        

if __name__ == "__main__":

    try:
            
        # handle command line arguments
        parser = argparse.ArgumentParser(description='Installer and uninstaller for watchdog plugins.',
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')
        parser.add_argument('command', help='command to execute', choices=['install', 'uninstall'])
        parser.add_argument('plugin', help='plugin to install/uninstall')
        args = parser.parse_args()
        
        if (args.command == 'install'):
            install(args.plugin, args.verbose)
        else:
            uninstall(args.plugin, args.verbose)

    except Exception, e:
        print >> sys.stderr, str(e) 
