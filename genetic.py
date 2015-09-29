import random
import numpy as np

from operator import itemgetter

from util import get_elo_probabilities, TEAMS


# monte carlo simulation suggests 12.5 for 10 ppl at 0.75, 10.5 for 10 ppl at .7
# lets go for week 12
GAMES = 12
POPULATION = 1000
PRUNE = 0.1
GENERATIONS = 100

#STARTING_PICKS = ['MIA', 'PIT']
STARTING_PICKS = ['DAL', 'NO', 'SEA']
NUM_STARTING_PICKS = len(STARTING_PICKS)
# TODO write out and read in data from other sources (lines?)

teams_playing_in_week = get_elo_probabilities()
week_dicts = []
for team_prob_tuples in teams_playing_in_week:
    week_dicts.append({t: prob for t, prob in team_prob_tuples})


def is_valid(genome):
    return all(t in week_dicts[i] for i, t in enumerate(genome))


def repeat_until(pred, fn):
    x = fn()
    while not pred(x):
        x = fn()
    return x


def random_genome():
    return repeat_until(is_valid, lambda: list(STARTING_PICKS) + random.sample(set(TEAMS) - set(STARTING_PICKS),
                                                                               GAMES - len(STARTING_PICKS)))


# evaluate fitness (probability of surviving, divide fitness for 1 failure in 1st 3 by 2, 0 o.w.), prune to top 10%
def fitness(genome):
    all_win_prob = sum(week_dicts[i][team] for i, team in enumerate(genome[NUM_STARTING_PICKS:], start=NUM_STARTING_PICKS))
    # see if taking a loss early on more than doubles odds
    if NUM_STARTING_PICKS < 3:
        one_loss_prob = max(all_win_prob - week_dicts[i][genome[i]] + np.log(1 - np.exp(week_dicts[i][genome[i]])) - np.log(2) for i in range(NUM_STARTING_PICKS, 3))
        all_win_prob = max(all_win_prob, one_loss_prob)

    return all_win_prob


def filter_top(population):
    # evaluate fitness, keep top %
    sorted_population = sorted([(g, fitness(g)) for g in population], key=itemgetter(1), reverse=True)
    return sorted_population[:int(np.round(POPULATION * PRUNE))]


def swap_mutate(genome):
    # pick 2 indices, swap them, make sure they are valid
    def swap():
        new_genome = list(genome)
        i, j = random.sample(range(NUM_STARTING_PICKS, len(new_genome)), 2)
        new_genome[i], new_genome[j] = new_genome[j], new_genome[i]
        return new_genome
    return repeat_until(is_valid, swap)


def replace_mutate(genome):
    def replace():
        new_genome = list(genome)
        i = random.randint(NUM_STARTING_PICKS, len(genome) - 1)
        new_genome[i] = repeat_until(lambda t: t not in genome, lambda: random.choice(TEAMS))
        return new_genome

    return repeat_until(is_valid, replace)

# best few recombine (recombine by inserting random segment of season, knock out any repeats, fill in randomly at end)
# then mutate (swap 2 teams, replace a team)
# repeat

# TODO keep multiple populations, recombine them with others

# generate population (choose GAMES out of 32 teams)
if __name__ == "__main__":
    population = [random_genome() for _ in range(POPULATION)]

    for generation in range(GENERATIONS):
        if generation % 5 == 0:
            print generation
        # prune down
        filtered_population = filter_top(population)

        filtered_population = [g for g, _ in filtered_population]
        new_population = []

        # generate mutated copies
        for _ in range(POPULATION / 2):
            g = random.choice(filtered_population)
            new_population.append(swap_mutate(g))

        for _ in range(POPULATION / 2):
            g = random.choice(filtered_population)
            new_population.append(replace_mutate(g))

        new_population.extend(filtered_population)
        population = new_population

    print [(genome, np.exp(logprob)) for genome, logprob in filter_top(population)[:3]]
