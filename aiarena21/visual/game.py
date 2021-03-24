import os
import pygame

import collections
import aiarena21.visual.constants as constants
from aiarena21.visual.screen import ScreenManager
from aiarena21.visual.utils import interpolate_colour_discrete
import json

from aiarena21.visual.game_input import get_input, use_file as use_file_for_input

this_dir = os.path.dirname(os.path.abspath(__file__))
f = lambda s: os.path.join(this_dir, s)

class GameStateHandler:

    # Timing constants
    TICK_RATE = 30
    GAME_RATE = 3
    ANIM_RATE = 3

    DIRECTION_UP = "UP"
    DIRECTION_DOWN = "DOWN"
    DIRECTION_RIGHT = "RIGHT"
    DIRECTION_LEFT = "LEFT"

    MOVE_MAPPING = {
        DIRECTION_UP: {
            "sprites": ([2] * int(TICK_RATE // ANIM_RATE)) + ([5] * int(TICK_RATE // ANIM_RATE)),
            "flipped": ([False] * int(TICK_RATE // ANIM_RATE)) + ([True] * int(TICK_RATE // ANIM_RATE)),
        },
        DIRECTION_DOWN: {
            "sprites": ([0] * int(TICK_RATE // ANIM_RATE)) + ([4] * int(TICK_RATE // ANIM_RATE)),
            "flipped": ([False] * int(TICK_RATE // ANIM_RATE)) + ([True] * int(TICK_RATE // ANIM_RATE)),
        },
        DIRECTION_LEFT: {
            "sprites": ([3] * int(TICK_RATE // ANIM_RATE)) + ([0] * int(TICK_RATE // ANIM_RATE)),
            "flipped": True,
        },
        DIRECTION_RIGHT: {
            "sprites": ([3] * int(TICK_RATE // ANIM_RATE)) + ([0] * int(TICK_RATE // ANIM_RATE)),
            "flipped": False,
        },
    }

    PLAYER_TRAIL = 5

    ITEM_ORDERING = [
        "O",
        "S",
        "D",
    ]

    def __init__(self):
        GameStateHandler.instance = self

    @classmethod
    def init(cls):
        while True:
            line = get_input()
            if line.startswith("[Replay]"): break
        cls.instance.start_payload = json.loads(line[8:])
        assert cls.instance.start_payload["type"] == "init", "Wrong payload encountered in game."
        cls.grid_defn = cls.instance.start_payload["grid"]
        ScreenManager()
        ScreenManager.createScreen()
        cls.start_grid = [[
            constants.COLORS[20] if x == "x" else constants.GREYSCALE[0]
            for x in y
        ] for y in cls.grid_defn]
        ScreenManager.initGrid(cls.start_grid)
        for x in range(len(cls.grid_defn)):
            for y in range(len(cls.grid_defn[0])):
                if cls.grid_defn[x][y] == '#':
                    ScreenManager.setGridColour(x, y, '#000000')
        ScreenManager.instance.REMAINING_TIME = cls.instance.start_payload["total_rounds"]
        ScreenManager.setScores(*cls.instance.start_payload["scores"], diff=False)
        ScreenManager.setNames(*cls.instance.start_payload["teams"])
        cls.spawnPlayers()
        ScreenManager.setSpritePaths({
            "portal1": [f("sprites/tp/tile009.png")] + [f(f"sprites/tp/tile0{x}.png") for x in range(10, 24)],
            "portal2": [f("sprites/tp/tile009.png")] + [f(f"sprites/tp/tile0{x}.png") for x in range(10, 24)],
            "p1": [
                f("sprites/p1/down.png"), 
                f("sprites/p1/down.png"), 
                f("sprites/p1/up.png"), 
                f("sprites/p1/side.png"), 
                f("sprites/p1/down.png"), 
                f("sprites/p1/up.png"), 
                f("sprites/p1/stand.png"),
            ],
            "p2": [
                f("sprites/p2/down.png"), 
                f("sprites/p2/down.png"), 
                f("sprites/p2/up.png"), 
                f("sprites/p2/side.png"), 
                f("sprites/p2/down.png"), 
                f("sprites/p2/up.png"), 
                f("sprites/p2/stand.png"),
            ],
        })
        ScreenManager.setItemPaths({
            "O": f("sprites/food/Onion.png"),
            "S": f("sprites/food/Strawberry.png"),
            "D": f("sprites/food/DragonFruit.png"),
        })
        ScreenManager.instance.playing["p1"] = "repeat"
        ScreenManager.instance.playing["p2"] = "repeat"
        ScreenManager.setSpriteIndex("portal1", [x//2 for x in range(30)])
        ScreenManager.setSpriteIndex("portal2", [x//2 for x in range(30)])

    @classmethod
    def spawnPlayers(cls):
        cls.instance.player_trails = [[], []]
        cls.instance.player_positions = {
            "p1": cls.instance.start_payload["spawn"][0],
            "p2": cls.instance.start_payload["spawn"][1],
        }

    @classmethod
    def mainLoop(cls):
        last_game = time.time()
        last_visual = time.time() - 1
        while True:
            c_time = time.time()
            if c_time - last_game > 1 / cls.GAME_RATE and not ScreenManager.instance.in_wager:
                last_game = c_time
                GameStateHandler.tick()
            if c_time - last_visual > 1 / cls.TICK_RATE:
                ScreenManager.mainLoopTick()


    @classmethod
    def tick(cls):
        try:
            while True:
                line = get_input()
                if line.startswith("[Replay]"): break
        except:
            import sys, pygame
            print("Replay over.")
            pygame.quit()
            sys.exit(0)
        payload = json.loads(line[8:])
        if payload["type"] == "finish":
            import sys, pygame
            print("Replay over.")
            pygame.quit()
            sys.exit(0)
        assert payload["type"] == "tick", "Wrong payload encountered in game."
        # Heatmap
        for x in range(len(payload["heatmap"])):
            for y in range(len(payload["heatmap"][x])):
                if cls.grid_defn[x][y] != '#':
                    ScreenManager.setGridColour(x, y, interpolate_colour_discrete(constants.POINT_GRADIENT[:0:-1], 2.5, 0, payload["heatmap"][x][y]))
        # Items
        positions = collections.defaultdict(list)
        for x in range(len(payload["items"])):
            for y in range(len(payload["items"][x])):
                if not payload["items"][x][y]: continue
                best_item_index = -1
                for item in payload["items"][x][y]:
                    best_item_index = max(best_item_index, cls.ITEM_ORDERING.index(item))
                positions[cls.ITEM_ORDERING[best_item_index]].append([x, y])
        ScreenManager.setItemPositions(positions)
        cls.instance.player_positions = {f"p{i+1}": x["new_pos"] for i, x in enumerate(payload["positions"])}
        if "wagers" in payload:
            ScreenManager.drawWager(*payload["wagers"], *[obj["new_pos"] for obj in payload["positions"]], *payload["scores"], *payload["wager_positions"])
        else:
            for x in range(2):
                if payload["bike"][x] != ("bike" in ScreenManager.instance.sprite_paths[f"p{x+1}"][0]):
                    ScreenManager.toggleBikeMode(f"p{x+1}")
                if payload["teleport"][x]:
                    cls.instance.sprite_positions[f"portal{x+1}"] = cls.instance.player_positions[x]
                    cls.instance.playing[f"portal{x+1}"] = "single"
            for x in range(2):
                dx, dy = payload["positions"][x]["delta"]
                if abs(dx) >= abs(dy):
                    if dx >= 0:
                        move = cls.DIRECTION_DOWN
                    else:
                        move = cls.DIRECTION_UP
                else:
                    if dy > 0:
                        move = cls.DIRECTION_RIGHT
                    elif dy < 0:
                        move = cls.DIRECTION_LEFT
                    else:
                        move = None
                obj = cls.instance.MOVE_MAPPING.get(move, {})
                ScreenManager.setSpriteIndex(f"p{x+1}", obj.get("sprites", [6]), obj.get("flipped", False))
            ScreenManager.setScores(*payload["scores"])
        ScreenManager.setSpritePositions(cls.instance.player_positions)
        # Handle player trails
        for x in range(2):
            cls.instance.player_trails[x].insert(0, cls.instance.player_positions[f"p{x+1}"])
            cls.instance.player_trails[x] = cls.instance.player_trails[x][:cls.instance.PLAYER_TRAIL]
        ScreenManager.clearTints()
        colours = [
            constants.TEAM_1_PALLETE[0],
            constants.TEAM_2_PALLETE[0],
        ]
        for x in range(2):
            for i, (a, b) in enumerate(cls.instance.player_trails[x][::-1]):
                strength = int((i + cls.instance.PLAYER_TRAIL - len(cls.instance.player_trails[x])) * 255 / (cls.instance.PLAYER_TRAIL - 1))
                ScreenManager.addTint(a, b, colours[x], strength)
        # Scores
        ScreenManager.instance.REMAINING_TIME = payload['remaining_rounds']


if __name__ == "__main__":
    import time
    os.environ["SDL_VIDEO_CENTERED"] = "1"  # You have to call this before pygame.init()

    use_file_for_input('replay.txt')

    pygame.init()

    GameStateHandler()
    GameStateHandler.init()
    GameStateHandler.mainLoop()