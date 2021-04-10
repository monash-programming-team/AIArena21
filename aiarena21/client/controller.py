import socket
import json
import aiarena21.client.data as game_data
from aiarena21.client.classes import Player, Map


def run_client(CLIENT_SOURCE, TEAM_NAME):
    from importlib.machinery import SourceFileLoader
    module = SourceFileLoader("__not_main__", CLIENT_SOURCE).load_module()
    try:
        play_auction = getattr(module, "play_auction")
        play_transport = getattr(module, "play_transport")
        play_turn = getattr(module, "play_turn")
        play_powerup = getattr(module, "play_powerup")
    except:
        raise ValueError(f"One of the bot methods not implemented for {CLIENT_SOURCE}.")

    HOST = socket.gethostname()
    SERVER_PORT = 8000
    SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    BUFFER_SIZE = 8 * 1024

    def connect_to_server():
        SOCKET.sendto(TEAM_NAME.encode('utf-8'), (HOST, SERVER_PORT))
        data, addr = SOCKET.recvfrom(BUFFER_SIZE)
        data = data.decode('utf-8')
        TOKEN = data.split('-')[1]
        return TOKEN

    def finish():
        SOCKET.close()

    def update_game_data(data):
        for key in ['map', 'map_size', 'players', 'items', 'new_items', 'heatmap', 'remaining_turns']:
            if key in data.keys():
                setattr(game_data, key.upper(), data[key])
        return 'ok'

    def run():
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
                print("Received wrong token from server. Skipping...", token, TOKEN)
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
            try:
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
            except Exception as e:
                print("Code crashed!")
                callback = 'CRASH'

            callback_obj = {'token': TOKEN, 'message': str(callback), 'id': message_id}
            SOCKET.sendto(json.dumps(callback_obj).encode('utf-8'), (HOST, SERVER_PORT))

    SOCKET.settimeout(None)
    TOKEN = connect_to_server()
    run()
