# Watchdog - Building supervision with Raspberry Pi
# (C)2017  - Norbert Huffschmid - GNU GPL V3 
# livecam plugin

import glob
import json
import os
import requests
import uuid
import time


def snapshot(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        #remove old snapshots
        for snapshot in glob.glob("/var/lib/motion/*snapshot.jpg"):
            os.remove(snapshot)
            
        # trigger motion to create new snapshot
        requests.get('http://localhost:8080/0/action/snapshot')
        time.sleep(1) # wait for motion server to complete snapshot
        return json.dumps({ 'Result': 'OK', 'Snapshot': '/captures/lastsnap.jpg?nocache=' + str(uuid.uuid4()) })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot make snapshot: ' + str(e) })
