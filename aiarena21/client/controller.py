import socket
import json
from aiarena21.client.random_source import play_auction, play_transport, play_turn, play_powerup
import aiarena21.client.data as game_data
from aiarena21.client.classes import Player, Map
from aiarena21.client.data import TEAM_NAME

HOST = socket.gethostname()
SERVER_PORT = 8000
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
BUFFER_SIZE = 8 * 1024

TOKEN = ''


def connect_to_server():
    SOCKET.sendto(game_data.TEAM_NAME.encode('utf-8'), (HOST, SERVER_PORT))
    data, addr = SOCKET.recvfrom(BUFFER_SIZE)
    data = data.decode('utf-8')
    global TOKEN
    TOKEN = data.split('-')[1]


def finish():
    SOCKET.close()


def update_game_data(data):
    for key in ['map', 'map_size', 'players', 'items', 'new_items', 'heatmap', 'remaining_turns']:
        if key in data.keys():
            setattr(game_data, key.upper(), data[key])
    return 'ok'


def run():
    SOCKET.settimeout(None)
    connect_to_server()
    while True:
        data, _ = SOCKET.recvfrom(BUFFER_SIZE)
        """
        Data is like:
        {
            token: ...
            id: ...
            message:
            {
                type: ...
                data: ...
            }
        }
        """
        try:
            data = json.loads(data.decode('utf-8'))
            token = data['token']
            message = data['message']
            message_id = data['id']
        except json.JSONDecodeError as e:
            print("Json Decoding Error occurred. This likely means you need to increase BUFFER_SIZE in controller.py")
            raise e
        except Exception as e:
            print("Invalid message received from server. Skipping...")
            continue
        if token != TOKEN:
            print("Received wrong token from server. Skipping...")
            continue

        if game_data.PLAYERS is None:
            players = [None, None]
        else:
            players = [Player(key, game_data.PLAYERS[key]) for key in game_data.PLAYERS.keys()]
            if players[0].name != TEAM_NAME:
                players[0], players[1] = players[1], players[0]
        args = [
            Map(game_data.MAP_SIZE, game_data.MAP),
            *players,
            game_data.ITEMS,
            game_data.NEW_ITEMS,
            game_data.HEATMAP,
            game_data.REMAINING_TURNS
        ]
        if message['type'] == 'update':
            # { map: ((), (), ...) }
            callback = update_game_data(message['data'])
        elif message['type'] == 'powerup':
            print("Picking powerups...")
            callback = play_powerup(*args)
        elif message['type'] == 'turn':
            print("It's my turn!")
            callback = play_turn(*args)
        elif message['type'] == 'auction':
            print("Got into an auction.")
            callback = play_auction(*args)
        elif message['type'] == 'transport':
            print("Transporting the other player")
            callback = play_transport(*args)
        elif message['type'] == 'finish':
            print("GG")
            finish()
            break
        else:
            print("Unknown message received from server. Skipping...")
            continue

        callback_obj = {'token': TOKEN, 'message': str(callback), 'id': message_id}
        SOCKET.sendto(json.dumps(callback_obj).encode('utf-8'), (HOST, SERVER_PORT))


run()
