class Player:
    def __init__(self, name, dict_object):
        self.name = name
        self.score = int(dict_object['score'])
        self.bike = bool(dict_object['bike'])
        self.portal_gun = bool(dict_object['portal_gun'])
        self.location = dict_object['location']


class Map:
    BLOCK_CHAR = '#'
    SPAWN_CHAR = 'S'
    FREE_CHAR = '.'

    def __init__(self, map_size, tuple_object):
        self.size = map_size
        self.rows = map_size[0]
        self.cols = map_size[1]
        self._map = tuple_object

    def get(self, row, col):
        return self._map[row][col]

    def is_free(self, row, col):
        return self.get(row, col) != self.BLOCK_CHAR
