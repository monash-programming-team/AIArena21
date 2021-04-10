from aiarena21.client.classes import Player, Map


class TransportModes:
    WALK = 1
    BIKE = 2


class Bot:
    CUTOFF = 12
    GAMMA = 0.6

    @staticmethod
    def div_up(a, b):
        return max(0, (a + b - 1) // b)

    @staticmethod
    def discount(value, distance, bike=False, factor_bike_cost=True):
        if not bike:
            if distance > Bot.CUTOFF:
                return 0
            return value * Bot.GAMMA ** distance
        else:
            bike_cost = Bot.div_up(distance, 9) * 30
            steps = Bot.div_up(distance, 3)
            return max(
                0,
                value * Bot.GAMMA ** steps - bike_cost * factor_bike_cost * 0,
            )

    @staticmethod
    def distance(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    @staticmethod
    def up(point, rmax, cmax):
        if not point[0]:
            return None
        return (point[0] - 1, point[1])

    @staticmethod
    def right(point, rmax, cmax):
        if point[1] >= cmax - 1:
            return None
        return (point[0], point[1] + 1)

    @staticmethod
    def down(point, rmax, cmax):
        if point[0] >= rmax - 1:
            return None
        return (point[0] + 1, point[1])

    @staticmethod
    def left(point, rmax, cmax):
        if not point[1]:
            return None
        return (point[0], point[1] - 1)

    def __init__(self):
        self.values = None

    def compute_values(self, gmap: Map, items: list, heatmap: list):
        # Map.size is rows,cols
        self.values = [[0] * gmap.size[1] for _ in range(gmap.size[0])]
        self.bike_values = [[0] * gmap.size[1] for _ in range(gmap.size[0])]
        self.bike_free_values = [
            [0] * gmap.size[1] for _ in range(gmap.size[0])
        ]
        self.best_values = [[0] * gmap.size[1] for _ in range(gmap.size[0])]
        self.best_modes = [[0] * gmap.size[1] for _ in range(gmap.size[0])]
        for r, row in enumerate(items):
            for c, val in enumerate(row):
                if not val:
                    continue
                self.propagate_value(gmap, val, r, c)
        for r in range(gmap.size[0]):
            for c in range(gmap.size[1]):
                v_walk = self.values[r][c]
                self.bike_values[r][c] -= 30
                v_bike = self.bike_values[r][c]
                if v_walk >= v_bike:
                    self.best_modes[r][c] = TransportModes.WALK
                    self.best_values[r][c] = v_walk
                else:
                    self.best_modes[r][c] = TransportModes.BIKE
                    self.best_values[r][c] = v_bike

    def propagate_value(self, gmap: Map, value: int, r: int, c: int):
        visited = [[False] * gmap.size[1] for _ in range(gmap.size[0])]
        # Breadth first walk
        edges = [(r, c)]
        depth = 0
        directions = [Bot.up, Bot.right, Bot.down, Bot.left]
        while edges and depth < Bot.CUTOFF:
            new_edges = []
            for edge in edges:
                for direction in directions:
                    pos = direction(edge, gmap.size[0], gmap.size[1])
                    if pos is None:
                        continue
                    r, c = pos
                    if not gmap.is_free(r, c):
                        continue
                    if visited[r][c]:
                        continue
                    visited[r][c] = True
                    self.values[r][c] += Bot.discount(value, depth)
                    self.bike_values[r][c] += Bot.discount(value, depth, True)
                    self.bike_free_values[r][c] += Bot.discount(
                        value, depth, True, False
                    )
                    new_edges.append(pos)
            depth += 1
            edges = new_edges

    def play_powerup(
        self,
        gmap: Map,
        us: Player,
        them: Player,
        items: list,
        new_items: list,
        heatmap: list,
        remaining_turns: int,
    ):
        self.compute_values(gmap, items, heatmap)
        if us.bike:
            return ""
        r, c = us.location
        # print(self.best_modes[r][c])
        # print(self.best_values[r][c])
        # print("v", self.values[r][c])
        # print("b", self.bike_values[r][c])
        if self.best_modes[r][c] == TransportModes.BIKE:
            # print("bike!", us.bike, us.score)
            return ""
        if not self.best_values[r][c]:
            # print("yayayayaya")
            return "portal gun"
        return ""

    def play_turn(
        self,
        gmap: Map,
        us: Player,
        them: Player,
        items: list,
        new_items: list,
        heatmap: list,
        remaining_turns: int,
    ):
        if us.bike:
            scores = []
            for dr in range(-3, 4):
                for dc in range(-3, 4):
                    if not dc and not dr:
                        continue
                    if abs(dc) + abs(dr) > 3:
                        continue
                    pos = us.location[0] + dr, us.location[1] + dc
                    if not (0 <= pos[0] < gmap.size[0]):
                        continue
                    if not (0 <= pos[1] < gmap.size[1]):
                        continue
                    r, c = pos
                    bonus = items[r][c] * 10000
                    # print('BB~', bonus)
                    scores.append((pos, self.bike_free_values[r][c] + bonus))
            best = float("-inf")
            best_ind = -1
            for i, score in enumerate(scores):
                if score[1] > best or best_ind == -1:
                    best = score[1]
                    best_ind = i
            # print('BB', best)
            r, c = scores[best_ind][0]
            # print('BB', scores[best_ind][1])
            # print('B?', items[r][c])
            return f"{r},{c}"
        if us.portal_gun:
            # Find the best square
            best = float("-inf")
            best_ind = -1
            for r in range(gmap.size[0]):
                for c in range(gmap.size[1]):
                    if best_ind == -1 or self.best_values[r][c] > best:
                        best_ind = (r, c)
            r, c = best_ind
            return f"{r},{c}"
        directions = [Bot.up, Bot.right, Bot.down, Bot.left]
        scores = []
        for direction in directions:
            pos = direction(us.location, gmap.size[0], gmap.size[1])
            if pos is None:
                scores.append(-1)
                continue
            r, c = pos
            if not gmap.is_free(r, c):
                scores.append(-1)
                continue
            scores.append(self.values[r][c])
            if items[r][c]:
                scores[-1] += items[r][c] * 1000
        best = max(scores)
        best_ind = scores.index(best)
        # print(best)
        goto = directions[best_ind](us.location, gmap.size[0], gmap.size[1])
        return f"{goto[0]},{goto[1]}"

    def play_auction(
        self,
        gmap: Map,
        us: Player,
        them: Player,
        items: list,
        new_items: list,
        heatmap: list,
        remaining_turns: int,
    ):
        return 1

    def play_transport(
        self,
        gmap: Map,
        us: Player,
        them: Player,
        items: list,
        new_items: list,
        heatmap: list,
        remaining_turns: int,
    ):
        # Find worst
        worst = float("inf")
        worst_place = None
        for r in range(gmap.size[0]):
            for c in range(gmap.size[1]):
                if not gmap.is_free(r, c):
                    continue
                if worst_place is None or self.values[r][c] < worst:
                    worst = self.values[r][c]
                    worst_place = r, c
        r, c = worst_place
        return f"{r},{c}"


_b = Bot()
play_powerup = _b.play_powerup
play_turn = _b.play_turn
play_auction = _b.play_auction
play_transport = _b.play_transport
