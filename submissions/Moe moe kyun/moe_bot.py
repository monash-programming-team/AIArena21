from aiarena21.client.classes import Player, Map
import numpy as np
import itertools 
import random
import os
# constant
SPAWN_MOVE = {'LEFT': [0, -1], 'RIGHT': [0, 1], 'UP':  [-1, 0], 'DOWN': [1, 0]}    

# MOVING PATTERN 

# SIMPLE MOVE
SIMPLE_MOVE_1 =  [SPAWN_MOVE['UP'], SPAWN_MOVE['RIGHT'], SPAWN_MOVE['DOWN'], SPAWN_MOVE['LEFT']]
SIMPLE_MOVE_2 =  [SPAWN_MOVE['DOWN'], SPAWN_MOVE['RIGHT'], SPAWN_MOVE['UP'], SPAWN_MOVE['LEFT']]
SIMPLE_MOVE_3 =  [SPAWN_MOVE['UP'], SPAWN_MOVE['LEFT'], SPAWN_MOVE['DOWN'], SPAWN_MOVE['RIGHT']]
SIMPLE_MOVE_4 =  [SPAWN_MOVE['DOWN'], SPAWN_MOVE['LEFT'], SPAWN_MOVE['UP'], SPAWN_MOVE['RIGHT']]

SIMPLE_MOVES = [SIMPLE_MOVE_1, SIMPLE_MOVE_2, SIMPLE_MOVE_3, SIMPLE_MOVE_4]

# L SHAPE MOVE
L_1 = [SPAWN_MOVE['LEFT']] * 3 + [SPAWN_MOVE['UP']] * 3
L_2 = [SPAWN_MOVE['DOWN']] * 3 + [SPAWN_MOVE['UP']] * 3
L_3 = [SPAWN_MOVE['UP']] * 3 + [SPAWN_MOVE['RIGHT']] * 3
L_4 = [SPAWN_MOVE['UP']] * 3 + [SPAWN_MOVE['LEFT']] * 3

L_MOVES = [L_1, L_2, L_3, L_4]

# SPIRAL MOVE
SPIRAL_RIGHT_UP = [ SPAWN_MOVE['RIGHT'], SPAWN_MOVE['RIGHT'], SPAWN_MOVE['UP'], SPAWN_MOVE['UP'], SPAWN_MOVE['LEFT'], SPAWN_MOVE['LEFT'], SPAWN_MOVE['DOWN'], SPAWN_MOVE['RIGHT']]
SPIRAL_RIGHT_DOWN = [ SPAWN_MOVE['RIGHT'], SPAWN_MOVE['RIGHT'], SPAWN_MOVE['DOWN'], SPAWN_MOVE['DOWN'], SPAWN_MOVE['LEFT'], SPAWN_MOVE['LEFT'], SPAWN_MOVE['UP'], SPAWN_MOVE['RIGHT']]
SPIRAL_LEFT_UP = [ SPAWN_MOVE['LEFT'], SPAWN_MOVE['LEFT'], SPAWN_MOVE['UP'], SPAWN_MOVE['UP'], SPAWN_MOVE['RIGHT'], SPAWN_MOVE['RIGHT'], SPAWN_MOVE['DOWN'], SPAWN_MOVE['LEFT']]        
SPIRAL_LEFT_DOWN = [ SPAWN_MOVE['LEFT'], SPAWN_MOVE['LEFT'], SPAWN_MOVE['DOWN'], SPAWN_MOVE['DOWN'], SPAWN_MOVE['RIGHT'], SPAWN_MOVE['RIGHT'], SPAWN_MOVE['UP'], SPAWN_MOVE['LEFT']]        
SPIRAL_MOVE = [SPIRAL_RIGHT_UP, SPIRAL_RIGHT_DOWN, SPIRAL_LEFT_UP, SPIRAL_LEFT_DOWN] 

# STRAIGHT MOVE
STRAIGHT_MOVE = [[list(SPAWN_MOVE[key])] * 4 for key in SPAWN_MOVE.keys()]

