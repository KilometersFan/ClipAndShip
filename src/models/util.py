import os
import sys


def resource_path(relative_path, config_related=False):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # if running as script or building as --console and --onefile, uncomment
    # this if-else block and comment the one below
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    if getattr(sys, 'frozen', False):
        # for onedir
        base_path = os.path.dirname(sys.executable)
    elif __file__:
        base_path = os.path.join(base_path, "..")
    # if building as noconsole and onefile, uncomment these next lines
    # base_path = os.path.join(os.path.dirname(sys.executable), "../../../")
    return os.path.join(base_path, relative_path)
