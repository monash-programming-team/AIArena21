import pygame, os
import pygame.gfxdraw
import pygame.freetype
import random
import platform

import aiarena21.visual.constants as constants
from pygame.constants import RESIZABLE

this_dir = os.path.dirname(os.path.abspath(__file__))
f = lambda s: os.path.join(this_dir, s)

class ScreenManager:

    instance: "ScreenManager"

    fullscreen = False
    windowed_res = (1440, 760)

    BG_COLOR = constants.GREYSCALE[-1]
    GRID_COLOR = constants.COLORS[20]

    # Margins are LRUD
    GRID_MARGIN = lambda self, s: (50, 50, 0, 50)
    HEADER_MARGIN = lambda self, s: (30, 30, 20, 40)
    DIALOG_MARGIN = lambda self, s: (s[0]/4, s[0]/4, s[1]/6, s[1]/6)

    GRID_WIDTH = 30
    GRID_HEIGHT = 20
    GRID_SQUARE_MARGIN = 5
    SPRITE_MARGIN = 2

    TIME_MARGIN = 15
    POWER_UP_SIZE = 30
    # SIDE, UP
    POWER_UP_MARGIN = (10, 10)

    TEAM_NAME_1 = "Team 1"
    TEAM_NAME_2 = "Team 2"

    WIN_COLOR = constants.COLORS[5]
    LOSS_COLOR = constants.COLORS[28]

    TEAM_SCORE_1 = 0
    TEAM_DIFF_1 = 0
    TEAM_SCORE_2 = 0
    TEAM_DIFF_2 = 0

    REMAINING_TIME = 250

    # Font scales are designed for 1920 * 1080 screens
    FONT_SCALE = 1920

    WAGER_TICKS = 60

    def __init__(self):
        ScreenManager.instance = self

    @classmethod
    def createScreen(cls):
        pygame.display.set_caption("Monash Food Rush")
        info = pygame.display.Info()
        cls.instance.start_info = [
            info.current_w,
            info.current_h - (80 if platform.system() != "Windows" else 0), # This seems to be required because the chrome of the window is not taken into account.
        ]
        cls.instance.screen = pygame.display.set_mode(cls.instance.windowed_res, RESIZABLE)
        if cls.instance.fullscreen:
            cls.toggleFullscreen()

    @classmethod
    def initGrid(cls, grid_data):
        cls.instance.GRID_WIDTH = len(grid_data[0])
        cls.instance.GRID_HEIGHT = len(grid_data)
        cls.instance.grid_data = grid_data
        cls.clearTints()
        cls.instance.in_wager = False

    @classmethod
    def clearTints(cls):
        cls.instance.tint_data = [[pygame.Color("#ffffff00") for _ in range(len(cls.instance.grid_data[0]))] for __ in range(len(cls.instance.grid_data))]

    @classmethod
    def addTint(cls, x, y, colour, strength):
        cls.instance.tint_data[x][y] = pygame.Color(colour)
        cls.instance.tint_data[x][y].a = strength

    @classmethod
    def setSpritePaths(cls, paths):
        cls.instance.sprite_paths = {key: [path for path in player] for key, player in paths.items()}
        cls.instance.sprites = {key: [pygame.image.load(path) for path in player] for key, player in paths.items()}
        cls.instance.sprite_indicies = {key:0 for key in paths}
        cls.instance.sprite_options = {key: [0] for key in paths}
        cls.instance.sprite_positions = {key: [0, 0] for key in paths}
        cls.instance.flipped = {key: [False for _ in player] for key, player in paths.items()}
        cls.instance.playing = {key: False for key in paths}

    @classmethod
    def setItemPaths(cls, paths):
        cls.instance.item_paths = {key: item for key, item in paths.items()}
        cls.instance.item_sprites = {key: pygame.image.load(item) for key, item in paths.items()}
        cls.instance.item_positions = {key: [] for key in paths}
        cls.instance.item_index = 0
        cls.instance.item_rotated = False
        cls.instance.item_rotate_time = 10

    @classmethod
    def setItemPositions(cls, positions):
        cls.instance.item_positions.update(positions)

    @classmethod
    def setSpritePositions(cls, positions):
        cls.instance.sprite_positions.update(positions)

    @classmethod
    def setSpriteIndex(cls, playerKey, indicies, flipped=False):
        different = len(cls.instance.sprite_options[playerKey]) != len(indicies)
        if not different:
            for x in range(len(indicies)):
                if indicies[x] != cls.instance.sprite_options[playerKey][x]:
                    different = True
                    break
        if different:
            cls.instance.sprite_indicies[playerKey] = 0
            cls.instance.sprite_options[playerKey] = indicies
        for i, index in enumerate(indicies):
            f = flipped[i] if isinstance(flipped, list) else flipped
            if f != cls.instance.flipped[playerKey][index]:
                cls.instance.flipped[playerKey][index] = f
                cls.instance.sprites[playerKey][index] = pygame.transform.flip(cls.instance.sprites[playerKey][index], True, False)

    @classmethod
    def setNames(cls, team1, team2):
        cls.instance.TEAM_NAME_1 = team1
        cls.instance.TEAM_NAME_2 = team2

    @classmethod
    def setScores(cls, score1, score2, diff=True):
        if diff:
            cls.instance.TEAM_DIFF_1 = score1 - cls.instance.TEAM_SCORE_1
            cls.instance.TEAM_DIFF_2 = score2 - cls.instance.TEAM_SCORE_2
        else:
            cls.instance.TEAM_DIFF_1 = 0
            cls.instance.TEAM_DIFF_2 = 0
        cls.instance.TEAM_SCORE_1 = score1
        cls.instance.TEAM_SCORE_2 = score2

    @classmethod
    def toggleBikeMode(cls, playerKey):
        if "bike" in cls.instance.sprite_paths[playerKey][0]:
            cls.instance.sprite_paths[playerKey] = [v.replace("_bike", "") for v in cls.instance.sprite_paths[playerKey]]
        else:
            cls.instance.sprite_paths[playerKey] = [v.replace(".png", "_bike.png") for v in cls.instance.sprite_paths[playerKey]]
        cls.instance.sprites[playerKey] = [pygame.image.load(path) for path in cls.instance.sprite_paths[playerKey]]
        cls.instance.flipped[playerKey] = [False] * len(cls.instance.sprites[playerKey])

    @classmethod
    def reloadSprites(cls):
        for key in cls.instance.sprite_paths:
            cls.instance.sprites[key] = [pygame.image.load(path) for path in cls.instance.sprite_paths[key]]
            cls.instance.flipped[key] = [False] * len(cls.instance.sprites[key])

    @classmethod
    def toggleFullscreen(cls):
        if cls.instance.fullscreen:
            cls.instance.old_info = pygame.display.Info()
            # Just a big screen
            cls.instance.screen = pygame.display.set_mode(
                cls.instance.start_info, RESIZABLE
            )
        if platform.system() == "Windows":
            pygame.display.toggle_fullscreen()
        if not cls.instance.fullscreen:
            if hasattr(cls.instance, "old_info"):
                size = (cls.instance.old_info.current_w, cls.instance.old_info.current_h)
            else:
                size = cls.instance.windowed_res
            cls.instance.screen = pygame.display.set_mode(size, RESIZABLE)

    @classmethod
    def keys(cls):
        return pygame.key.get_pressed()

    @classmethod
    def mainLoopTick(cls, update=True):
        cls.handleEvents()
        cls.instance.screen.fill(cls.instance.BG_COLOR)
        
        size = cls.instance.screen.get_size()
        pref_ratio = cls.instance.GRID_WIDTH / cls.instance.GRID_HEIGHT
        header_height = max(120, size[1] / 8)
        max_time_width = size[0] / 6
        min_time_width = max_time_width - 100
        
        allowed_size = (
            size[0] - cls.instance.GRID_MARGIN(size)[0] - cls.instance.GRID_MARGIN(size)[1],
            size[1] - cls.instance.GRID_MARGIN(size)[2] - cls.instance.GRID_MARGIN(size)[3] - header_height - cls.instance.HEADER_MARGIN(size)[2] - cls.instance.HEADER_MARGIN(size)[3],
        )
        allowed_size = (
            int(min(allowed_size[0], allowed_size[1] * pref_ratio)),
            int(min(allowed_size[1], allowed_size[0] / pref_ratio)),
        )
        grid = pygame.Surface(allowed_size)
        grid.fill(cls.instance.GRID_COLOR)

        grid_point = (size[0]/2 - allowed_size[0]/2, size[1] - allowed_size[1] - cls.instance.GRID_MARGIN(size)[3])
        cls.instance.screen.blit(grid, grid_point)

        # Draw grid
        sq_size = (allowed_size[0] - cls.instance.GRID_SQUARE_MARGIN) / cls.instance.GRID_WIDTH - cls.instance.GRID_SQUARE_MARGIN
        for x in range(cls.instance.GRID_HEIGHT):
            for y in range(cls.instance.GRID_WIDTH):
                sq = pygame.Surface((sq_size, sq_size))
                c1 = pygame.Color(cls.instance.grid_data[x][y])
                c2 = cls.instance.tint_data[x][y]
                prop = c2.a / 255
                new_c = pygame.Color(
                    f"#{int(c1.r + (c2.r - c1.r) * prop):2x}".replace(" ", "0") +
                    f"{int(c1.g + (c2.g - c1.g) * prop):2x}".replace(" ", "0") +
                    f"{int(c1.b + (c2.b - c1.b) * prop):2x}".replace(" ", "0")
                )
                sq.fill(new_c)
                draw_point = (
                    grid_point[0] + y * (sq_size + cls.instance.GRID_SQUARE_MARGIN) + cls.instance.GRID_SQUARE_MARGIN,
                    grid_point[1] + x * (sq_size + cls.instance.GRID_SQUARE_MARGIN) + cls.instance.GRID_SQUARE_MARGIN,
                )
                cls.instance.screen.blit(sq, draw_point)

        # Draw item sprites
        for key, positions in cls.instance.item_positions.items():
            for x, y in positions:
                margin = 0
                sprite_size = cls.instance.item_sprites[key].get_size()
                pref_size = (int(sq_size - margin * 2), int(sq_size - margin * 2))
                if sprite_size[0] != pref_size[0]:
                    cls.instance.item_sprites[key] = pygame.transform.scale(cls.instance.item_sprites[key], pref_size)
                draw_point = (
                    grid_point[0] + y * (sq_size + cls.instance.GRID_SQUARE_MARGIN) + cls.instance.GRID_SQUARE_MARGIN + margin,
                    grid_point[1] + x * (sq_size + cls.instance.GRID_SQUARE_MARGIN) + cls.instance.GRID_SQUARE_MARGIN + margin,
                )
                rot_surface = pygame.transform.rotate(cls.instance.item_sprites[key], 30 if cls.instance.item_rotated else 0)
                draw_point = (
                    draw_point[0] + (cls.instance.item_sprites[key].get_size()[0] - rot_surface.get_size()[0])/2,
                    draw_point[1] + (cls.instance.item_sprites[key].get_size()[1] - rot_surface.get_size()[1])/2,
                )
                cls.instance.screen.blit(rot_surface, draw_point)
        cls.instance.item_index += 1
        if cls.instance.item_rotate_time == cls.instance.item_index:
            cls.instance.item_index = 0
            cls.instance.item_rotated = not cls.instance.item_rotated
        # Draw player sprites
        for key, sprite_index in cls.instance.sprite_indicies.items():
            if cls.instance.playing[key] is False: continue
            margin = cls.instance.SPRITE_MARGIN if key in ["p1", "p2"] else -8*cls.instance.SPRITE_MARGIN
            sprite_size = cls.instance.sprites[key][cls.instance.sprite_options[key][sprite_index]].get_size()
            pref_size = (int(sq_size - margin * 2), int(sq_size - margin * 2))
            if sprite_size[0] != pref_size[0]:
                cls.instance.sprites[key][cls.instance.sprite_options[key][sprite_index]] = pygame.transform.scale(cls.instance.sprites[key][cls.instance.sprite_options[key][sprite_index]], pref_size)
            draw_point = (
                grid_point[0] + cls.instance.sprite_positions[key][1] * (sq_size + cls.instance.GRID_SQUARE_MARGIN) + cls.instance.GRID_SQUARE_MARGIN + margin,
                grid_point[1] + cls.instance.sprite_positions[key][0] * (sq_size + cls.instance.GRID_SQUARE_MARGIN) + cls.instance.GRID_SQUARE_MARGIN + margin,
            )
            cls.instance.screen.blit(cls.instance.sprites[key][cls.instance.sprite_options[key][sprite_index]], draw_point)
            cls.instance.sprite_indicies[key] += 1
            if cls.instance.sprite_indicies[key] == len(cls.instance.sprite_options[key]):
                cls.instance.sprite_indicies[key] = 0
                if cls.instance.playing[key] == "single":
                    cls.instance.playing[key] = False

        # Draw header
        p1 = pygame.Surface((
            (size[0] - cls.instance.HEADER_MARGIN(size)[0] - cls.instance.HEADER_MARGIN(size)[1]) / 2,
            header_height
        ))
        p1.fill(cls.instance.BG_COLOR)
        p2 = pygame.Surface((
            (size[0] - cls.instance.HEADER_MARGIN(size)[0] - cls.instance.HEADER_MARGIN(size)[1]) / 2,
            header_height
        ))
        p2.fill(cls.instance.BG_COLOR)
        header_size = p1.get_size()
        rect_height = header_size[1] - cls.instance.POWER_UP_SIZE - cls.instance.POWER_UP_MARGIN[1]
        header_bottom_width = max_time_width + (min_time_width - max_time_width) * (rect_height / header_size[1])
        rect_top_width = header_size[0] - max_time_width/2 - cls.instance.TIME_MARGIN
        rect_bot_width = header_size[0] - header_bottom_width/2 - cls.instance.TIME_MARGIN
        # Background
        pygame.gfxdraw.filled_polygon(p1, [
            (0, 0),
            (rect_top_width, 0),
            (rect_bot_width, rect_height),
            (0, rect_height),
        ], pygame.Color(constants.TEAM_1_PALLETE[1]))
        pygame.gfxdraw.filled_polygon(p2, [
            (header_size[0], 0),
            (header_size[0] - rect_top_width, 0),
            (header_size[0] - rect_bot_width, rect_height),
            (header_size[0], rect_height),
        ], pygame.Color(constants.TEAM_2_PALLETE[1]))
        # Team Names
        title_font = pygame.freetype.Font(f("fonts/Montserrat/Montserrat-Medium.ttf"), 56 * cls.instance.screen.get_size()[0] / cls.instance.FONT_SCALE)
        title_font.render_to(p1, (10, 10), cls.instance.TEAM_NAME_1, constants.GREYSCALE[0])
        p2_title_size = title_font.render(cls.instance.TEAM_NAME_2, constants.GREYSCALE[0])[1].width
        title_font.render_to(p2, (header_size[0] - p2_title_size - 10, 10), cls.instance.TEAM_NAME_2, constants.GREYSCALE[0])
        # Score
        score_font = pygame.freetype.Font(f("fonts/Montserrat/Montserrat-Bold.ttf"), 56 * cls.instance.screen.get_size()[0] / cls.instance.FONT_SCALE)
        score_1_rect = score_font.render(str(cls.instance.TEAM_SCORE_1), constants.GREYSCALE[0])[1]
        score_2_rect = score_font.render(str(cls.instance.TEAM_SCORE_2), constants.GREYSCALE[0])[1]
        shift_amount = 0.3
        score_font.render_to(
            p1,
            ((rect_top_width * (1 - shift_amount) + rect_bot_width * shift_amount) - 30 - score_1_rect.width, rect_height * shift_amount - score_1_rect.height / 2),
            str(cls.instance.TEAM_SCORE_1), 
            constants.GREYSCALE[0],
        )
        score_font.render_to(
            p2,
            (header_size[0] - (rect_top_width * (1 - shift_amount) + rect_bot_width * shift_amount) + 30, rect_height * shift_amount - score_2_rect.height / 2),
            str(cls.instance.TEAM_SCORE_2), 
            constants.GREYSCALE[0],
        )
        # Score diff
        diff_font = pygame.freetype.Font(f("fonts/Montserrat/Montserrat-Light.ttf"), 36 * cls.instance.screen.get_size()[0] / cls.instance.FONT_SCALE)
        if cls.instance.TEAM_DIFF_1 != 0:
            string = ("+" if cls.instance.TEAM_DIFF_1 > 0 else "") + str(cls.instance.TEAM_DIFF_1)
            text_rect = diff_font.render(string, constants.GREYSCALE[0])[1]
            diff_font.render_to(
                p1, 
                (rect_bot_width - 40 - text_rect.width, rect_height - 10 - text_rect.height), 
                string, 
                cls.instance.WIN_COLOR if cls.instance.TEAM_DIFF_1 > 0 else cls.instance.LOSS_COLOR,
            )
        if cls.instance.TEAM_DIFF_2 != 0:
            string = ("+" if cls.instance.TEAM_DIFF_2 > 0 else "") + str(cls.instance.TEAM_DIFF_2)
            text_rect = diff_font.render(string, constants.GREYSCALE[0])[1]
            diff_font.render_to(
                p2, 
                (
                    header_size[0] - rect_bot_width + 40, 
                    rect_height - 10 - text_rect.height
                ), 
                string, 
                cls.instance.WIN_COLOR if cls.instance.TEAM_DIFF_2 > 0 else cls.instance.LOSS_COLOR,
            )

        cls.instance.screen.blit(p1, (cls.instance.HEADER_MARGIN(size)[0], cls.instance.HEADER_MARGIN(size)[2]))
        cls.instance.screen.blit(p2, (cls.instance.HEADER_MARGIN(size)[0] + header_size[0], cls.instance.HEADER_MARGIN(size)[2]))

        # Time
        time = pygame.Surface((max_time_width, header_height), pygame.SRCALPHA, 32)
        time = time.convert_alpha()
        pygame.gfxdraw.filled_polygon(time, [
            (0, 0),
            (max_time_width, 0),
            ((max_time_width + min_time_width)/2, header_height),
            ((max_time_width - min_time_width)/2, header_height),
        ], pygame.Color(constants.GREYSCALE[0]))
        time_font = pygame.freetype.Font(f("fonts/Montserrat/Montserrat-Bold.ttf"), 72 * cls.instance.screen.get_size()[0] / cls.instance.FONT_SCALE)
        time_rect = time_font.render(str(cls.instance.REMAINING_TIME), constants.GREYSCALE[4])[1]
        time_font.render_to(
            time,
            (max_time_width / 2 - time_rect.width / 2, header_height / 2 - time_rect.height / 2),
            str(cls.instance.REMAINING_TIME), 
            constants.GREYSCALE[4],
        )

        cls.instance.screen.blit(time, (cls.instance.HEADER_MARGIN(size)[0] + header_size[0] - max_time_width / 2, cls.instance.HEADER_MARGIN(size)[2]))

        if cls.instance.in_wager:
            left_happy = "happy" if cls.instance.wager_amount1 > cls.instance.wager_amount2 else "sad"
            right_happy = "happy" if cls.instance.wager_amount2 > cls.instance.wager_amount1 else "sad"

            size = cls.instance.screen.get_size()
            dialog = pygame.Surface((
                size[0] - cls.instance.DIALOG_MARGIN(size)[0] - cls.instance.DIALOG_MARGIN(size)[1],
                size[1] - cls.instance.DIALOG_MARGIN(size)[2] - cls.instance.DIALOG_MARGIN(size)[3]
            ))
            dialog.fill(constants.GREYSCALE[3])
            dialog_size = dialog.get_size()
            normal = cls.instance.wager_tick > 2 * cls.instance.WAGER_TICKS / 3
            left_sprite = pygame.transform.scale(pygame.image.load(f(f"sprites/p1/icon_{'normal' if normal else left_happy}.png")), (dialog_size[0]//4, dialog_size[0]//4))
            right_sprite = pygame.transform.scale(pygame.image.load(f(f"sprites/p2/icon_{'normal' if normal else right_happy}.png")), (dialog_size[0]//4, dialog_size[0]//4))
            dialog.blit(left_sprite, (dialog_size[0]//8, dialog_size[1]//4 - dialog_size[0]//8))
            dialog.blit(right_sprite, (5*dialog_size[0]//8, dialog_size[1]//4 - dialog_size[0]//8))
            if not normal:
                colour_tick = cls.instance.wager_tick % 20 < 10
                wager_font = pygame.freetype.Font(f("fonts/Montserrat/Montserrat-Bold.ttf"), 72 * size[0] / cls.instance.FONT_SCALE)
                wager_1_rect = wager_font.render(str(cls.instance.wager_amount1), constants.GREYSCALE[0])[1]
                wager_2_rect = wager_font.render(str(cls.instance.wager_amount2), constants.GREYSCALE[0])[1]
                wager_font.render_to(
                    dialog,
                    (dialog_size[0] / 4 - wager_1_rect.width / 2, 3 * dialog_size[1] / 4 - wager_1_rect.height / 2),
                    str(cls.instance.wager_amount1), 
                    (
                        constants.COLORS[5]
                        if left_happy == "happy" else
                        constants.COLORS[-1]
                    )
                    if colour_tick else
                    constants.GREYSCALE[0],
                )
                wager_font.render_to(
                    dialog,
                    (3 * dialog_size[0] / 4 - wager_2_rect.width / 2, 3 * dialog_size[1] / 4 - wager_2_rect.height / 2),
                    str(cls.instance.wager_amount2), 
                    (
                        constants.COLORS[5]
                        if right_happy == "happy" else
                        constants.COLORS[-1]
                    )
                    if colour_tick else
                    constants.GREYSCALE[0],
                )

            cls.instance.screen.blit(dialog, (cls.instance.DIALOG_MARGIN(size)[0], cls.instance.DIALOG_MARGIN(size)[2]))
            cls.instance.wager_tick -= 1
            if cls.instance.wager_tick == 0:
                cls.instance.in_wager = False
                if left_happy == "sad":
                    cls.instance.sprite_positions["portal2"] = cls.instance.end_pos1
                    cls.instance.playing["portal2"] = "single"
                if right_happy == "sad":
                    cls.instance.sprite_positions["portal1"] = cls.instance.end_pos2
                    cls.instance.playing["portal1"] = "single"
                cls.setScores(cls.instance.end_score1, cls.instance.end_score2)
                cls.setSpritePositions([cls.instance.end_pos1, cls.instance.end_pos2])

        pygame.display.update()

    @classmethod
    def drawWager(cls, amount1, amount2, pos1, pos2, endscore1, endscore2, endpos1, endpos2):
        cls.instance.wager_amount1 = amount1
        cls.instance.wager_amount2 = amount2
        cls.instance.wager_pos1 = pos1
        cls.instance.wager_pos2 = pos2
        cls.instance.wager_tick = cls.instance.WAGER_TICKS
        cls.instance.in_wager = True
        cls.instance.end_score1 = endscore1
        cls.instance.end_score2 = endscore2
        cls.instance.end_pos1 = endpos1
        cls.instance.end_pos2 = endpos2

    @classmethod
    def handleEvents(cls):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                cls.instance.fullscreen = not cls.instance.fullscreen
                cls.toggleFullscreen()
            if event.type == pygame.WINDOWRESIZED:
                cls.reloadSprites()
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                cls.instance.loop = False
                pygame.quit()
    
    @classmethod
    def setGridColour(cls, x, y, colour):
        cls.instance.grid_data[x][y] = colour

if __name__ == "__main__":

    os.environ["SDL_VIDEO_CENTERED"] = "1"  # You have to call this before pygame.init()

    pygame.init()

    ScreenManager()
    ScreenManager.createScreen()
    test_grid = [
        [constants.POINT_GRADIENT[random.randint(0, len(constants.POINT_GRADIENT)-1)] for x in range(15)]
        for y in range(10)
    ]
    for x in [2, 3, 6, 7, 8]:
        for y in range(3, 6):
            test_grid[y][x] = constants.COLORS[20]
    ScreenManager.initGrid(test_grid)

    while True:
        ScreenManager.mainLoopTick()
