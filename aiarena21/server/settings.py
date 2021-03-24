import os

TOTAL_ROUNDS = 100

MAP = None
MAP_SIZE = None
MAP_FILE = None


def set_map_file(cwd, path):
    global MAP, MAP_SIZE, MAP_FILE
    MAP_FILE = path

    if os.path.isfile(os.path.join(cwd, path)):
        correct_path = os.path.join(cwd, path)
    else:
        correct_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'maps', MAP_FILE)

    with open(correct_path, 'r') as f:
        rows = []
        for line in f.readlines():
            rows.append(tuple(line.strip()))
        MAP = tuple(rows)
        MAP_SIZE = (len(rows), len(rows[0]))

set_map_file("", "5.txt")

BIKE_LENGTH = 3  # How far can one travel with a bike
BIKE_COST = 30
BIKE_TURNS = 3  # How many turns one can use a bike with one rent
PORTAL_GUN_COST = 100
PORTAL_GUN_TURNS = 1
ITEM_SPAWN_PERIOD = 20  # How many ticks before the next batch of items spawn
OVERLAP_ITEMS = True
HEATMAP_LARGEST_DISTANCE = 10

REPLAY_PATH = "replay.txt"