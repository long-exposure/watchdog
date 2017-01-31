# Watchdog - Building supervision with Raspberry Pi
# (C)2017  - Norbert Huffschmid - GNU GPL V3 

import datetime
import json
import os
import re
import time

CAPTURE_PATH = '/var/lib/motion'


def get_captures(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        captures = [os.path.basename(f) for f in os.listdir(CAPTURE_PATH) if re.match(r'[0-9\-]+.jpg', f)]
        return json.dumps({ 'Result': 'OK', 'Captures': sorted(captures) })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot read image files: ' + str(e) })


def delete_captures(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        captures = [os.path.basename(f) for f in os.listdir(CAPTURE_PATH) if re.match(r'[0-9\-]+.jpg', f)]
        for f in captures:
            os.remove(os.path.join(CAPTURE_PATH, f))        
            
        return json.dumps({ 'Result': 'OK' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot delete image files: ' + str(e) })


def wait_for_new_captures(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        captures = []
        now = datetime.datetime.now()
        while True:
            captures = [os.path.basename(f) for f in os.listdir(CAPTURE_PATH)
                        if (re.match(r'[0-9\-]+.jpg', f)
                        and (datetime.datetime.fromtimestamp(os.stat(CAPTURE_PATH + '/' + f).st_mtime) > now))]
            if (len(captures) > 0):
                break # new captures found- we're done
            time.sleep(5)
        return json.dumps({ 'Result': 'OK', 'Captures': sorted(captures) })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'While waiting for new captures: ' + str(e) })
