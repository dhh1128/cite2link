import os
import sys

# Try loading an installed python package. If not installed, load it
# from path relative to this script.

try:
    from cite2link.app import main
except ModuleNotFoundError:
    MY_FOLDER = os.path.normpath(os.path.dirname(os.path.realpath(os.path.abspath(__file__))))
    sys.path.insert(0, os.path.normpath(os.path.join(MY_FOLDER, '..')))
    from cite2link.app import main


if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print('')
