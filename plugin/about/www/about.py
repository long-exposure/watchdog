# Watchdog - Building supervision with Raspberry Pi
# (C)2017  - Norbert Huffschmid - GNU GPL V3 

import os
from subprocess import Popen, PIPE

def index(req):
    
    req.write('Watchdog - (C)2017 - Norbert Huffschmid\n\n')

    req.write('Building supervision with Raspberry Pi\n\n')

    process = Popen(['/usr/bin/git', 'describe', '--tags'], stdout=PIPE, stderr=PIPE, cwd=os.path.dirname(__file__))
    output, errors = process.communicate()
    req.write('Version: %s\n' % output)

    req.write('License: GNU GPL V3\n\n')
    
    process = Popen(['/bin/uname', '-a'], stdout=PIPE, stderr=PIPE)
    output, errors = process.communicate()
    req.write(output)
