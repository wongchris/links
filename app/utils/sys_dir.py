import os
import sys

class SystemPath():

    APP_DIR = ''
    if getattr(sys, 'frozen', False):
        APP_DIR = os.path.dirname(sys.executable)
    elif __file__:
        APP_DIR = os.path.dirname(os.path.dirname(__file__))
    print(APP_DIR)

    PROJECT_DIR = os.path.dirname(APP_DIR)

    SQL_DIR = os.path.join(APP_DIR, 'usage\SQL')
    MAP_DIR = os.path.join(APP_DIR, 'usage\Mapping')
    TOOL_DIR = os.path.join(APP_DIR, 'usage\Tools')
