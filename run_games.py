import shutil, sys, subprocess, os

round_times = {
    "1.txt": 300,
    "2.txt": 300,
    "3.txt": 200,
    "4.txt": 200,
    "5.txt": 400,
    "6.txt": 400,
    "7.txt": 400,
}

with open(sys.argv[1], "r") as f:
    games = f.readlines()

for game in games:
    s1, n1, s2, n2, m = game.split('$')
    m = m.replace('\n', '')
    replay_name = f"replays/{n1}-{n2}-{m}"
    subprocess.run(["aiarena21", s1, s2, "-n1", n1, "-n2", n2, "-m", m, "-rt", str(round_times[m]), "-nv"])
    shutil.copy("replay.txt", replay_name)
