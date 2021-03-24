class Item:

    # Lower mult = Less clumped and less spawns.
    NOISE_MULT = 0.5
    # Bigger diff = less spawns.
    SPAWN_DIFF = 0.01

    def __init__(self, name, points):
        self.name = name
        self.short_name = self.name[0]
        self.points = points


# TODO: Tinker with NOISE_MULT and SPAWN_DIFF for each item once it's hooked up to visuals.

class Item1(Item):
    NOISE_MULT = 0.75
    SPAWN_DIFF = 0.03

    def __init__(self):
        super(Item1, self).__init__('Onion', 2)


class Item2(Item):
    NOISE_MULT = 1
    SPAWN_DIFF = 0.3

    def __init__(self):
        super(Item2, self).__init__('Strawberry', 10)


class Item3(Item):
    NOISE_MULT = 4
    SPAWN_DIFF = 0.55

    def __init__(self):
        super(Item3, self).__init__('DragonFruit', 30)

