import logging
import logging.config

logging.config.fileConfig('/etc/watchdog-logging.conf', disable_existing_loggers=False)
