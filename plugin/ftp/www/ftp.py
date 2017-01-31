# Watchdog - Building supervision with Raspberry Pi
# (C)2017  - Norbert Huffschmid - GNU GPL V3 

import ConfigParser
import ftplib
import json
import re

CONFIG_FILE = '/etc/watchdog.conf'


def get_ftp_data(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        result = { 'Result': 'OK'}

        config = ConfigParser.SafeConfigParser()
        config.read(CONFIG_FILE)
        result['Active'] = config.getboolean('ftp', 'active')
        result['Host'] = config.get('ftp', 'host')
        result['User'] = config.get('ftp', 'user')
        result['Password'] = config.get('ftp', 'password')
        result['Directory'] = config.get('ftp', 'directory')

        return json.dumps(result)

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot get ftp data: ' + str(e) })


def set_ftp_data(req):
    req.content_type = 'application/json; charset=UTF8'

    try:

        # read POST parameters 
        active = req.form.getfirst('active')
        host = req.form.getfirst('host')
        user = req.form.getfirst('user')
        password = req.form.getfirst('password')
        directory = req.form.getfirst('directory')

        config = ConfigParser.SafeConfigParser()
        config.read(CONFIG_FILE)
        config.set('ftp', 'active', active)
        config.set('ftp', 'host', host)
        config.set('ftp', 'user', user)
        config.set('ftp', 'password', password)
        config.set('ftp', 'directory', directory)
        with open(CONFIG_FILE, 'wb') as configfile:
            config.write(configfile)

        return json.dumps({ 'Result': 'OK' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot set ftp data: ' + str(e) })


def test_ftp_access(req):
    req.content_type = 'application/json; charset=UTF8'

    try:

        # read POST parameters 
        host = req.form.getfirst('host')
        user = req.form.getfirst('user')
        password = req.form.getfirst('password')
        directory = req.form.getfirst('directory')

        # perform rudimentary test
        ftp = ftplib.FTP(host)
        ftp.login(user, password)
        ftp.cwd(directory.strip('/'))
        files = [] 
        ftp.dir(files.append)
        ftp.quit()

        return json.dumps({ 'Result': 'OK', 'Message': 'FTP connection successfully tested.' , 'Files': len(files) })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'FTP test failed: ' + str(e) })


def clear_directory(req):
    req.content_type = 'application/json; charset=UTF8'

    try:

        # read POST parameters 
        host = req.form.getfirst('host')
        user = req.form.getfirst('user')
        password = req.form.getfirst('password')
        directory = req.form.getfirst('directory')

        ftp = ftplib.FTP(host)
        ftp.login(user, password)
        ftp.cwd(directory.strip('/'))
        for file in ftp.nlst():
            ftp.delete(file)
        ftp.quit()

        return json.dumps({ 'Result': 'OK', 'Message': 'All files deleted.' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Clear command failed: ' + str(e) })
