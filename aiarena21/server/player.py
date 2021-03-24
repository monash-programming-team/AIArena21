import random
import string
import re


class Player:
    def __init__(self, name, address):
        self.token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.name = name
        self.address = address
        self.score = 100
        self.location = (0, 0)
        self.remaining_bikes = 0
        self.remaining_portal_guns = 0
        self.last_move = None

    @property
    def using_bike(self):
        return self.remaining_bikes > 0

    @property
    def using_portal_gun(self):
        return self.remaining_portal_guns > 0

    def update_powerups(self):
        self.remaining_portal_guns = max(0, self.remaining_portal_guns - 1)
        self.remaining_bikes = max(0, self.remaining_bikes - 1)

    def equip_bike(self, game):
        if self.score >= game.bike_cost:
            self.score -= game.bike_cost
            self.remaining_bikes += game.bike_turns
            return True
        else:
            return False

    def equip_portal_gun(self, game):
        if self.score >= game.portal_gun_cost:
            self.score -= game.portal_gun_cost
            self.remaining_portal_guns += game.portal_gun_turns
            return True
        else:
            return False

    def update_location(self, row, col, update_move=False):
        if update_move:
            self.last_move = (row-self.location[0], col-self.location[1])
        self.location = (row, col)

    def play_move(self, game, move):
        location_reg = re.compile(r'([0-9]+),([0-9]+)')
        if type(move) == str and location_reg.fullmatch(move):
            row, col = map(int, location_reg.fullmatch(move).groups())
            if not game.cell_available(row, col):
                self.last_move = (0, 0)
                print(f'Location sent from {self.name} is unavailable: {move}')
                return
            dist = abs(row - self.location[0]) + abs(col - self.location[1])
            if dist <= 1:
                self.update_location(row, col, True)
            elif dist <= game.bike_length and self.using_bike:
                if game.path_available(self.location, (row, col), game.bike_length):
                    self.update_location(row, col, True)
                else:
                    self.last_move = (0, 0)
                    print(f'{self.name} wants to go to {move} but the path is blocked by #s.')
                    return
            elif self.using_portal_gun:
                self.update_location(row, col, True)
            else:
                self.last_move = (0, 0)
                print(f'{self.name} does not have enough powerups to go to {move}')
        else:
            self.last_move = (0, 0)
            print(f'Invalid move sent from {self.name}: {move}')

    def pickup_items(self, game):
        for item in game.items_map[self.location[0]][self.location[1]]:
            self.score += item.points
        game.items_map[self.location[0]][self.location[1]] = []


players = []
