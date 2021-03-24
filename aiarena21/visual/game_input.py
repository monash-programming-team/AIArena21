import time

USE_FILE = False
FILE_PATH = 'replay.txt'
TAIL = None
FILE = None


def use_file(path):
    global USE_FILE
    global FILE_PATH
    # global TAIL
    global FILE
    USE_FILE = True
    FILE_PATH = path
    # TAIL = sh.tail("-f", path, _iter=True)
    FILE = open(FILE_PATH, 'r')


queue = []


def get_input():
    global USE_FILE
    # global TAIL
    global queue
    global FILE

    if not USE_FILE:
        return input()

    line = FILE.readline()
    while not line:
        time.sleep(0.1)
        line = FILE.readline()
    return line


