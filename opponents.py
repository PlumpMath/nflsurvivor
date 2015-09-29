from collections import Counter

from pprint import pprint as pp

from util import get_schedule

# Given a survivor pool genome, list the opponents

schedule = get_schedule()


def find_opponents(genome):
    opponents = []
    for i, (team, home_to_away) in enumerate(zip(genome, schedule)):
        if team not in home_to_away:
            print "Huh? not a home game?"
            print team
        else:
            print "Week %d: %s vs %s" % (i + 1, team, home_to_away[team])
            opponents.append(home_to_away[team])
    return opponents

# genome = ['DAL', 'NO', 'SEA', 'IND', 'KC', 'NYJ', 'SD', 'NE', 'PIT', 'BAL', 'CAR', 'GB']
genome = ['DAL', 'NO', 'SEA', 'IND', 'KC', 'DEN', 'NE', 'ATL', 'CIN', 'PIT', 'CAR', 'GB']

opponents = find_opponents(genome)
pp(Counter(opponents))
