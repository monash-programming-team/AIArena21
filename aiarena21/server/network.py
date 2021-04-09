import socket
from aiarena21.server.player import Player, players
from aiarena21.server.game import Game
import time
from timeit import default_timer as timer
import json


def init():
    global HOST, PORT, SOCKET, TIMEOUT_TIME, recv_msg_queue

    HOST = socket.gethostname()
    PORT = 8000
    SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    SOCKET.bind((HOST, PORT))

    TIMEOUT_TIME = 2

    print("Server Started")

    recv_msg_queue = {}


def connect_players():
    while len(players) < 2:
        data, addr = SOCKET.recvfrom(1024)
        data = data.decode('utf-8')
        print(f'Team {data} connected...')
        players.append(Player(data, addr))
        success_message = f'ok-{players[-1].token}'
        SOCKET.sendto(success_message.encode('utf-8'), addr)
        recv_msg_queue[players[-1].token] = []


message_counter = 0


def send_player(player: Player, message):
    global message_counter
    SOCKET.settimeout(None)
    message_obj = {'token': player.token, 'message': message, 'id': message_counter}
    message_counter += 1
    SOCKET.sendto(json.dumps(message_obj).encode('utf-8'), player.address)
    return message_counter - 1


def recv_player(player: Player, waiting_id):
    while len(recv_msg_queue[player.token]) != 0:
        message_id, message = recv_msg_queue[player.token][0]
        recv_msg_queue[player.token] = recv_msg_queue[player.token][1:]
        if message_id != waiting_id:
            continue
        return message

    sleep_time = 0.001
    start = timer()
    while True:
        if timer() - start >= TIMEOUT_TIME:
            return None

        time_left = TIMEOUT_TIME - (timer() - start)

        SOCKET.settimeout(time_left)

        try:
            data, _ = SOCKET.recvfrom(1024)
            try:
                data = json.loads(data.decode('utf-8'))
                token = data['token']
                message = data['message']
                message_id = data['id']
            except Exception:
                print("Invalid value received. Skipping...")
                continue

            if token == player.token and message_id == waiting_id:
                return message
            if token in recv_msg_queue.keys():
                recv_msg_queue[token].append((message_id, message))
        except socket.timeout:
            print(f'Player {player.name} timed out.')
            return None

        time.sleep(sleep_time)
        sleep_time = min(0.2, 2*sleep_time)


def send_player_update(player: Player, game: Game):
    send_player(player, {
        'type': 'update',
        'data': {
            'map_size': game.map_size,
            'map': game.map,
        }
    })
    send_player(player, {
        'type': 'update',
        'data': {
            'remaining_turns': game.total_rounds - game.current_round,
            'heatmap': game.heatmap
        }
    })
    send_player(player, {
        'type': 'update',
        'data': {
            'items': game.items_score_map()
        }
    })
    send_player(player, {
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
            'new_items': [
                [[x.name for x in position] for position in sublist]
                for sublist in game.new_items
            ] if game.new_items else None
        }
    })


def finish():
    SOCKET.close()
    print("Server closed")
