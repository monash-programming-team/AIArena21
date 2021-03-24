import random
TEAM_NAME = f"team{random.randint(1,9)}"
REMAINING_TURNS = 0  # How many turns left in the game
MAP_SIZE = (-1, -1)  # rows, cols
MAP = None  # MAP[row][col] is either . (for free cells) or # (for blocked ones)
PLAYERS = None  # PLAYERS[player_name] will be of format { score: int, location: (row, col) }
ITEMS = None  # List of all items on the map. Each item will be of format { type: int, score: int, location: (row, col)}
NEW_ITEMS = None  # List of items added to the map in this round with the same format above. None if no items added.
HEATMAP = None  # The heatmap of hints for new batch of items deploying on the map
