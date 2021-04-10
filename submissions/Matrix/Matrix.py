from aiarena21.client.classes import Player, Map
import numpy as np
import random



def move_direction_step(game_map: Map, me: Player, items: list, my_location, destination_location):
    try:
        direction = MDP(game_map, items, my_location,
                        [destination_location[0], destination_location[1]])

        if direction == 'U':
            return f'{my_location[0] - 1},{my_location[1]}'
        elif direction == 'D':
            return f'{my_location[0] + 1},{my_location[1]}'
        elif direction == 'L':
            return f'{my_location[0]},{my_location[1] - 1}'
        elif direction == 'R':
            return f'{my_location[0]},{my_location[1] + 1}'
    except ValueError:
        possibles = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        randomed_choice = possibles[random.randint(0, 3)]

        return f'{my_location[0] + randomed_choice[0]},{my_location[1] + randomed_choice[1]}'


def through_wall(game_map: Map, pos_1, pos_2):
    distance = distance_on_map(pos_1, pos_2)
    if pos_1[0] == pos_2[0]:
        mini_col = min(pos_1[1], pos_2[1])
        for i in range(1, distance+1):
            if not game_map.is_free(pos_1[0], mini_col+i):
                return True
    elif pos_1[1] == pos_2[1]:
        mini_row = min(pos_2[0], pos_1[0])
        for i in range(1, distance+1):
            if not game_map.is_free(mini_row+1, pos_1[1]):
                return True
    else:
        return False

def bike_land_on(game_map: Map, current_pos, remaining_turns, items, heatmap):
    # maximum_distance = 3
    adds = [(+3, 0),
           (+2, -1), (+2, 0), (+2, +1),
           (+1, -2), (+1, -1), (+1, 0), (+1, +1), (+1, +2),
           (0, -3), (0, -2), (0, -1), (0, +1), (0, +2), (0, +3),
           (-1, -2), (-1, -1), (-1, 0), (-1, +1), (-1, +2),
           (-2, -1), (-2, 0), (-2, +1),
           (-3, 0)]
    valid_adds = []
    for add in adds:
        new_row, new_col = current_pos[0] + add[0], current_pos[1] + add[1]
        if 0 <= new_row < game_map.rows and 0 <= new_col < game_map.cols:
            if game_map.is_free(new_row, new_col):
                valid_adds.append(add)

    # Find out who holds the most current score in items
    # If there are more than 14 turns left in current 20 turns, go to the location who holds the highest heat value
    # Else go to the location who holds the most fruits
    land_point = [-1, -1]
    if remaining_turns % 20 > 14:
        max_heat_value = float("-inf")
        for add in valid_adds:
            new_row, new_col = current_pos[0] + add[0], current_pos[1] + add[1]
            if heatmap[new_row][new_col] > max_heat_value and not through_wall(game_map, current_pos, [new_row, new_col]):
                land_point = [new_row, new_col]
                max_heat_value = heatmap[new_row][new_col]
    else:
        max_items_score = float("-inf")
        for add in valid_adds:
            new_row, new_col = current_pos[0] + add[0], current_pos[1] + add[1]
            if items[new_row][new_col] > max_items_score and not through_wall(game_map, current_pos, [new_row, new_col]):
                land_point = [new_row, new_col]
                max_items_score = items[new_row][new_col]
    print(land_point)
    return land_point

def block_coefficient(game_map: Map, center_pos, checking_range):
    avaiablable_directions = [[1, 0], [-1, 0], [0, 1], [0, -1]]
    accessable_blocks = [[center_pos[0], center_pos[1]]]
    total = 0
    for i in range(checking_range + 1):
        total += i * i
    for i in range(checking_range):
        for blocks in center_pos:
            for directions in avaiablable_directions:
                try:
                    if game_map.is_free(center_pos[0] + directions[0], center_pos[1] + directions[1]) == True:
                        accessable_blocks.append([center_pos[0] + directions[0], center_pos[1] + directions[1]])
                except IndexError:
                    pass
    return len(accessable_blocks) / total


