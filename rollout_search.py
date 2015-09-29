from operator import itemgetter
from collections import defaultdict

from monte_carlo import CURRENT_STATUS, simulate_season, probability_by_week
from util import TEAMS


def next_best_move(N, players, cur_idx):
    cur_player = None
    other_players = []
    for i, strikes, player in players:
        if i == cur_idx:
            cur_player = (i, strikes, player)
        else:
            other_players.append((i, strikes, player))

    week = len(cur_player[2])
    print "Computing for week: ", week + 1

    results = []
    for t in TEAMS:
        print "Processing: ", t
        if t not in probability_by_week[week]:
            # bye week
            continue

        if t in cur_player[2]:
            # already chosen
            continue

        winner_equity = 0.0
        next_player = (cur_player[0], cur_player[1], cur_player[2] + [t])
        next_outcomes = {week: {t: True}}
        for run in range(N):
            if run > 0 and run % 1000 == 0:
                print run

            winners = simulate_season(week, players + [next_player], next_outcomes)
            if cur_idx in winners:
                winner_equity += 1. / len(winners)

        prob_win = probability_by_week[week][t]
        equity = winner_equity / float(N)
        results.append((t, equity, prob_win, prob_win * equity))

    print
    print "RESULTS"
    print
    row_format = "{:>15.3}" * len(results[0])
    for entry in sorted(results, key=itemgetter(-1), reverse=True):
        print row_format.format(*entry)


if __name__ == "__main__":
    next_best_move(100000, CURRENT_STATUS, 11)
