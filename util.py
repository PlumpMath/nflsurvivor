import fileinput
import json


import numpy as np


ALIASES = {
    'New England': 'NE',
    'Denver': 'DEN',
    'Seattle': 'SEA',
    'Green Bay': 'GB',
    'Arizona': 'ARI',
    'Pittsburgh': 'PIT',
    'Cincinnati': 'CIN',
    'Dallas': 'DAL',
    'Buffalo': 'BUF',
    'Carolina': 'CAR',
    'Kansas City': 'KC',
    'Atlanta': 'ATL',
    'Philadelphia': 'PHI',
    'Indianapolis': 'IND',
    'Baltimore': 'BAL',
    'Minnesota': 'MIN',
    'San Francisco': 'SF',
    'San Diego': 'SD',
    'Houston': 'HOU',
    'Detroit': 'DET',
    'N.Y. Jets': 'NYJ',
    'N.Y. Giants': 'NYG',
    'Miami': 'MIA',
    'St. Louis': 'STL',
    'New Orleans': 'NO',
    'Oakland': 'OAK',
    'Cleveland': 'CLE',
    'Chicago': 'CHI',
    'Washington': 'WSH',
    'Tennessee': 'TEN',
    'Tampa Bay': 'TB',
    'Jacksonville': 'JAX',
    }

TEAMS = [
    "PIT",
    "IND",
    "MIA",
    "KC",
    "GB",
    "SEA",
    "CLE",
    "CAR",
    "DET",
    "NO",
    "CIN",
    "BAL",
    "TEN",
    "NYG",
    "PHI",
    "MIN",
    "NE",
    "BUF",
    "WSH",
    "HOU",
    "CHI",
    "STL",
    "NYJ",
    "JAX",
    "SD",
    "ARI",
    "OAK",
    "DEN",
    "TB",
    "DAL",
    "ATL",
    "SF",
    ]


def canonicalize_team(team_name):
    return ALIASES.get(team_name, team_name)


def elo_to_spread(home_team, away_team, ratings):
    # home field worth 65 elo points, divide by 25 to get point spread
    return float(ratings[home_team] + 65 - ratings[away_team]) / 25


def elo_to_probability_home_win(home_elo, away_elo):
    # http://fivethirtyeight.com/datalab/introducing-nfl-elo-ratings/
    # 1 / (10^(-ELODIFF / 400) + 1)
    return 1. / (10 ** (-float(home_elo + 65 - away_elo) / 400.) + 1)


def get_elo_probabilities(infile='data/elo_ratings_week_3.txt'):
    elo_ratings = {}
    for line in fileinput.input(infile):
        rating, _, team_name = line.strip().partition(' ')
        elo_ratings[canonicalize_team(team_name)] = int(rating)

    # fill in schedule
    home_team_by_weeks = get_schedule()

    team_prob_by_week = []
    team_prob_tuples_by_week = []
    for home_team_dict in home_team_by_weeks:
        team_prob_dict = {}
        for home, away in home_team_dict.iteritems():
            prob = elo_to_probability_home_win(elo_ratings[home], elo_ratings[away])
            team_prob_dict[home] = np.log(prob)
            team_prob_dict[away] = np.log(1 - prob)
        team_prob_by_week.append(team_prob_dict)
        team_prob_tuples_by_week.append(team_prob_dict.items())

    # make sure we get the same numbers as the scrape data
    # for i, team_prob_tuples in enumerate(parse_538_elo_data()):
    #     if i < 3: continue
    #     for t, prob in team_prob_tuples:
    #         assert abs(np.exp(team_prob_by_week[i][t]) - np.exp(prob)) < 0.01

    return team_prob_tuples_by_week


def get_schedule(infile='data/2015_schedule.json'):
    """
    Returns a list of dictionaries mapping home to away team for that week
    """
    with open(infile) as f:
        return json.load(f)


def get_home_teams(teams_playing_in_week):
    week_dicts = []
    for team_prob_tuples in teams_playing_in_week:
        away_teams = [t for t, _ in team_prob_tuples[:len(team_prob_tuples) / 2]]
        home_teams = [t for t, _ in team_prob_tuples[len(team_prob_tuples) / 2:]]
        away_week = {away: home for away, home in zip(away_teams, home_teams)}
        home_week = {h: a for a, h in away_week.iteritems()}
        week_dicts.append(home_week)
    return week_dicts


def get_opponents_by_week(teams_playing_in_week):
    week_dicts = []
    for team_prob_tuples in teams_playing_in_week:
        away_teams = [t for t, _ in team_prob_tuples[:len(team_prob_tuples) / 2]]
        home_teams = [t for t, _ in team_prob_tuples[len(team_prob_tuples) / 2:]]
        away_week = {away: home for away, home in zip(away_teams, home_teams)}
        home_week = {h: a for a, h in away_week.iteritems()}
        away_week.update(home_week)
        week_dicts.append(away_week)
    return week_dicts


def do_cprofile(func):
    import cProfile

    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats(sort='time')
    return profiled_func