def distance_on_map(pos_1, pos_2):
    return abs(pos_1[0] - pos_2[0]) + abs(pos_1[1] - pos_2[1])

def valid_actions(game_map: Map, state):
    actions = ['U', 'D', 'L', 'R']
    x_coor = state[1]
    y_coor = state[0]
    if y_coor - 1 < 0 or not game_map.is_free(y_coor - 1, x_coor):
        actions.remove('U')
    if y_coor + 1 >= game_map.rows or not game_map.is_free(y_coor + 1, x_coor):
        actions.remove('D')
    if x_coor - 1 < 0 or not game_map.is_free(y_coor, x_coor - 1):
        actions.remove('L')
    if x_coor + 1 >= game_map.cols or not game_map.is_free(y_coor, x_coor + 1):
        actions.remove('R')
    assert actions != []
    return actions


def MDP(game_map: Map, items: list, my_location, goal_location: list):
    '''==================================================
    Initial set up
    =================================================='''

    # Hyperparameters
    GAMMA = 0.9

    # Define all states
    all_states = []
    blocked_states = []
    for i in range(game_map.rows):
        for j in range(game_map.cols):
            if game_map.is_free(i, j):
                all_states.append((i, j))
            else:
                blocked_states.append((i, j))

    # Define rewards for all states
    rewards = {}
    for state in all_states:
        rewards[state] = items[state[0]][state[1]]
    for blocked in blocked_states:
        rewards[blocked] = -float('inf')

    # Dictionnary of possible actions.
    actions = {}
    for state in all_states:
        actions[state] = valid_actions(game_map, state)

    # Define an initial policy
    policy = {}
    for s in all_states:
        policy[s] = np.random.choice(actions[s])

    # Define initial value function
    V = {}
    for state in all_states:
        V[state] = rewards[state]

    '''==================================================
    Value Iteration
    =================================================='''

    for _ in range(200):
        for s in all_states:
            if s in policy:

                old_v = V[s]
                new_v = 0
                for a in actions[s]:
                    if a == 'U':
                        nxt = [s[0] - 1, s[1]]
                    if a == 'D':
                        nxt = [s[0] + 1, s[1]]
                    if a == 'L':
                        nxt = [s[0], s[1] - 1]
                    if a == 'R':
                        nxt = [s[0], s[1] + 1]

                    # Calculate the value
                    nxt = tuple(nxt)
                    v = rewards[s] + (GAMMA * V[nxt])
                    if v > new_v:  # Is this the best action so far? If so, keep it
                        new_v = v
                        policy[s] = a

                # Save the best of all actions for the state
                V[s] = new_v

    return policy[(my_location[0], my_location[1])]


total_turn = None
analysis_range = 10

