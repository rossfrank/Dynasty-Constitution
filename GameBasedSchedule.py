import random
import copy
import time


d1 = ["Ross", "Austin", "Thomas", "Kurt", "Nick"]
d2 = ["Eric", "Matt", "Logan", "Danny", "Graeme"]
weeks = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Week 7",
         "Week 8", "Week 9", "Week 10", "Week 11", "Week 12", "Week 13"]
rivalry = [("Ross", "Eric"), ("Austin", "Graeme"), ("Kurt", "Danny"), ("Matt", "Logan"), ("Thomas", "Nick")]
base_schedule = {"Week 1": [],
                 "Week 2": [],
                 "Week 3": rivalry,
                 "Week 4": [],
                 "Week 5": [],
                 "Week 6": [],
                 "Week 7": [],
                 "Week 8": [],
                 "Week 9": [],
                 "Week 10": [],
                 "Week 11": [],
                 "Week 12": [],
                 "Week 13": []}


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


# Prints nicely
def pretty_print(schedule):
    for week in weeks:
        print week
        for home, away in schedule[week]:
            print home + " v. " + away


# Adds the last game to the week
def finish_week(schedule, week, games):
    teams = d1 + d2
    for g in schedule[week]:
        home, away = g
        teams.remove(home)
        teams.remove(away)
    game = (teams[0], teams[1])
    if game not in games:
        game = (teams[1], games[0])
    games.remove(game)
    schedule[week].append(game)


def run(games):
    schedule = copy.deepcopy(base_schedule)
    random.shuffle(games)
    while games:
        game = games.pop()
        home, away = game
        temp_weeks = schedule.keys()
        while temp_weeks:
            week = random.choice(temp_weeks)
            if check_week(schedule[week], home, away):
                # If the teams can play schedule them
                schedule[week].append(game)
                # If 8 teams are already scheduled, schedule the last one
                if len(schedule[week]) is 4:
                    finish_week(schedule, week, games)
                break
            temp_weeks.remove(week)
            # Throw Exception if game can't be scheduled
            if not temp_weeks:
                raise Exception
    pretty_print(schedule)

cnt = 0
start_time = time.time()
# Runs until it finds a solution
base_games = build()
while True:
    try:
        games = copy.deepcopy(base_games)
        run(games)
        break
    except Exception:
        cnt += 1
print str(cnt) + " Fails"
print("--- %s minutes ---" % ((time.time() - start_time)/60))
