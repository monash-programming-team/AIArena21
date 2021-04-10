from aiarena21.client.classes import Player, Map
import random
import logging

"""
Strategy:

find all paths of depth n from the player's current position
evaluate the value of the paths based on the score of the fruit or heatmap
"""
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.INFO)


def play_powerup(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    return
#     #return random.choice(['bike', 'portal gun', ''])
#     me_x, me_y = me.location
#     op_x, op_y = opponent.location
#
#     me_score = me.score
#     op_score = opponent.score
#
#     item_tensor = torch.tensor(items)
#
#     heatmap_rowsum = []
#     row_max_index = []
#
#     for i, each in enumerate(heatmap):
#         heatmap_rowsum.append(sum(each))
#         row_max_index.append(np.argmax(np.array(each)))
#
#     heatmap_colsum = []
#     col_max_index = []
#
#     temp_heatmap = np.array(heatmap).T.tolist()
#     for i, each in enumerate(temp_heatmap):
#         heatmap_colsum.append(sum(each))
#         col_max_index.append(np.argmax(np.array(each)))
#
#     if ((me_x < op_x < max(row_max_index) and me_y < op_y < max(col_max_index)) or
#         (me_x > op_x > max(row_max_index) and me_y > op_y > max(col_max_index))) and op_score - me_score > 100:
#         return 'portal gun'
#     elif sum(heatmap_rowsum) + sum(heatmap_colsum) > me_score + op_score and me_score < op_score:
#         return 'bike'


# def play_transport(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
#         me_x, me_y = me.location
#     op_x, op_y = opponent.location
#
#     me_score = me.score
#     op_score = opponent.score
#
#     item_tensor = torch.tensor(items)
#
#     heatmap_rowsum = []
#     row_max_index = []
#
#     for i, each in enumerate(heatmap):
#         heatmap_rowsum.append(sum(each))
#         row_max_index.append(np.argmax(np.array(each)))
#
#     heatmap_colsum = []
#     col_max_index = []
#
#     temp_heatmap = np.array(heatmap).T.tolist()
#     for i, each in enumerate(temp_heatmap):
#         heatmap_colsum.append(sum(each))
#         col_max_index.append(np.argmax(np.array(each)))
#
#     return f'{max(row_max_index)},{max(col_max_index)}'


def play_turn(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    n = 10
    paths = []
    row, col = me.location
    for row2, col2 in [(row - 1, col), (row, col - 1), (row + 1, col), (row, col + 1)]:
        if 0 <= row2 < game_map.rows and 0 <= col2 < game_map.cols and game_map.is_free(row2, col2):
            paths.append(find_path(n - 1, 0, me.location, (row2, col2), game_map, items, heatmap))

    # try:
    score, pos = max(paths, key=lambda item: item[0])
    # except:
    #     for row2, col2 in [(row - 1, col), (row, col - 1), (row + 1, col), (row, col + 1)]:
    #         logging.info("")
    #         logging.info(0 <= row2 < game_map.rows)
    #         logging.info(0 <= col2 < game_map.cols)
    #         logging.info(game_map.is_free(row2, col2))
    #         logging.info(find_path(n - 1, 0, me.location, (row2, col2), game_map, items, heatmap))
    #         logging.info("")
    # TODO: getting an error because max() arg is an empty sequence

    if sum([sum(i) for i in items]) == 0:
        heat_row, heat_col = search_map(game_map, me.location, heatmap)
        print("initial", heat_row, heat_col)
        if heat_row > row and game_map.is_free(row+1, col):
            heat_row = row + 1
            heat_col = col
        elif heat_row < row and game_map.is_free(row-1, col):
            heat_row = row - 1
            heat_col = col
        elif heat_col > col and game_map.is_free(row, col + 1):
            heat_col = col + 1
            heat_row = row
        elif heat_col < row and game_map.is_free(row, col-1):
            heat_col = col - 1
            heat_row = row

        print("initial", heat_row, heat_col)
        print(row, col)
        print(me.location)
        return f'{heat_row},{heat_col}'

    return f'{pos[0]},{pos[1]}'


def play_auction(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    location = me.location
    right_end = location[0] + 20 if location[0] + 20 < game_map.rows else game_map.rows - 1
    top_end = location[1] + 20 if location[1] + 20 < game_map.cols else game_map.cols - 1
    left_end = location[0] - 20 if location[0] - 20 >= 0 else 0
    bottom_end = location[1] - 20 if location[1] - 20 >= 0 else 0
    our_area = sum([sum(i) for i in items[left_end:right_end+1][bottom_end:top_end+1]])
    print(sum([sum(i) for i in items[left_end:right_end+1][bottom_end:top_end+1]]))
    print("our area: ", our_area)

    location = opponent.location
    right_end = location[0] + 20 if location[0] + 20 < game_map.rows else game_map.rows - 1
    top_end = location[1] + 20 if location[1] + 20 < game_map.cols else game_map.cols - 1
    left_end = location[0] - 20 if location[0] - 20 >= 0 else 0
    bottom_end = location[1] - 20 if location[1] - 20 >= 0 else 0
    their_area = sum([sum(i) for i in items[left_end:right_end+1][bottom_end:top_end+1]])
    print("their area: ", their_area)
    if their_area > our_area:
        return max((our_area+their_area)/30, 10)

    return max(our_area / 15, 5)


def play_transport(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    s = 100000
    index = (-1,-1)
    for i in range(game_map.rows):
        for j in range(game_map.cols):
            location = (i, j)
            right_end = location[0] + 10 if location[0] + 10 < game_map.rows else game_map.rows - 1
            top_end = location[1] + 10 if location[1] + 10 < game_map.cols else game_map.cols - 1
            left_end = location[0] - 10 if location[0] - 10 >= 0 else 0
            bottom_end = location[1] - 10 if location[1] - 10 >= 0 else 0
            if s > sum([sum(i) for i in items[left_end:right_end+1][bottom_end:top_end+1]]):
                index = (i, j)
                s = sum([sum(i) for i in items[left_end:right_end+1][bottom_end:top_end+1]])


    return f'{index[0]},{index[1]}'


def search_map(game_map: Map, location, heat_map):
    right_end = location[0] + 10 if location[0] + 10 < game_map.rows else game_map.rows-1
    top_end = location[1] + 10 if location[1] + 10 < game_map.cols else game_map.cols - 1
    left_end = location[0] - 10 if location[0] - 10 >= 0 else 0
    bottom_end = location[1] - 10 if location[1] - 10 >= 0 else 0

    highest_heat_point = 0
    heat_row = None
    heat_col = None

    for i in range(left_end, right_end):
        for j in range(bottom_end, top_end):
            if game_map.is_free(i, j) and heat_map[i][j] > highest_heat_point:
                heat_row = i
                heat_col = j

    return heat_row, heat_col



def find_path(depth, accumulated_score, previous_pos, current_pos, game_map: Map, items: list, heat_map: list):
    if depth == 0:
        # return score at this position and the positions
        row, col = current_pos
        return items[row][col] + heat_map[row][col]/10, current_pos
    else:
        # generate possible moves and call find_path, return the value that is higher
        row, col = current_pos
        paths = []
        no_paths = True
        for row2, col2 in [(row - 1, col), (row, col - 1), (row + 1, col), (row, col + 1)]:
            if 0 <= row2 < game_map.rows and 0 <= col2 < game_map.cols and game_map.is_free(row2, col2):
                if previous_pos is not None and (row2, col2) == previous_pos:
                    continue
                no_paths = False
                paths.append(find_path(depth - 1, accumulated_score, current_pos, (row2, col2), game_map, items, heat_map))
        if no_paths:
            # logging.info("Supposedly there are no paths")
            paths.append(find_path(depth - 1, accumulated_score, current_pos, previous_pos, game_map, items, heat_map))

        score, pos = max(paths, key=lambda item: item[0])
        return items[row][col] + score, current_pos