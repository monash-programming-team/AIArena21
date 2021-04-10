import json, os, xlsxwriter

maps = [
    '1', '2', '3', '4', '5', '6', '7'
]

teams = [
    'team1',
    'team2',
]

workbook = xlsxwriter.Workbook("analysis.xlsx")

for i, team1 in enumerate(teams):
    worksheet = workbook.add_worksheet(name=team1)
    worksheet.write(2, 0, "Score")
    worksheet.write(3, 0, "Enemy Score")
    worksheet.write(4, 0, "Points")
    for j, team2 in enumerate(teams):
        if i == j: continue
        if j > i:
            j -= 1
        # Set up columns/rows
        worksheet.write(0, j * len(maps) + 1, team2)
        # Data
        for k, m in enumerate(maps):
            map_index = j * len(maps) + 1 + k
            worksheet.write(1, map_index, f'{m}.txt')
            replay_1 = f"replays/{team1}-{team2}-{m}.txt"
            replay_2 = f"replays/{team2}-{team1}-{m}.txt"
            if os.path.isfile(replay_1):
                f = open(replay_1, "r")
                l = list(f.readlines())
                f.close()
            elif os.path.isfile(replay_2):
                f = open(replay_2, "r")
                l = list(f.readlines())
                f.close()
            else:
                l = []
            # Try to find the (last line with scores.
            done = False
            if len(l) != 0:
                team_names = json.loads(l[0][8:])["teams"]
                for i in range(len(l)-1, -1, -1):
                    if l[i].startswith("[Replay]"):
                        obj = json.loads(l[i][8:])
                        if obj["type"] == "tick":
                            t1_score = obj["scores"][0]
                            t2_score = obj["scores"][1]
                            rounds = obj["remaining_rounds"]
                            if team_names[0] == team2:
                                t1_score, t2_score = t2_score, t1_score
                            if rounds == 1:
                                # Write result
                                worksheet.write(2, map_index, t1_score)
                                worksheet.write(3, map_index, t2_score)
                                if t1_score > t2_score:
                                    if (t1_score - t2_score) / t1_score >= 0.2:
                                        points = 5
                                    else:
                                        points = 4
                                elif t1_score < t2_score:
                                    if (t2_score - t1_score) / t2_score >= 0.2:
                                        points = 1
                                    else:
                                        points = 2
                                else:
                                    points = 3
                                worksheet.write(4, map_index, points)
                                done = True
                                break
                            else:
                                break
            if not done:
                worksheet.write(2, map_index, "N/A")
                worksheet.write(3, map_index, "N/A")
                worksheet.write(4, map_index, "N/A")

                        


workbook.close()