# STAIRS MOVE
STAIR_RIGHT_UP = [SPAWN_MOVE['UP'], SPAWN_MOVE['RIGHT']] * 2
STAIR_RIGHT_DOWN = [SPAWN_MOVE['DOWN'], SPAWN_MOVE['RIGHT']] * 2
STAIR_LEFT_UP = [SPAWN_MOVE['UP'], SPAWN_MOVE['LEFT']] * 2
STAIR_LEFT_DOWN = [SPAWN_MOVE['DOWN'], SPAWN_MOVE['LEFT']] * 2
STAIRS_MOVE = [STAIR_RIGHT_UP, STAIR_RIGHT_DOWN, STAIR_LEFT_UP, STAIR_LEFT_DOWN]

# RECTANGLE MOVE
RECTANGLE_RIGHT_UP = [SPAWN_MOVE['RIGHT']] * 2 + SPAWN_MOVE['UP'] + [SPAWN_MOVE['LEFT']] * 2
RECTANGLE_RIGHT_DOWN = [SPAWN_MOVE['RIGHT']] * 2 + SPAWN_MOVE['DOWN'] + [SPAWN_MOVE['LEFT']] * 2
RECTANGLE_LEFT_UP = [SPAWN_MOVE['LEFT']] * 2 + SPAWN_MOVE['UP'] + [SPAWN_MOVE['RIGHT']] * 2
RECTANGLE_LEFT_DOWN = [SPAWN_MOVE['LEFT']] * 2 + SPAWN_MOVE['DOWN'] + [SPAWN_MOVE['RIGHT']] * 2

RECTANGLE_UP_RIGHT = [SPAWN_MOVE['UP']] * 2 + SPAWN_MOVE['RIGHT'] + [SPAWN_MOVE['DOWN']] * 2
RECTANGLE_DOWN_RIGHT = [SPAWN_MOVE['DOWN']] * 2 + SPAWN_MOVE['RIGHT'] + [SPAWN_MOVE['UP']] * 2
RECTANGLE_UP_LEFT = [SPAWN_MOVE['UP']] * 2 + SPAWN_MOVE['LEFT'] + [SPAWN_MOVE['DOWN']] * 2
RECTANGLE_DOWN_LEFT = [SPAWN_MOVE['DOWN']] * 2 + SPAWN_MOVE['LEFT'] + [SPAWN_MOVE['UP']] * 2

RECTANGLE_MOVE = [RECTANGLE_RIGHT_UP, RECTANGLE_RIGHT_DOWN, RECTANGLE_LEFT_UP, RECTANGLE_LEFT_DOWN, RECTANGLE_UP_RIGHT, RECTANGLE_DOWN_RIGHT, RECTANGLE_UP_LEFT, RECTANGLE_DOWN_LEFT]

# COMBINE ALL PATTERNS
MOVES_PATTERN = SPIRAL_MOVE + STRAIGHT_MOVE + STAIRS_MOVE + RECTANGLE_MOVE + SIMPLE_MOVES + L_MOVES

