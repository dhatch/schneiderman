#!/usr/bin/env python
import random
import itertools
from heapq import nlargest
import numpy
import math


class player:

    def __init__(self, name, position, e_v, var, diff, salary):
        self.name = name
        self.position = position
        self.e_v = e_v
        self.var = var
        self.diff = diff
        self.salary = salary

    def __repr__(self):
        return self.name
    name = ''
    position = ''
    e_v = 0
    var = 0
    diff = 0
    salary = 0


def set_var(players, pvar, p):
    # dictionary mapping numbers to positions
    position_order = {1: 'PG', 2: 'SG', 3: 'SF',
                      4: 'PF', 5: 'C', 6: 'G', 7: 'F', 8: 'UTIL'}
    for position in position_order.values():
        # go through players[position], which is a list
        for player in players[position]:
            if player.name == p:
                player.var = pvar

# given choices, an iterable of two items each, where the first item is the player and the
# second item is his e_v/salary ratio (and his probability of being
# chosen), select a player


def weighted_choice(choices):
    total = 0.0
    for choice in choices:
        total += choice[1]
    r = random.uniform(0, total)
    upto = 0
    for choice in choices:
        if upto + choice[1] >= r:
            return choice[0]
        upto += choice[1]
    assert False, "Shouldn't get here"

# return the expected score of a lineup


def get_score(lineup):
    # dictionary mapping numbers to positions
    position_order = {1: 'PG', 2: 'SG', 3: 'SF',
                      4: 'PF', 5: 'C', 6: 'G', 7: 'F', 8: 'UTIL'}
    score = 0
    for i in range(1, 9):
        score += lineup[position_order[i]].e_v
    return score

# return the salary of a lineup


def get_salary(lineup):
    # dictionary mapping numbers to positions
    position_order = {1: 'PG', 2: 'SG', 3: 'SF',
                      4: 'PF', 5: 'C', 6: 'G', 7: 'F', 8: 'UTIL'}
    salary = 0
    for i in range(1, 9):
        salary += lineup[position_order[i]].salary
    return salary

# return median of a list
# credit to http://stackoverflow.com/questions/24101524/finding-median-of-list-in-python
# pretty basic concept though


def get_median(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2
    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1]) / 2.0

# generates a pretty good lineup
# which is a dictinoary with key position type and value player class
# (which is what the database returns)


def get_lineup(players):  # players is dict of key position (so like "PG") and value list of players
    # website specific stats
    min_salary = 4000

    # dictionary mapping numbers to positions
    position_order = {1: 'PG', 2: 'SG', 3: 'SF',
                      4: 'PF', 5: 'C', 6: 'G', 7: 'F', 8: 'UTIL'}

    # make iterables of (player, prob_to_be_chosen)
    distributions = {}  # key position value iterable
    for i in range(1, 9):
        dist = []
        for p in players[position_order[i]]:
            dist.append((p, 1.0 * p.e_v / p.salary))
            #dist.append((p, (1.0*p.e_v/p.salary)**2))
        distributions[position_order[i]] = dist
        # to get one, use weighted_choice(distributions["PG"]), etc.
    # roster we are constructing, key position, value name THIS IS NOT RETURNED
    roster = {}
    # lineup we are constructing.  key position, value instance of player
    # class THIS IS RETURNED
    lineup = {}
    # randomize order we pick positions in
    shuffled = range(1, 9)
    random.shuffle(shuffled)
    salary = 50000
    players_left = 7
    # pick initial lineup
    for i in shuffled:
        # get a player p of position position_order[i] whose salary is small
        # enough and isn't on our roster
        chosen = weighted_choice(distributions[position_order[i]])
        while (chosen.salary >= salary - min_salary * players_left or chosen.name in roster.values()):
            chosen = weighted_choice(distributions[position_order[i]])
        # subtract his salary from salary
        salary -= chosen.salary
        roster[position_order[i]] = chosen.name
        lineup[position_order[i]] = chosen
        players_left -= 1
    changed = 0
    # improve lineup
    while (salary > 500 and changed > -5):
        shuffled = range(1, 9)
        random.shuffle(shuffled)
        changed -= 1
        for i in shuffled:
            chosen = weighted_choice(distributions[position_order[i]])
            d_salary = -lineup[position_order[i]].salary + chosen.salary
            if (lineup[position_order[i]].e_v < chosen.e_v and d_salary <= salary and chosen.name not in roster.values()):
                # replace this guy, update salary, roster, lineup
                roster[position_order[i]] = chosen.name
                lineup[position_order[i]] = chosen
                salary -= d_salary
                changed += 1
    return lineup


