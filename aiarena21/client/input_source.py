from aiarena21.client.classes import Player, Map


def play_powerup(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    print(f'My score: {str(me.score)}')
    print('Cost: 30 for bike, 100 for portal gun.')
    return input("what power up do I want? ('bike' / 'portal gun' / ''): ")


def play_turn(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    print(f'My location: {str(me.location)}')
    print(f'My score: {str(me.score)}')
    return input("where do I want to go on the map? (0,0 or 1,2 etc.): ")


def play_auction(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    print(f'My score: {str(me.score)}')
    return input("How much do I wager? (10, 15, etc.): ")


def play_transport(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    print(f'Enemy location: {str(opponent.location)}')
    return input("Where do I want to transport the other player? (e.g. 0,0 or 1,2 etc.): ")