# divide map into smaller maps
def divide_map(game_map:Map, items: list, nrows, ncols):
    grid, areas = items.copy(), []     

    for y in range(game_map.rows): 
        for x in range(game_map.cols):
            if not game_map.is_free(y,x): grid[y][x] = -30    

    len_row, len_col = game_map.rows // nrows, game_map.cols // ncols        

    for y in range(nrows):
        for x in range(ncols):            
            start_y, start_x  = y*len_row, x*len_col 
            end_y, end_x = (y+1)*len_row, (x+1)*len_col
            new_area = grid[start_y:end_y][start_x:end_x]

            areas.append({
                "items": new_area,
                "value":  np.mean(new_area),                
                "mid": ((end_y-start_y)//2, (end_x-start_x)//2),
                "edges": {"start_y": start_y, "start_x": start_x, "end_y": end_y, "end_x": end_x}
            })

    return sorted(areas, key= lambda x: x["value"], reverse=True)

def adjust_mid_point(game_map:Map, items:list, area: list):
    mid = area["mid"]
    if game_map.is_free(mid[0], mid[1]) and items[mid[0]][mid[1]] == 0: 
        return mid
    else:
        free_cells = [(iy,ix) for iy, row in enumerate(items) for ix, val in enumerate(row) if val >= 0]
        worst_free_cells = sorted(free_cells, key = lambda pos: pos[0] + pos[1])[0]
        return (worst_free_cells[0] + area["edges"]["start_y"], worst_free_cells[1] + area["edges"]["start_x"])

def tile_is_available(game_map: Map, pos):
    return (0 <= pos[0] < game_map.rows - 1) and (0 <= pos[1] < game_map.cols - 1)  and game_map.is_free(pos[0], pos[1])      

def check_items(game_map: Map, items, pos):
    # check item and its point in a tile
    if (pos[0] < game_map.rows - 1) and (pos[1] < game_map.cols - 1):
        item = items[pos[0]][pos[1]]
        return item

def generate_path(game_map: Map, items, moves, pos, remaining_turns):           
    # generate available path and its potential points count
    current_pos = np.array([pos[0], pos[1]])
    paths = []        
    efficiency = []

    # consider remaining
    rem = min(remaining_turns, len(moves))
    remaining_moves = moves[0:rem]
    move_count = 0

    for move in remaining_moves:        
        test = current_pos.copy() + move                
        if tile_is_available(game_map, test):            
            move_count += 1
            current_pos += move
            paths.append(current_pos.copy())           
            point = check_items(game_map, items, current_pos) 
            efficiency.append(point)
        else:
            break

    # remove empty tile in the end
    while True:        
        point = check_items(game_map, items, paths[-1]) if len(paths) > 0 else 30
        if point == 0: 
            paths.pop()       
            efficiency.pop()     
        else:
            break    

    return {
        "path": paths,
        "efficiency_data": efficiency,
        "distance": len(paths),
        'efficiency': 0 if len(efficiency) == 0 else np.average(efficiency) 
    }

def find_best_path(game_map: Map, items: list, pos, remaining_turns):
    paths = [y for move in MOVES_PATTERN if (y := generate_path(game_map, items, move, pos, remaining_turns)) is not None]   
    return max(paths, key = lambda x: (x['efficiency']))

# ================================= Base Gameplay Functions ===========================
# ===================================================================================== 

moves_plan = []
current_plan_efficiency = 0

def play_powerup(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    return ''

def play_turn(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):    
    global moves_plan
    global current_plan_efficiency

    if (len(moves_plan) == 0):        
        best_move = find_best_path(game_map, items, me.location, remaining_turns)    
        moves_plan = best_move['path']  
        current_plan_efficiency = best_move['efficiency_data']                          

    if (len(moves_plan) > 0):      
        newpos = moves_plan.pop(0)
        current_plan_efficiency.pop(0)                         

        # evaluate route        
        another_best_move = find_best_path(game_map, items, me.location, remaining_turns)  
        if np.average(current_plan_efficiency) < another_best_move['efficiency']:
            moves_plan = another_best_move['path']  
            current_plan_efficiency = another_best_move['efficiency_data']              
            
        return f'{newpos[0]},{newpos[1]}' 
                                      
    if not new_items:   
        
        return f'{me.location[0] + random.randint(0,1)},{me.location[1] + random.randint(0,1)}'


def play_auction(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):  
    global moves_plan
    global current_plan_efficiency

    potential_point = find_best_path(game_map, items, me.location, remaining_turns)['efficiency']
    score_difference = me.score - opponent.score
    factor = remaining_turns / 20

    moves_plan = []
    current_plan_efficiency = []
    
    return random.randint(1, max(5, min([score_difference // factor, potential_point // factor])))

def play_transport(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    worst_area = divide_map(game_map,items,10,10)[-1]
    worst_point = adjust_mid_point(game_map, items, worst_area)

    return f'{worst_point[0]},{worst_point[1]}'
