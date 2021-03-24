__version__ = "1.0.0"

from aiarena21 import client, visual
import argparse, os
from multiprocessing import Process

parser = argparse.ArgumentParser(description="Run the AIArena 2021 simulation.")
parser.add_argument(
    "bot1",
    type=str,
    default=None,
    help="The path of the bot script for Orange Team.",
)
parser.add_argument(
    "bot2",
    type=str,
    default=None,
    help="The path of the bot script for Blue Team.",
)
parser.add_argument(
    "--map",
    "-m",
    type=str,
    default="1.txt",
    help="The map to simulate on.",
)
parser.add_argument(
    "--replay",
    "-r",
    type=str,
    default="replay.txt",
    help="Path to store the replay file.",
)
parser.add_argument(
    "--no-visual",
    "-nv",
    action="store_false",
    help="Disable the visual representation of the game, and simply create a replay file. Much faster.",
    dest="visual",
)

def main():
    import sys, time
    args = parser.parse_args(sys.argv[1:])
    called_from = os.getcwd()

    from aiarena21.server import start_server
    from aiarena21.client import run_client

    replay_path = os.path.join(called_from, args.replay)

    server_process = Process(target=start_server, args=[called_from, args.map, replay_path], daemon=True)
    client1_process = Process(target=run_client, args=[], daemon=True)
    client2_process = Process(target=run_client, args=[], daemon=True)

    visual_process = None
    if args.visual:
        from aiarena21.visual import run_visual
        visual_process = Process(target=run_visual, args=[replay_path], daemon=True)

    server_process.start()
    time.sleep(0.5)
    client1_process.start()
    client2_process.start()

    if args.visual:
        # Make sure the replay file is created and replaced.
        time.sleep(0.05)
        visual_process.start()

    try:
        if args.visual:
            visual_process.join()
        else:
            server_process.join()
    except KeyboardInterrupt:
        for process in [
            server_process,
            client1_process,
            client2_process,
        ] + ([visual_process] if args.visual else []):
            process.terminate()
            process.join()
            process.close()
    except Exception as e:
        for process in [
            server_process,
            client1_process,
            client2_process,
        ] + ([visual_process] if args.visual else []):
            process.terminate()
            process.join()
            process.close()
        raise e  
