"""
Survivor pool tester code
"""
import operator
import numpy as np


from util import get_elo_probabilities


# DP
# Compute: best way of getting to state {t_1, t_2, ..., t_i} together with the probability of arriving at that state
# one way of getting to state: {t_1, ..., t_{i-1}} + {t_i}, probability is best way of getting to earlier state multipled by probability t_i wins game
# Then: compute for each week the highest probability way of getting there, together with the associated best way
def survivor_dp():
    teams_playing_in_week = get_elo_probabilities()
    current_states = set([()])
    best_log_prob = {(): 0.0}
    best_path = {(): []}

    for week in range(6):
        next_states = set()
        next_log_prob_dict = {}
        for current_state in current_states:
            for team, log_prob in teams_playing_in_week[week]:
                if team in current_state:
                    continue
                next_state = tuple(sorted(list(current_state) + [team]))
                next_log_prob = best_log_prob[current_state] + log_prob
                if next_log_prob > next_log_prob_dict.get(next_state, -1e100):
                    next_log_prob_dict[next_state] = next_log_prob
                    best_path[next_state] = best_path[current_state] + [team]
                    next_states.add(next_state)

        # compute best log prob, best path
        best_state, best_prob = max(next_log_prob_dict.iteritems(), key=operator.itemgetter(1))
        path = best_path[best_state]
        print "Best after week ", week, np.exp(best_prob), path

        best_log_prob.update(next_log_prob_dict)
        current_states = next_states

    return current_states, best_log_prob, best_path

if __name__ == "__main__":
    cs, lgs, pths = survivor_dp()
    print len(cs)
