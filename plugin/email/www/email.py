# Watchdog - Building supervision with Raspberry Pi
# (C)2017  - Norbert Huffschmid - GNU GPL V3 

import ConfigParser
import json
import re

CONFIG_FILE = '/etc/watchdog.conf'


def get_email_data(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        result = { 'Result': 'OK'}

        config = ConfigParser.SafeConfigParser()
        config.read(CONFIG_FILE)
        result['Active'] = config.get('email', 'active')
        result['Recipient'] = config.get('email', 'recipient')
        result['Subject'] = config.get('email', 'subject')
        result['Message'] = config.get('email', 'message')
        result['Attach'] = config.get('email', 'attach')
        result['Smtp'] = config.get('email', 'smtp')
        result['User'] = config.get('email', 'user')
        result['Password'] = config.get('email', 'password')

        return json.dumps(result)

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot get email data: ' + str(e) })


def set_email_data(req):
    req.content_type = 'application/json; charset=UTF8'

    try:

        # read POST parameters 
        active = req.form.getfirst('active')
        recipient = req.form.getfirst('recipient')
        subject = req.form.getfirst('subject')
        message = req.form.getfirst('message')
        attach = req.form.getfirst('attach')
        smtp = req.form.getfirst('smtp')
        user = req.form.getfirst('user')
        password = req.form.getfirst('password')
        
        # validity check for recipient(s)
        valid_email = '[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]+'
        if not re.match('^' + valid_email + '(;' + valid_email + ')*$', recipient):
            raise ValueError('Invalid recipient(s):\n' + recipient)

        config = ConfigParser.SafeConfigParser()
        config.read(CONFIG_FILE)
        config.set('email', 'active', active)
        config.set('email', 'recipient', recipient)
        config.set('email', 'subject', subject)
        config.set('email', 'message', message)
        config.set('email', 'attach', attach)
        config.set('email', 'smtp', smtp)
        config.set('email', 'user', user)
        config.set('email', 'password', password)
        with open(CONFIG_FILE, 'wb') as configfile:
            config.write(configfile)

        return json.dumps({ 'Result': 'OK' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot set email data: ' + str(e) })
