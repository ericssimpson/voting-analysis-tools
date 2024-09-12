import argparse
import seaborn as sns
from scipy.optimize import linprog
from scipy.stats import kurtosis, skew
import os 
from rcv_distribution import *
from MDS_analysis import *
from consistency import *
from voting_rules import *
from itertools import permutations
from collections import defaultdict
from collections import Counter
import random


# capturing lengths specific to each candidate
def get_mild_null_ballots(df):

    ballots = {}
    candidates = df['candidate'].values

    for c in candidates:
        ballots[(c,)] = df.loc[df['candidate']==c, 'len_1'].values[0]
        b = (c,)
    
        for i in range(2, len(candidates) + 1):
            if df.loc[df['candidate']==c, 'len_'+str(i)].values[0] != -1:
                count_i = df.loc[df['candidate']==c, 'len_'+str(i)].values[0]
                
                while(len(b) < i):
                    random_candidate = random.choice(candidates)
                    if random_candidate not in b:
                        b += (random_candidate,)
    
                ballots[b] = count_i
    return ballots


#cepturing the lengths
def get_slow_null_ballots(df):
    
    final_ballots = {}
    ballots_set = Counter()
    candidates = df['candidate'].values
    candidates = sorted(candidates)


    for candidate in candidates:
        first_place = df.loc[df['candidate']==candidate, 'first place count'].values[0]
        ballots_set[(candidate,)] += first_place


    lengths = {}
    for i in range (len(candidates)):
        sum_i = df['len_' + str(i+1)].sum()
        if (sum_i > 0):
            lengths[i+1] = sum_i

    for i in range(len(candidates)):
        if  i+1 == 1:
            ballots_list = list(ballots_set.elements())
            random_voters = random.choices(ballots_list, k=lengths[i+1])
            for b in random_voters:
                if b not in final_ballots:
                    final_ballots[b] = 0
                final_ballots[b] += 1
                ballots_set[b] -= 1
            

        elif i+1 in lengths and lengths[i+1] > 0:
            len_i = lengths[i+1]
            ballots_list = list(ballots_set.elements())
            random_voters = random.choices(ballots_list, k=lengths[i+1])

            for ranking in random_voters:
                new_ranking = ranking
                random_candidates = random.sample(candidates, i)
                for c in random_candidates:
                    new_ranking += (c,)
                if new_ranking not in final_ballots:
                    final_ballots[new_ranking] = 0
                final_ballots[new_ranking] += 1
                ballots_set[ranking] -= 1
           
   
    return final_ballots



def generate_and_group_permutations(items, choices):
    n = len(items)
    grouped_permutations = defaultdict(list)
    
    for i in range(1, choices + 1):
        for perm in permutations(items, i):
            grouped_permutations[perm[0]].append(perm)
    
    return grouped_permutations


def get_extreme_null_ballots(df, choices):

    candidates = df['candidate'].values
    candidates = sorted(candidates)
    ballots = {}
    #get choices from elections.csv
    grouped_permutations = generate_and_group_permutations(candidates, choices)
    sum_voters = df['first place count'].sum()
    for candidate in candidates:
        first_place_freq = df.loc[df['candidate']==candidate, 'first place freq'].values[0]
        first_place = int(round(first_place_freq, 3) * 1000)
        random_ballots = random.choices(grouped_permutations[candidate], k=first_place)
        for b in random_ballots:
            if b not in ballots:
                ballots[b] = 0
            ballots[b] += 1
    return ballots


def get_null_gamma(filename, randomness):

    directory = "null_elections"
    csv = os.path.join(directory, filename) 
    df = pd.read_csv(csv)  
    candidates = df['candidate'].values
    election = pd.read_csv("election_table.csv")
    choices = min(len(candidates), round(election.loc[election['filename']==filename, 'choices'].values[0]))
    
    #print(choices)
    if randomness == 'extreme':
        ballots = get_extreme_null_ballots(df, choices)
    elif randomness == 'slow':
        ballots = get_slow_null_ballots(df)
    else:
        ballots = get_mild_null_ballots(df)

    normalized_distances_original = {}
    for c in candidates:
        position = df.loc[df['candidate']==c, 'position']
        normalized_distances_original[c] = position.values[0]
    #print(filename, "  original normalized distances: ", normalized_distances_original)

    test = perform_rcv_analysis(ballots, candidates, n_init=100, max_itr=1000, n_runs=1000, metric=False)
    mds_1d_coordinates, mds_2d_coordinates, most_common_order, order_frequencies, candidate_names = test

    # Print the normalized distances between candidates and plot the MDS analysis
    normalized_distances = get_distances_normalized(most_common_order, mds_1d_coordinates, candidate_names)

    #print("new distances: ", normalized_distances_original)
    consistent_ballots, gamma = get_permissive_gamma(ballots, normalized_distances)
    return consistent_ballots, gamma


def main():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('input', metavar='INPUT', type=str, help='Input string')
    
    args = parser.parse_args()
    user_input = args.input

    null_gammas = pd.read_csv("null_gammas.csv")
    ans = []
    sum = 0
    for i in range(1, 1001):
        sum += get_null_gamma(user_input)[1]
        if i == 10:
            ans.append(sum/10)
            null_gammas.loc[null_gammas["filename"] == user_input, "null_gamma_10"] = sum/10
        if i == 100:
            ans.append(sum/100)
            null_gammas.loc[null_gammas["filename"] == user_input, "null_gamma_100"] = sum/100
    ans.append(sum/1000)
    null_gammas.loc[null_gammas["filename"] == user_input, "null_gamma_1000"] = sum/1000
    
    
    null_gammas.to_csv("null_gammas.csv", index=False)  # Ensure index is not written to the CSV


    
    

if __name__ == "__main__":
    main()
