import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    if getattr(sys, 'frozen', False):
        print("Executable")
    elif __file__:
        print("Script")
        base_path = os.path.join(base_path, "..")
    return os.path.join(base_path, relative_path)
