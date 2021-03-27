import random
import copy
import time


d1 = ["Ross", "Austin", "Thomas", "Kurt", "Nick"]
d2 = ["Eric", "Matt", "Logan", "Danny", "Graeme"]
rivalry = [("Ross", "Eric"), ("Austin", "Graeme"), ("Kurt", "Danny"), ("Matt", "Logan"), ("Thomas", "Nick")]
base_schedule = {1: [],
                 2: [],
                 3: rivalry,
                 4: [],
                 5: [],
                 6: [],
                 7: [],
                 8: [],
                 9: [],
                 10: [],
                 11: [],
                 12: [],
                 13: []}


class ScheduleError(Exception):
    pass


# Generates a list of games outside of Rivalry week
def build():
    game_list = []
    for name in d1:
        for opp in d1:
            temp = (name, opp)
            if not(name is opp) and temp not in rivalry:
                game_list.append(temp)
        for opp in d2:
            temp = (name, opp)
            if temp not in rivalry:
                game_list.append(temp)
    for name in d2:
        for opp in d2:
            temp = (name, opp)
            if not(name is opp) and temp not in rivalry:
                game_list.append(temp)
    return game_list


# Checks if either team already plays that week
def check_week(week, name1, name2):
    for g in week:
        if name1 in g or name2 in g:
            return False
    return True


def checkGame(games, team1, team2, temp_games):
    if not check_week(temp_games, team1, team2):
        return False
    game = (team1, team2)
    if game in games:
        return game
    game = (team2, team1)
    if game in games:
        return game
    return False

# Prints nicely
def pretty_print(schedule):
    for week in range(1,14):
        print("Week " + str(week))
        for home, away in schedule[week]:
            print(home + " v. " + away)


def inner(i, teams, temp_games, games):
    for j in range(0, len(teams)):
        if i is j:
            continue
        game = checkGame(games, teams[i], teams[j], temp_games)
        if game:
            return game
    return False


def getTeamsLeftToPlay(schedule, week, games):
    cur_week = schedule[week]
    teams = d1 + d2
    for home, away in schedule[week]:
        teams.remove(home)
        teams.remove(away)
    random.shuffle(teams)
    temp_games = []
    for i in range(0, len(teams)):
        game = inner(i, teams, temp_games, games)
        if game:
            temp_games.append(game)
        else:
            continue
        if (len(temp_games) + len(cur_week)) == 5:
            for g in temp_games:
                games.remove(g)
                schedule[week].append(g)
            return True
    raise ScheduleError


def getGame(games):
    return games.pop()


def getKeys(dic):
    return list(dic.keys())


def generate(games, schedule):
    while games:
        home, away = getGame(games)
        temp_weeks = getKeys(schedule)
        while temp_weeks:
            week = random.choice(temp_weeks)
            if check_week(schedule[week], home, away):
                # If the teams can play schedule them
                schedule[week].append((home, away))
                if len(schedule[week]) == 2:
                    getTeamsLeftToPlay(schedule, week, games)
                break
            temp_weeks.remove(week)
            # Throw Exception if game can't be scheduled
            if not temp_weeks:
                raise ScheduleError
    return schedule


def run(printing):
    count = 0
    while True:
        try:
            games = copy.deepcopy(base_games)
            schedule = copy.deepcopy(base_schedule)
            random.shuffle(games)
            schedule = generate(games, schedule)
            if printing:
                pretty_print(schedule)
            break
        except ScheduleError:
            # print(cnt)
            count += 1
    print(str(count) + " Fails")
    return count

#params
runs = 100
printing = False

cnt = 0
start_time = time.time()
# Runs until it finds a solution
base_games = build()
for x in range(runs):
    print("Run %s" % x)
    cnt += run(printing)
print("--- %s Runs" % runs)
print("--- %s Fails per Run" % (cnt/runs))
print("--- %s Seconds per Run" % ((time.time() - start_time)/runs))
