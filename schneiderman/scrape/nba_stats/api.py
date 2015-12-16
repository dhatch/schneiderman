import urlparse
import re

import requests
import dateutil.parser



API_ROOT = 'http://stats.nba.com/stats/'

class NbaApiResource(object):

    ENDPOINT = ''
    DEFAULT_PARAMETERS = {}
    ALLOWED_PARAMETERS = []

    def __init__(self):
        self.response = None
        self.resource_endpoint = urlparse.urljoin(API_ROOT, self.ENDPOINT)

    def reload(self):
        """Force reloading from API.  Clear cached data."""
        self.response = None
        self.make_request()

    def make_request(self, **kwargs):
        """Make request to api.

        :raises: requests.HTTPError if unsuccessful.

        Uses kwargs as request parameters.
        """
        if self.response is not None:
            return

        params = self.DEFAULT_PARAMETERS
        params.update({ key : val for key, val in kwargs.items()
                        if key in self.ALLOWED_PARAMETERS })
        self.response = requests.get(self.resource_endpoint, params=params)
        self.response.raise_for_status() # Check for success.

    def json(self, **kwargs):
        """Get own JSON data. Transformed to python dict.  Raw api resource response.

        kwargs are additional request parameters.
        """
        self.make_request(**kwargs)
        return self.response.json()

    def csv(self, **kwargs):
        """Get own data as CSV.  Returns an iterator of csv rows.

        The first row is the header row.
        kwargs are additional request parameters.
        """
        pass

class NbaPlayerList(NbaApiResource):
    ENDPOINT = 'commonallplayers'
    ALLOWED_PARAMETERS = ['IsOnlyCurrentSeason', 'LeagueID', 'Season']
    DEFAULT_PARAMETERS = {
        'IsOnlyCurrentSeason': 1,
        'LeagueID' : '00',
        'Season': '2015-16',
    }

    def json(self):
        """Get the player list.

        Cleaned api response:


        .. code-block:: javascript

            [
                {
                    'id' : Number,
                    'name': String,
                    'team': {
                        'id': Number,
                        'name': String,
                        'fromYear': Number,
                        'toYear': Number
                    }
                }
            ]

        :returns: An array of players.
        """
        json = super(NbaPlayerList, self).json()
        def transform(player):
            rt = dict()
            rt['id'] = player[0]
            rt['name'] = None
            names = map(lambda s: s.strip(), player[1].split(','))
            if len(names) == 2:
                names.reverse()
                rt['name'] = ' '.join(names).strip()
            elif len(names) == 1:
                rt['name']= ''.join(names).strip()
            else:
                raise TypeError("Invalid player name from API.")

            team = dict()
            team['id'] = player[6]
            team['name'] = (player[7] + ' ' + player[8]).strip()
            team['fromYear'] = player[3]
            team['toYear'] = player[4]
            rt['team'] = team
            return rt

        return [
            transform(player) for player in json['resultSets'][0]['rowSet']
        ]

    def csv(self, *args, **kwargs):
        """
        Columns: 'playerId', 'name', 'teamId', 'teamName', 'teamFromYear', 'teamToYear'

        :returns: An iterator for csv.
        """
        json = self.json()
        def transform(player):
            return [player['id'], player['name'], player['team']['id'],
                player['team']['name'], player['team']['fromYear'], player['team']['toYear']]

        yield ['playerId', 'name', 'teamId', 'teamName', 'teamFromYear', 'teamToYear']
        for player in json:
            yield transform(player)

class NbaPlayerGameLog(NbaApiResource):
    ENDPOINT = 'playergamelog'
    ALLOWED_PARAMETERS = ['PlayerID', 'LeagueID', 'Season', 'SeasonType']
    DEFAULT_PARAMETERS = {
        'LeagueID' : '00',
        'Season': '2015-16',
        'SeasonType' : 'Regular Season'
    }

    def __init__(self, player_id):
        super(NbaPlayerGameLog, self).__init__()
        self.player_id = player_id

    def json(self, **kwargs):
        """Get the game stats for a player.

        Cleaned api response:


        .. code-block:: python

            [
                {
                    'id' : int,
                    'playerId': int,
                    'date' : str,
                    'isHome' : bool,
                    'opponentTeamCode': str,
                    'didWin' bool,
                    'minutesPlayed': int,
                    'fieldGoalMade' : int,
                    'fieldGoalAttempts': int,
                    'fieldGoalPercentage': float,
                    'threePointMade': int,
                    'threePointAttempted': int,
                    'threePointPercentage': float,
                    'freeThrowMade': int,
                    'freeThrowAttempted': int,
                    'freeThrowPercentage': float,
                    'offensiveRebounds': int,
                    'defensiveRebounds': int,
                    'totalRebounds': int,
                    'assists': int,
                    'steals' : int,
                    'blocks': int,
                    'turnovers': int,
                    'personalFouls' : int,
                    'points' : int,
                    'plusMinus': float
                }
            ]

        :returns: An array of games.
        """
        params = kwargs
        params.update({
            'PlayerID' : self.player_id
        })
        json = super(NbaPlayerGameLog, self).json(**params)

        home_matchup_re = re.compile(r'^.+?vs\. (\w{3})$')
        away_matchup_re = re.compile(r'^.+?@ (\w{3})$')

        def transform(game):
            rt = dict()
            rt['id'] = int(game[2])
            rt['playerId'] = game[1]
            rt['date'] = game[3]

            # Parse matchup
            matchup = game[4]
            if 'vs' in matchup:
                rt['isHome'] = True
                rt['opponentTeamCode'] = home_matchup_re.match(matchup).group(1)
            elif '@' in matchup:
                rt['isHome'] = False
                rt['opponentTeamCode'] = away_matchup_re.match(matchup).group(1)
            else:
                raise TypeError("Invalid matchup")

            rt['didWin'] = game[5] == 'W'
            rt['minutesPlayed'] = game[6]
            rt['fieldGoalMade'] = game[7]
            rt['fieldGoalAttempts'] = game[8]
            rt['fieldGoalPercentage'] = game[9]
            rt['threePointMade'] = game[10]
            rt['threePointAttempted'] = game[11]
            rt['threePointPercentage'] = game[12]
            rt['freeThrowMade'] = game[13]
            rt['freeThrowAttempted'] = game[14]
            rt['freeThrowPercentage'] = game[15]
            rt['offensiveRebounds'] = game[16]
            rt['defensiveRebounds'] = game[17]
            rt['totalRebounds'] = game[18]
            rt['assists'] = game[19]
            rt['steals'] = game[20]
            rt['blocks'] = game[21]
            rt['turnovers'] = game[22]
            rt['personalFouls'] = game[23]
            rt['points'] = game[24]
            rt['plusMinus'] = game[25]
            return rt

        return [transform(game) for game in json['resultSets'][0]['rowSet']]

    def csv(self, **kwargs):
        json = self.json()
        yield json[0].keys()
        for game in json:
            yield game.values()

