__version__ = "1.1.1"

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
parser.add_argument(
    "--name-1",
    "-n1",
    default="Team 1",
    help="Name of Orange team",
    dest="name1",
)
parser.add_argument(
    "--name-2",
    "-n2",
    default="Team 2",
    help="Name of Blue team",
    dest="name2",
)
parser.add_argument(
    "--round-time",
    "-rt",
    default=100,
    help="How many rounds to run for",
    dest="rounds",
)

def main():
    import sys, time
    args = parser.parse_args(sys.argv[1:])
    called_from = os.getcwd()

    from aiarena21.server import start_server
    from aiarena21.client import run_client

    replay_path = os.path.join(called_from, args.replay)

    try:
        args.rounds = int(args.rounds)
        assert args.rounds > 0
    except:
        raise ValueError("Rounds should be a positive integer")

    # Resolve bot paths
    if not args.bot1.endswith(".py"):
        args.bot1 = args.bot1 + ".py"
    if not args.bot2.endswith(".py"):
        args.bot2 = args.bot2 + ".py"
    full_path_1 = os.path.join(called_from, args.bot1)
    if not os.path.isfile(full_path_1):
        full_path_1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client', args.bot1)
    if not os.path.isfile(full_path_1):
        raise ValueError(f"Could not find bot file {args.bot1}")
    full_path_2 = os.path.join(called_from, args.bot2)
    if not os.path.isfile(full_path_2):
        full_path_2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client', args.bot2)
    if not os.path.isfile(full_path_2):
        raise ValueError(f"Could not find bot file {args.bot2}")

    server_process = Process(target=start_server, args=[called_from, args.map, replay_path, args.rounds], daemon=True)
    client1_process = Process(target=run_client, args=[full_path_1, args.name1], daemon=True)
    client2_process = Process(target=run_client, args=[full_path_2, args.name2], daemon=True)

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
