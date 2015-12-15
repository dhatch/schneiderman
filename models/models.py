import datetime

from pony.orm import *
from .db import db

class Team(db.Entity):
    id = PrimaryKey(int, auto=False)
    name = Required(str, 300)
    nba_abbreviation = Optional(str, 5)
    dk_abbreviation = Optional(str, 5)
    conference = Optional(str, 150)
    division = Optional(str, 150)
    code = Optional(str, 100)
    conference_rank = Optional(int)
    division_rank = Optional(int)
    wins = Optional(int)
    losses = Optional(int)
    win_percentage = Optional(float)

    players  = Set('Player')
    opposing_games = Set('PlayerGame') # A kind of useless reverse relationship.

class Player(db.Entity):
    id = PrimaryKey(int, auto=False)
    name = Required(str, 150)
    startYear = Optional(int)
    endYear = Optional(int)
    position = Optional(str, 20)

    team = Required(Team)
    games = Set('PlayerGame')

class PlayerGame(db.Entity):
    id = PrimaryKey(int, auto=False)
    date = Required(datetime.date)
    isHome = Optional(bool)
    didWin = Optional(bool)
    minutesPlayed = Optional(int)
    fieldGoalMade = Optional(int)
    fieldGoalAttempts = Optional(int)
    fieldGoalPercentage = Optional(float)
    threePointMade = Optional(int)
    threePointAttempted = Optional(int)
    threePointPercentage = Optional(float)
    freeThrowMade = Optional(int)
    freeThrowAttempted = Optional(int)
    freeThrowPercentage =  Optional(float)
    offensiveRebounds = Optional(int)
    defensiveRebounds = Optional(int)
    totalRebounds = Optional(int)
    assists = Optional(int)
    steals = Optional(int)
    blocks = Optional(int)
    turnovers = Optional(int)
    personalFouls = Optional(int)
    points = Optional(int)
    plusMinus = Optional(float)

    opponent = Required(Team)
    player = Required(Player)
