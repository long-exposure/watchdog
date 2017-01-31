# Watchdog - Building supervision with Raspberry Pi
# (C)2017  - Norbert Huffschmid - GNU GPL V3 

from subprocess import Popen, PIPE

def index(req):
    
    req.write('Watchdog - (C)2017 - Norbert Huffschmid\n\n')

    req.write('Building supervision with Raspberry Pi\n\n')
    
    with open ('/etc/watchdog.version', 'r') as version_file:
        version = version_file.read()
    req.write('Version: ' + version + '\n')

    req.write('License: GNU GPL V3\n\n')
    
    process = Popen(['/bin/uname', '-a'], stdout=PIPE, stderr=PIPE)
    output, errors = process.communicate()
    req.write(output)
