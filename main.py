import json
import math
import numpy as np

for test_case_numbers in range(26, 51):
    print(test_case_numbers)
    test_case_number = str(test_case_numbers)
    while len(test_case_number) < 3:
        test_case_number = "0" + test_case_number

    inputFILE = test_case_number + ".json"
    outputFILE = "output " + test_case_number + ".json"
    inp = open(inputFILE, "r")
    data = json.load(inp)
    inp.close()

    base_speed = data["hero"]["base_speed"]
    base_power = data["hero"]["base_power"]
    base_range = data["hero"]["base_range"]
    level_speed_coeff = data["hero"]["level_speed_coeff"]
    level_power_coeff = data["hero"]["level_power_coeff"]
    level_range_coeff = data["hero"]["level_range_coeff"]
    start_x = data["start_x"]
    start_y = data["start_y"]
    width = data["width"]
    height = data["height"]
    num_turns = data["num_turns"]
    monsters = data["monsters"]
    monsters_cnt = len(monsters)
    enemies = np.arange(monsters_cnt * 6).reshape(monsters_cnt, 6)
    GOLD = 0
    EXP = 0
    LVL = 0
    DATA = np.array([])

    for i in range(monsters_cnt):
        enemies[i][0] = monsters[i]["x"]
        enemies[i][1] = monsters[i]["y"]
        enemies[i][2] = monsters[i]["hp"]
        enemies[i][3] = monsters[i]["gold"]
        enemies[i][4] = monsters[i]["exp"]
        enemies[i][5] = i  # target_id


    def my_speed():
        return int(base_speed * (1 + LVL * level_speed_coeff / 100))


    def my_power():
        return int(base_power * (1 + LVL * level_power_coeff / 100))


    def my_range():
        return int(base_range * (1 + LVL * level_range_coeff / 100))


    def move(x, y):
        global num_turns, DATA, start_x, start_y
        num_turns -= 1
        start_x = int(x)
        start_y = int(y)
        DATA = np.append(DATA, {"type": "move",
                                "target_x": int(x),
                                "target_y": int(y)})


    def tarmacnel():
        global LVL, EXP
        while 1:
            pts = 1000 + LVL * (LVL + 1) * 50
            if EXP >= pts:
                EXP -= pts
                LVL += 1
            else:
                break


    def attack(idx):
        global num_turns, DATA, enemies, GOLD, EXP
        num_turns -= 1
        DATA = np.append(DATA, {
            "type": "attack",
            "target_id": int(enemies[idx][5])
        })
        if enemies[idx][2] <= my_power():
            GOLD += enemies[idx][3]
            EXP += enemies[idx][4]
            tarmacnel()
            enemies = np.delete(enemies, idx, 0)
        else:
            enemies[idx][2] -= my_power()


    def dist2(x, y, xs, ys):
        return (x - xs) * (x - xs) + (y - ys) * (y - ys)


    enemies = sorted(enemies, key=lambda x: -x[3])


    # enemies = sorted(enemies, key=lambda x: -x[3] / x[2])

    def optimal_monster(from_x, from_y):
        idx = -1
        for cur_idx in range(min(100, len(enemies))):
            if idx == -1:
                idx = cur_idx
            elif (dist2(from_x, from_y, enemies[cur_idx][0], enemies[cur_idx][1]) <
                  dist2(from_x, from_y, enemies[idx][0], enemies[idx][1])):
                idx = cur_idx
        return idx


    def GO(from_x, from_y, to_x, to_y):  # move towards to_x, to_y: coordinates are integers
        spd = my_speed()
        D_x = to_x - from_x
        D_y = to_y - from_y

        nerqnacig = math.sqrt(D_x ** 2 + D_y ** 2)

        U_x = D_x / nerqnacig
        U_y = D_y / nerqnacig
        spd = min(spd, int(nerqnacig))
        C_x = from_x + spd * U_x
        C_y = from_y + spd * U_y
        if U_x < 0:
            C_x = math.ceil(C_x)
        if U_y < 0:
            C_y = math.ceil(C_y)
        move(C_x, C_y)


    while num_turns > 0:
        next_kill = optimal_monster(start_x, start_y)
        if next_kill == -1:
            break
        if dist2(start_x, start_y, enemies[next_kill][0], enemies[next_kill][1]) < my_range() * my_range():
            attack(next_kill)
            continue
        else:
            GO(start_x, start_y, enemies[next_kill][0], enemies[next_kill][1])

    finaldata = dict()
    finaldata["moves"] = DATA.tolist()
    try:
        f = open(outputFILE, "x")
    except:
        pass

    with open(outputFILE, 'w') as out:
        json.dump(finaldata, out)
