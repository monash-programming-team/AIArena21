import random
import aiarena21.server.settings as settings
from aiarena21.server.item import Item1, Item2, Item3
from opensimplex import OpenSimplex
from aiarena21.server.logs import log, replay


class Game:
    def __init__(self, players):
        self.current_round = 0
        self.total_rounds = settings.TOTAL_ROUNDS
        self.map_size = settings.MAP_SIZE
        self.map = settings.MAP
        self.bike_length = settings.BIKE_LENGTH
        self.players = players
        self.items_map = [[[] for _ in range(settings.MAP_SIZE[1])] for _ in range(settings.MAP_SIZE[0])]
        self.new_items = None
        self._incoming_items = None
        self.heatmap = [[0 for _ in range(self.map_size[1])] for _ in range(self.map_size[0])]
        self.bike_cost = settings.BIKE_COST
        self.portal_gun_cost = settings.PORTAL_GUN_COST
        self.bike_turns = settings.BIKE_TURNS
        self.portal_gun_turns = settings.PORTAL_GUN_TURNS
        self.all_items = [Item1, Item2, Item3]
        self.noise_gen = OpenSimplex()
        self.random_spawn()

    def cell_available(self, row, col):
        return 0 <= row < self.map_size[0] and 0 <= col < self.map_size[1] and self.map[row][col] != '#'

    def path_available(self, p1, p2, max_dist):
        q = [(p1, 0)]
        seen = [p1]
        dx = [0, 1, 0, -1]
        dy = [1, 0, -1, 0]
        while len(q) > 0:
            front, dist = q[0]
            if dist >= max_dist:
                return False
            q = q[1:]
            for d in range(4):
                new_p = (front[0] + dx[d], front[1] + dy[d])
                if new_p not in seen and self.cell_available(*new_p):
                    if new_p == p2:
                        return True
                    seen.append(new_p)
                    q.append((new_p, dist + 1))

    def random_spawn(self):
        spawn_locations = []
        for row in range(self.map_size[0]):
            for col in range(self.map_size[1]):
                if self.map[row][col] in ['S', 's']:
                    spawn_locations.append((row, col))

        while len(spawn_locations) < len(self.players):
            row, col = (random.randint(0, self.map_size[i] - 1) for i in range(2))
            while not self.cell_available(row, col) or (row, col) in spawn_locations:
                row, col = (random.randint(0, self.map_size[i] - 1) for i in range(2))
            spawn_locations.append((row, col))

        random_bool = random.randint(0, 1)
        if random_bool == 1:
            spawn_locations[0], spawn_locations[1] = spawn_locations[1], spawn_locations[0]

        for i in range(2):
            self.players[i].location = spawn_locations[i]

    def deploy_items(self):
        """
        Generate new items and update items_map and new_items accordingly
        if no new item -> self.new_items = None
        if new items -> add to self.new_items
        """
        # Do nothing outside of the spawning tick.
        if self.current_round % settings.ITEM_SPAWN_PERIOD != 0: return
        if self._incoming_items is not None:
            # Time to spawn some items.
            self.new_items = self._incoming_items
            for x in range(settings.MAP_SIZE[0]):
                for y in range(settings.MAP_SIZE[1]):
                    if settings.OVERLAP_ITEMS:
                        self.items_map[x][y].extend(self.new_items[x][y])
                    else:
                        if self.new_items[x][y]:
                            self.items_map[x][y] = self.new_items[x][y]
        # Set the new incoming items.
        grid_noise = [[-1 for __ in range(settings.MAP_SIZE[1])] for _ in range(settings.MAP_SIZE[0])]
        self._incoming_items = [[[] for __ in range(settings.MAP_SIZE[1])] for _ in range(settings.MAP_SIZE[0])]
        for item in self.all_items:
            z = random.random() * 10000
            for x in range(settings.MAP_SIZE[0]):
                for y in range(settings.MAP_SIZE[1]):
                    if not self.cell_available(x, y):
                        continue
                    grid_noise[x][y] = self.noise_gen.noise3d(x * item.NOISE_MULT, y * item.NOISE_MULT, z)
                    for a, b in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
                        if grid_noise[x][y] < self.noise_gen.noise3d(a * item.NOISE_MULT, b * item.NOISE_MULT, z) + item.SPAWN_DIFF:
                            break
                    else:
                        if settings.OVERLAP_ITEMS:
                            self._incoming_items[x][y].append(item())
                        else:
                            self._incoming_items[x][y] = [item()]

    def update_heatmap(self):
        """
        Return a 2d list with the shape of the game map for heatmap
        """
        self.heatmap = [[0 for __ in range(settings.MAP_SIZE[1])] for _ in range(settings.MAP_SIZE[0])]
        target_distance = 1 + ((settings.ITEM_SPAWN_PERIOD - 1 - self.current_round % settings.ITEM_SPAWN_PERIOD) * settings.HEATMAP_LARGEST_DISTANCE) // settings.ITEM_SPAWN_PERIOD
        # Target distance will start off as HEATMAP_LARGEST_DISTANCE, then taper off to 1.
        for x in range(settings.MAP_SIZE[0]):
            for y in range(settings.MAP_SIZE[1]):
                if not self.cell_available(x, y):
                    continue
                for a in range(settings.MAP_SIZE[0]):
                    for b in range(settings.MAP_SIZE[1]):
                        dist = abs(x-a) + abs(y-b)
                        if dist < target_distance:
                            self.heatmap[x][y] += (sum(item.points for item in self._incoming_items[a][b]) / (pow(dist + 1, 3)))

                self.heatmap[x][y] = float("{:.2f}".format(self.heatmap[x][y]))

    def transport_random(self, player):
        row, col = random.randint(0, self.map_size[0] - 1), random.randint(0, self.map_size[1] - 1)
        while not self.cell_available(row, col):
            row, col = random.randint(0, self.map_size[0] - 1), random.randint(0, self.map_size[1] - 1)
        player.update_location(row, col)

    def finish_turn(self, wagers_obj=None):
        recap = {
            'type': 'tick',
            'heatmap': self.heatmap,
            'positions': [{
                'new_pos': self.players[i].location,
                'delta': self.players[i].last_move
            } for i in range(2)],
            'items': [[[y.short_name for y in position] for position in sublist] for sublist in self.items_map],
            'bike': [
                self.players[i].using_bike
                for i in range(2)
            ],
            'teleport': [
                self.players[i].using_portal_gun
                for i in range(2)
            ],
            'scores': [
                self.players[i].score
                for i in range(2)
            ],
            'remaining_rounds': self.total_rounds - self.current_round
        }
        if wagers_obj is not None:
            recap.update({
                'wagers': wagers_obj['wagers'],
                'positions': [{
                    'new_pos': wagers_obj['before_positions'][i],
                    'delta': self.players[i].last_move
                } for i in range(2)],
                'wager_positions': [self.players[i].location for i in range(2)]
            })
        replay(recap)
        self.current_round += 1