def play_powerup(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    global total_turn
    if total_turn == None:
        total_turn = remaining_turns

    if block_coefficient(game_map, me.location,
                         5) < 0.4 and me.portal_gun == False and total_turn - remaining_turns > 20:
        return 'portal gun'
    elif remaining_turns < 20 and me.bike == False and me.score>30 and remaining_turns%3 == 2 :
        return 'bike'
    else:
        return ''






def play_turn(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    current_y = me.location[0]
    current_x = me.location[1]
    # for the first 20 turns
    map_length = len(items[0])
    map_height = len(items)
    block_coefficient_range = 0
    smaller = min(map_length, map_height)
    if smaller in range(1, 4):
        block_coefficient_range = 1
    elif smaller in range(5, 8):
        block_coefficient_range = 2
    elif smaller in range(9, 13):
        block_coefficient_range = 3
    elif smaller in range(14, 24):
        block_coefficient_range = 4
    else:
        block_coefficient_range = 5
    if me.portal_gun == True and total_turn - remaining_turns > 20:
        max_coefficient = [0, 0, 0]

        for y in range(-20, 20 + 1):
            for x in range(-20 - y if y < 0 else -20 + y,
                           20 - x + 1 if y > 0 else 20 + y + 1):
                if current_y + y in range(0, len(items)) and current_x + x in range(0, len(items[0])):
                    temp_coefficient = block_coefficient(game_map, [current_y + y, current_x + x],
                                                         block_coefficient_range)
                    if temp_coefficient > max_coefficient[2]:
                        max_coefficient = [current_y + y, current_x + x, temp_coefficient]
        return f'{max_coefficient[0]},{max_coefficient[1]}'
    if total_turn - remaining_turns < 20:
        max_heat = [0, 0, 0]
        for y in range(-analysis_range, analysis_range + 1):
            for x in range(-analysis_range - y if y < 0 else -analysis_range + y,
                           analysis_range - x + 1 if y > 0 else analysis_range + y + 1):
                if current_y + y in range(0, len(items)) and current_x + x in range(0, len(items[0])):
                    temp_heat = heatmap[current_y + y][current_x + x]
                    if temp_heat > max_heat[2]:
                        max_heat = [current_y + y, current_x + x, temp_heat]
        return move_direction_step(game_map, me, items, me.location, max_heat)
    if remaining_turns < 20 and me.bike == True:
        position = bike_land_on(game_map,me.location,remaining_turns,items,heatmap)
        return f'{position[0]},{position[1]}'

    else:
        max_score = [0, 0, 0, 0, 0]
        for y in range(-analysis_range, analysis_range + 1):
            for x in range(-analysis_range - y if y < 0 else -analysis_range + y,
                           analysis_range - y + 1 if y > 0 else analysis_range + y + 1):
                y_cursor = current_y + y
                x_cursor = current_x + x
                while y_cursor < 0:
                    y_cursor += len(items)
                while y_cursor > len(items) - 1:
                    y_cursor -= len(items)
                while x_cursor < 0:
                    x_cursor += len(items[0])
                while x_cursor > len(items[0]) - 1:
                    x_cursor -= len(items[0])
                if items[y_cursor][x_cursor] > 0:
                    if distance_on_map([current_y, current_x], [y_cursor, x_cursor]) == 0:
                        y_cursor += 1
                    score_per_step = items[y_cursor][x_cursor] / distance_on_map([current_y, current_x],
                                                                                 [y_cursor, x_cursor])
                    if score_per_step > max_score[4]:
                        max_score = [y_cursor, x_cursor, items[y_cursor][x_cursor],
                                     distance_on_map([current_y, current_x], [y_cursor, x_cursor]), score_per_step]

        return move_direction_step(game_map, me, items, me.location, max_score)


def play_auction(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    my_score = me.score
    opp_score = opponent.score
    max_opp_bid_prediciton = round(opp_score * 70 / 100)
    score_diff_threshold = 80
    if remaining_turns < round(total_turn/5):  # we don't want to take risk on the last 20 turns
        return 0
    elif remaining_turns < round(total_turn * 2/5 ) and remaining_turns >= round(total_turn/5):
        percentage_bid = 10
    elif remaining_turns < round(total_turn * 3/5 ) and remaining_turns >= round(total_turn * 2/5 ):
        percentage_bid = 7
    else:
        percentage_bid = 6
    if my_score - opp_score > score_diff_threshold:
        percentage_bid += 2
    return min(max_opp_bid_prediciton, round(my_score/percentage_bid))




def play_transport(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    least_coefficient = [0, 0, 1]
    map_length = len(items[0]) - 1
    map_height = len(items) - 1
    for y in range(map_height):
        for x in range(map_length):
            if block_coefficient(game_map, [y, x], 10) < least_coefficient[2]:
                least_coefficient = [y, x, block_coefficient(game_map, [y, x], 10)]
    return f'{least_coefficient[0]},{least_coefficient[1]}'
