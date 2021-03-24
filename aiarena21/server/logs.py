import json
from aiarena21.server.settings import REPLAY_PATH

replay_file = None

def init_replay():
    global replay_file
    replay_file = open(REPLAY_PATH, 'w')
    replay_file.write('')
    replay_file.flush()


def replay(thing):
    global replay_file
    # print(f'[Replay]{json.dumps(thing)}', flush=True)
    replay_file.write(f'[Replay]{json.dumps(thing)}\n')
    replay_file.flush()


def finish():
    replay_file.close()


def log(message):
    pass
    # print(message)
