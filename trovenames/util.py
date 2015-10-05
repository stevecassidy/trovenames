

from ConfigParser import ConfigParser
import os

def readconfig():
    """Read the configuration file config.ini and return a dictionary
    of configuration variables"""

    configfile = os.path.join(os.path.dirname(__file__), 'config.ini')
    config = ConfigParser()
    config.read(configfile)

    return config
