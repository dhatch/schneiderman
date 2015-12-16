#!/usr/bin/env python
import random
import itertools
from heapq import nlargest
import numpy
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

#given choices, an iterable of two items each, where the first item is the player and the
#second item is his e_v/salary ratio (and his probability of being chosen), select a player
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

#return the expected score of a lineup
def get_score(lineup):
    #dictionary mapping numbers to positions
    position_order = {1:'PG', 2:'SG', 3:'SF', 4:'PF', 5: 'C', 6:'G', 7:'F', 8:'UTIL'}
    score = 0
    for i in range(1, 9):
        score += lineup[position_order[i]].e_v
    return score
    
#return median of a list
#credit to http://stackoverflow.com/questions/24101524/finding-median-of-list-in-python
#pretty basic concept though
def get_median(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2
    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0

#generates a pretty good lineup
#which is a dictinoary with key position type and value player class (which is what the database returns)
def get_lineup(players): #players is dict of key position (so like "PG") and value list of players
    #website specific stats
    min_salary = 3000

    #dictionary mapping numbers to positions
    position_order = {1:'PG', 2:'SG', 3:'SF', 4:'PF', 5: 'C', 6:'G', 7:'F', 8:'UTIL'}
    
    #make iterables of (player, prob_to_be_chosen)
    distributions = {} #key position value iterable

    for i in range(1, 9):
        dist = []
        for p in players[position_order[i]]:
            dist.append((p, 1.0*p.e_v/p.salary))
        distributions[position_order[i]] = dist
        #to get one, use weighted_choice(distributions["PG"]), etc.

    #roster we are constructing, key position, value name THIS IS NOT RETURNED
    roster = {}
    #lineup we are constructing.  key position, value instance of player class THIS IS RETURNED
    lineup = {}
    #randomize order we pick positions in
    shuffled = range(1,9)
    random.shuffle(shuffled)
    salary = 50000
    players_left = 7
    for i in shuffled:
        #get a player p of position position_order[i] whose salary is small enough and isn't on our roster
        chosen = weighted_choice(distributions[position_order[i]])
        while (chosen.salary > salary - min_salary*players_left or chosen.name in roster.values()):
            #pick a new one
            chosen = weighted_choice(distributions[position_order[i]])
        #subtract his salary from salary
        salary -= chosen.salary
        roster[position_order[i]] = chosen.name
        lineup[position_order[i]] = chosen
        players_left -= 1
    return lineup


#runs the lineup generator
def main():
    #TODO: figure out how long something has been on the list
    #aka make lineups a list of tuple (roster, times)

    #read csv
    players = {}
    players["PG"] = []
    players["SG"] = []
    players["SF"] = []
    players["PF"] = []
    players["C"] = []
    players["G"] = []
    players["F"] = []
    players["UTIL"] = []
    a = open('testcsv', 'r')
    for line in a:
        line = line.split(',')
        p = player(name=line[0], position=line[1], e_v=float(line[2]), var=float(line[3]), diff = float(line[4]), salary=float(line[5]))
        players[p.position].append(p)
        if (p.position == 'PG' or p.position == 'SG'):
            players['G'].append(p)
        elif (p.position == 'SF' or p.position == 'PF'):
            players['F'].append(p)
        players['UTIL'].append(p)

    #dictionary mapping numbers to positions
    position_order = {1:'PG', 2:'SG', 3:'SF', 4:'PF', 5: 'C', 6:'G', 7:'F', 8:'UTIL'}

    #generate a bunch of lineups
    #get the threshold for the top x%
    threshold = 0
    num_lineups = 1000
    num_shakes = 50
    lineups = []
    tuning_num = 10000
    thresh_num = 50
    tuning = []
    #tune threshold
    for i in range(0, tuning_num):
        print i 
        print "in tuning"
        cur_lineup = get_lineup(players)
        tuning.append(get_score(cur_lineup))
    indices = range(0,tuning_num)
    tuning = iter(tuning)
    threshold = min(nlargest(thresh_num, tuning)) 

    print "TUNED"

    #make a box of lineups
    for i in range(0, num_lineups):
        score = 0
        while (score < threshold):
            cur_lineup = get_lineup(players)
            score = get_score(cur_lineup)
        lineups.append(cur_lineup)

    print "made a box"

    #shake the box num_shakes times
    for i in range(0,num_shakes):
        #simulate player shit
        scores = {}
        for i in range(1,9):
            for p in players[position_order[i]]:
                scores[p.name] = numpy.random.normal(p.e_v, p.var)
        lineup_scores = []
        for lineup in lineups:
            #evaluate lineups
            cur_score = 0
            for i in range(1, 9):
                cur_score += scores[lineup[position_order[i]].name]
            lineup_scores.append(cur_score)
        
        median = get_median(lineup_scores) #get median
        lower = set()
        for i in range(0, num_lineups):
            if (lineup_scores[i] < median):
                lower.add(i) #get a set of indices below

        #coinflip to cull the below median lineups, then refill
        added = 0
        new_lineups = []
        for i in range(0, num_lineups):#go through all lineups
            if i in lower: #maybe cull
                if random.choice([True, False]): #flip coin
                    added += 1
                    new_lineups.append(lineups[i])
            else: #don't cull
                added +=1
                new_lineups.append(lineups[i])
        for i in range(added, num_lineups): #refill
            new_lineups.append(get_lineup(players))
        lineups = new_lineups
    print lineups

if __name__ == "__main__":
    main()