# runs the lineup generator
def main():
    # todo: implement variance
    # todo: capture anything that gets to 10
    # todo: say how many times each player is used

    # dictionary mapping numbers to positions
    position_order = {1: 'PG', 2: 'SG', 3: 'SF',
                      4: 'PF', 5: 'C', 6: 'G', 7: 'F', 8: 'UTIL'}

    # read csv
    players = {}
    players["PG"] = []
    players["SG"] = []
    players["SF"] = []
    players["PF"] = []
    players["C"] = []
    players["G"] = []
    players["F"] = []
    players["UTIL"] = []
    a = open('data/predict/predictions.csv', 'r')
    for line in a:
        line = line.split(',')
        p = player(name=line[0], position=line[1], e_v=float(line[2]), var=float(
            line[3]), diff=float(line[4]), salary=float(line[4]))
        players[p.position].append(p)
        if (p.position == 'PG' or p.position == 'SG'):
            players['G'].append(p)
        elif (p.position == 'SF' or p.position == 'PF'):
            players['F'].append(p)
        players['UTIL'].append(p)
    # set variances
    for i in range(1, 6):
        a = open('data/train/resid_' + position_order[i] + '.csv', 'r')
        # key player name, key (sum squared resid, num_games)
        variance_dict = {}
        for line in a:
            line = line.split(',')
            if line[0] not in variance_dict.keys():
                variance_dict[line[0]] = [
                    float(line[1]) ** 2, 1.0]  # [ssr, n_games]
            else:
                variance_dict[line[0]][0] += float(line[1]) ** 2
                variance_dict[line[0]][1] += 1.0
        for p in variance_dict.keys():
            pvar = math.sqrt(variance_dict[p][0] / variance_dict[p][1])
            set_var(players, pvar, p)

    # generate a bunch of lineups
    # get the threshold for the top x%
    threshold = 0
    num_lineups = 100
    num_shakes = 50
    lineups = []
    times = []
    tuning_num = 10000
    thresh_num = 50
    tuning = []
    # tune threshold
    for i in range(0, tuning_num):
        print i
        print "in tuning"
        cur_lineup = get_lineup(players)
        tuning.append(get_score(cur_lineup))
    indices = range(0, tuning_num)
    tuning = iter(tuning)
    threshold = min(nlargest(thresh_num, tuning))

    print "TUNED"
    # make a box of lineups
    for i in range(0, num_lineups):
        print i
        score = 0
        while (score < threshold):
            cur_lineup = get_lineup(players)
            score = get_score(cur_lineup)
        lineups.append(cur_lineup)
        times.append(0)
    print "made a box"

    # shake the box num_shakes times
    for i in range(0, num_shakes):
        # simulate player shit
        scores = {}
        for i in range(1, 9):
            for p in players[position_order[i]]:
                scores[p.name] = numpy.random.normal(p.e_v, p.var)
                """
                print p.name
                normal = "normal: " + str(p.e_v)
                real = "actual: " + str(scores[p.name])
                print normal
                print real
                """
                #scores[p.name] = p.e_v
        lineup_scores = []
        for lineup in lineups:
            # evaluate lineups
            cur_score = 0
            for i in range(1, 9):
                cur_score += scores[lineup[position_order[i]].name]
            lineup_scores.append(cur_score)

        median = get_median(lineup_scores)  # get median
        lower = set()
        for i in range(0, num_lineups):
            if (lineup_scores[i] < median):
                lower.add(i)  # get a set of indices below

        # coinflip to cull the below median lineups, then refill
        added = 0
        new_lineups = []
        new_times = []
        for i in range(0, num_lineups):  # go through all lineups
            if i in lower:  # maybe cull
                if random.choice([True, False]):  # if true, not culled
                    added += 1
                    new_lineups.append(lineups[i])
                    new_times.append(times[i] + 1)
            else:  # don't cull
                added += 1
                new_lineups.append(lineups[i])
                new_times.append(times[i] + 1)
        for i in range(added, num_lineups):  # refill
            new_lineups.append(get_lineup(players))
            new_times.append(0)
        lineups = new_lineups
        times = new_times
        print times

    player_times = {}  # key player name, value number of times he was chosen
    for (l, t) in zip(lineups, times):
        print l
        print get_score(l)
        print get_salary(l)
        print t
        for p in l.values():
            if p.name in player_times.keys():
                player_times[p.name] += 1
            else:
                player_times[p.name] = 1
    inv_map = {}
    for k, v in player_times.iteritems():
        inv_map[v] = inv_map.get(v, [])
        inv_map[v].append(k)
    for a, b in inv_map.iteritems():
        print a
        print b
if __name__ == "__main__":
    main()
