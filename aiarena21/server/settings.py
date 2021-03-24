import os

TOTAL_ROUNDS = 100

MAP_FILE = '5.txt'

with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'maps'), MAP_FILE), 'r') as f:
    rows = []
    for line in f.readlines():
        rows.append(tuple(line.strip()))
    MAP = tuple(rows)
    MAP_SIZE = (len(rows), len(rows[0]))

BIKE_LENGTH = 3  # How far can one travel with a bike
BIKE_COST = 30
BIKE_TURNS = 3  # How many turns one can use a bike with one rent
PORTAL_GUN_COST = 100
PORTAL_GUN_TURNS = 1
ITEM_SPAWN_PERIOD = 20  # How many ticks before the next batch of items spawn
OVERLAP_ITEMS = True
HEATMAP_LARGEST_DISTANCE = 10
