import random
from collections import defaultdict
from pprint import pprint as pp

import numpy as np
from scipy import stats

from util import do_cprofile, get_elo_probabilities, get_opponents_by_week

NWEEKS = 17


teams_playing_in_week = get_elo_probabilities()
probability_by_week = []
for team_prob_tuples in teams_playing_in_week:
    probability_by_week.append({t: np.exp(prob) for t, prob in team_prob_tuples})

opponents_by_week = get_opponents_by_week(teams_playing_in_week)

# convert team probs into a dict of teams and normalized probabilities
team_sample_probs_by_week = []
for team_prob_tuples in teams_playing_in_week:
    t_p_tuples = [(t, np.exp(p) ** 1.5) for t, p in team_prob_tuples]
    teams, probs = zip(*t_p_tuples)
    normalized_probs = np.array(probs) / sum(probs)
    team_sample_probs_by_week.append((teams, normalized_probs))


def repeat_until(pred, fn):
    x = fn()
    while not pred(x):
        x = fn()
    return x


def weighted_sample((teams, probs)):
    return np.random.choice(teams, p=probs)


# Simulate a week of the season
def simulate_week(week, players, seed_outcome):
    # outcomes: dict mapping {(home, away): {home, away}}
    # seed_outcome: maps {week: {team: outcome}}
    if seed_outcome is not None:
        outcomes = dict(seed_outcome.get(week, {}))
    else:
        outcomes = {}

    survivors = []
    for i, strikes, player in players:
        if len(player) > week:
            survivors.append((i, strikes, player))
            continue

        # for each player, randomly pick teams for each week weighted by win probability ** 1.5
        cur_team = repeat_until(lambda team: team not in player,
                                lambda: weighted_sample(team_sample_probs_by_week[week]))

        if cur_team not in outcomes:
            # sample and cache the game outcome
            outcomes[cur_team] = probability_by_week[week][cur_team] > random.random()
            outcomes[opponents_by_week[week][cur_team]] = not outcomes[cur_team]

        if outcomes[cur_team]:
            # prepare for the next week
            survivors.append((i, strikes, player + [cur_team]))
        else:
            if strikes == 0 and week <= 2:
                survivors.append((i, strikes + 1, player + [cur_team]))

    return survivors

# print simulate_week(3, [(0, 0, []), (1, 0, [])], {})


def compute_winner(players):
    zero_strike_win = {p for p, strikes, _ in players if strikes == 0}
    if zero_strike_win:
        return zero_strike_win
    return {p for p, _, _ in players}


# Simulate the remainder of the season.
def simulate_season(start_week, players, seed_outcome=None):
    for i in range(start_week, NWEEKS):
        next_players = simulate_week(i, players, seed_outcome)
        if len(next_players) == 0:
            # winnings split among previous players
            return i, compute_winner(players)
        players = next_players
    return i, compute_winner(players)
# print simulate_season(3, CURRENT_STATUS)


CURRENT_STATUS = [
    # player id, strikes, teams
    (0, 0, ['MIA', 'PIT', 'SEA']),  # replacement
#    (1, 1, ['DAL', 'NO']), # albert
#    (2, 1, ['DAL', 'NO']), # dart thrower
    (3, 1, ['DEN', 'IND', 'SEA']),  # dont forget
    (4, 1, ['CIN', 'NO', 'SEA']),  # i miss the nba
    (5, 1, ['GNB', 'BAL', 'NE']),  # Jeff
    (6, 1, ['NE', 'IND', 'SEA']),  # JPWB
#    (7, 1, ['DAL', 'IND']), # Levi's or bust
    (8, 1, ['DAL', 'NO', 'SEA']),  # Ty Montgomery
    (9, 1, ['CAR', 'BAL', 'SEA']),  # Weeden
    (10, 1, ['DAL', 'NO', 'CAR']),  # Z House
    (11, 1, ['DAL', 'NO', 'SEA']),  # zzz
    ]

# CURRENT_STATUS = [
#     # player id, strikes, teams
#     (0, 0, ['MIA', 'PIT']),  # replacement
# #    (1, 1, ['DAL', 'NO']), # albert
# #    (2, 1, ['DAL', 'NO']), # dart thrower
#     (3, 1, ['DEN', 'IND']),  # dont forget
#     (4, 1, ['CIN', 'NO']),  # i miss the nba
#     (5, 1, ['GNB', 'BAL']),  # Jeff
#     (6, 1, ['NE', 'IND']),  # JPWB
# #    (7, 1, ['DAL', 'IND']), # Levi's or bust
#     (8, 1, ['DAL', 'NO']),  # Ty Montgomery
#     (9, 1, ['CAR', 'BAL']),  # Weeden
#     (10, 1, ['DAL', 'NO']),  # Z House
#     (11, 1, ['DAL', 'NO']),  # zzz
#     ]


# Simulate many seasons, gather statistics
# average utilities over all random runs
# TODO maybe do bootstrap / online variance calculations?
def simulate_seasons(N, start_week, players):
    winner_equity = defaultdict(float)
    last_weeks = []
    for i in range(N):
        if i % 1000 == 0:
            print i
        last_week, winners = simulate_season(start_week, players)
        for winner in winners:
            winner_equity[winner] += 1. / len(winners)
        last_weeks.append(last_week)

    pp({p: "%.2f" % (100 * e / N) for p, e in winner_equity.iteritems()})
    print stats.describe(last_weeks)
    print stats.histogram(last_weeks)


if __name__ == "__main__":
    simulate_seasons(100000, start_week=3, players=CURRENT_STATUS)