class NbaTeamList(NbaApiResource):
    ENDPOINT = 'leaguedashteamstats'
    ALLOWED_PARAMETERS = [
        'Conference',
        'DateFrom',
        'DateTo',
        'Division',
        'GameScope',
        'GameSegment',
        'LastNGames'
        'LeagueID',
        'Location',
        'MeasureType',
        'Month',
        'OpponentTeamId',
        'PORound',
        'PaceAdjust',
        'PerMode',
        'Period',
        'PlayerExperience',
        'PlayerPosition'
        'PlusMinus',
        'Rank',
        'Season',
        'SeasonSegment',
        'SeasonType',
        'ShotClockRange',
        'StarterBench'
        'TeamID',
        'VsConference',
        'VsDivision'
    ]

    DEFAULT_PARAMETERS = {
        'Conference': '',
        'DateFrom': '',
        'DateTo': '',
        'Division': '',
        'GameScope': '',
        'GameSegment': '',
        'LastNGames': 0,
        'LeaugeID': '00',
        'Location': '',
        'MeasureType': 'Base',
        'Month': 0,
        'OpponentTeamID': 0,
        'Outcome': '',
        'PORond': 0,
        'PaceAdjust': 'N',
        'PerMode': 'PerGame',
        'Period': 0,
        'PlayerExperience': '',
        'PlayerPosition': '',
        'PlusMinus': 'N',
        'Rank': 'N',
        'Season': '2015-16',
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'ShotClockRange': '',
        'StarterBench': '',
        'TeamID': 0,
        'VsConference': '',
        'VsDivision': ''
    }

    def json(self, **kwargs):
        """Return a list of team data.

        .. code-block: python
            [
                {
                    'id': int,
                    'name': str,
                }
            ]
        """
        json = super(NbaTeamList, self).json(**kwargs)
        def transform(team):
            return {
                'id': team[0],
                'name': team[1]
            }

        return [transform(team) for team in json['resultSets'][0]['rowSet']]

    def csv(self, **kwargs):
        json = self.json(**kwargs)
        yield ['id', 'name']
        for team in json:
            yield [team['id'], team['name']]


class NbaTeamInfo(NbaApiResource):
    ENDPOINT = 'teaminfocommon'
    ALLOWED_PARAMETERS = ['LeagueID', 'SeasonType', 'TeamID', 'Season']
    DEFAULT_PARAMETERS = {
        'LeagueID': '00',
        'SeasonType': 'Regular Season',
        'Season' : '2015-16'
    }

    def __init__(self, team_id):
        super(NbaTeamInfo, self).__init__()
        self.team_id = team_id

    def json(self, **kwargs):
        """Get cleaned team information:

        .. code-block: python

            [
                {
                    'id' : int,
                    'name' : str,
                    'abbreviation' : str,
                    'conference': str,
                    'division' : str,
                    'code' : str,
                    'conference_rank' : int,
                    'division_rank': int,
                    'wins': int,
                    'losses': int,
                    'win_percentage': float
                }
            ]

        """
        params = kwargs
        params.update({
            'TeamID': self.team_id
        })
        json = super(NbaTeamInfo, self).json(**params)
        def transform(team):
            rt = dict()
            rt['id'] = team[0]
            rt['name'] = (team[2].strip() + ' ' + team[3]).strip()
            rt['abbreviation'] = team[4]
            rt['conference'] = team[5]
            rt['division'] = team[6]
            rt['code'] = team[7]
            rt['wins'] = team[8]
            rt['losses'] = team[9]
            rt['win_percentage'] = team[10]
            rt['conference_rank'] = team[11]
            rt['division_rank'] = team[12]
            return rt

        return transform(json['resultSets'][0]['rowSet'][0])

    def csv(self, **kwargs):
        raise NotImplementedError("Detail resource does not support csv output.")
