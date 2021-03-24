from typing import List

import aiarena21.server.network as network
from aiarena21.server.player import players, Player
from aiarena21.server.game import Game
from aiarena21.server.logs import init_replay, replay, log, finish as finish_logs
import aiarena21.server.settings as settings

import re


def ask_powerups(game):
    for player in game.players:
        network.send_player_update(player, game)
        waiting_id = network.send_player(player, {'type': 'powerup'})
        powerup_request = network.recv_player(player, waiting_id)
        if powerup_request not in ['bike', 'portal gun', '']:
            log(f'{player.name} requested invalid powerup: {powerup_request}')
        else:
            if powerup_request == 'bike':
                if player.equip_bike(game):
                    log(f'{player.name} got bike powerup.')
                else:
                    log(f'{player.name} did not have enough scores for bike powerup.')
            elif powerup_request == 'portal gun':
                if player.equip_portal_gun(game):
                    log(f'{player.name} got portal gun powerup.')
                else:
                    log(f'{player.name} did not have enough scores for portal gun powerup.')
            else:
                log(f'{player.name} did not purchase a powerup.')


def get_moves(game):
    moves = []
    for player in game.players:
        network.send_player_update(player, game)
        waiting_id = network.send_player(player, {'type': 'turn'})
        move = network.recv_player(player, waiting_id)
        log(f'{player.name} played {move} for their turn.')
        moves.append(move)
    return moves


def auction_transport(game, winner, cost):
    loser = 1 - winner
    game.players[winner].score -= cost
    waiting_id = network.send_player(game.players[winner], {'type': 'transport'})
    location = network.recv_player(game.players[winner], waiting_id)
    transport_reg = re.compile(f'([0-9]+),([0-9]+)')
    if not transport_reg.fullmatch(location):
        game.transport_random(game.players[loser])
    else:
        row, col = map(int, transport_reg.fullmatch(location).groups())
        if not game.cell_available(row, col):
            game.transport_random(game.players[loser])
        else:
            game.players[loser].update_location(row, col)


def start_auction(game):
    amounts = []
    for player in game.players:
        network.send_player(player, {
            'type': 'update',
            'data': {
                'players': {
                    players[x].name: {
                        'score': players[x].score,
                        'location': players[x].location,
                        'bike': players[x].using_bike,
                        'portal_gun': players[x].using_portal_gun
                    }
                    for x in [0, 1]
                },
            }
        })
        waiting_id = network.send_player(player, {'type': 'auction'})
        amount = network.recv_player(player, waiting_id)
        log(f'{player.name} wagered {amount} for their auction.')
        amounts.append(amount)

    for i in range(2):
        try:
            amounts[i] = int(amounts[i])
            if not 0 <= amounts[i] <= players[i].score:
                log(f'Invalid wager from {game.players[i].name}: {amounts[i]}')
                amounts[i] = 0
        except (ValueError, TypeError):
            log(f'Non-numeric wager from {game.players[i].name}: {amounts[i]}')
            amounts[i] = 0

    avg_wager = sum(amounts) // 2
    if amounts[0] > amounts[1]:
        auction_transport(game, 0, avg_wager)
    elif amounts[1] > amounts[0]:
        auction_transport(game, 1, avg_wager)
    else:
        game.transport_random(game.players[0])
        game.transport_random(game.players[1])
    return amounts


def run_game(players: List[Player]):
    game = Game(players)
    init_payload = {
        'type': 'init',
        'grid': game.map,
        'scores': [game.players[0].score, game.players[1].score],
        'teams': [game.players[0].name, game.players[1].name],
        'spawn': [game.players[0].location, game.players[1].location],
        'total_rounds': settings.TOTAL_ROUNDS,
    }
    replay(init_payload)

    for round_counter in range(game.total_rounds):
        game.deploy_items()
        game.update_heatmap()
        ask_powerups(game)
        moves = get_moves(game)
        for i in range(2):
            players[i].play_move(game, moves[i])

        locations_before_wager = [game.players[i].location for i in range(2)]
        # This is a while instead of an if so if the random location after transport is still the same location
        # auction would happen again
        wagers = None
        while players[0].location == players[1].location:
            wagers = start_auction(game)

        for player in game.players:
            player.pickup_items(game)
            player.update_powerups()

        if wagers is not None:
            wagers = {
                'wagers': wagers,
                'before_positions': locations_before_wager
            }
        game.finish_turn(wagers)

    for player in game.players:
        network.send_player(player, {'type': 'finish'})
        replay({
            'type': 'finish'
        })

def start_server(cwd, map_file, replay_path):
    network.init()
    settings.set_map_file(cwd, map_file)
    settings.REPLAY_PATH = replay_path
    init_replay()
    network.connect_players()
    run_game(players)
    finish_logs()
    network.finish()
