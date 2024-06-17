import argparse
import seaborn as sns
from scipy.optimize import linprog
from scipy.stats import kurtosis, skew
import os 
from rcv_distribution import *
from MDS_analysis import *
from consistency import *
from voting_rules import *
import itertools
import random


def get_strict_null_ballots(df):

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



def generate_permutations(items):
    n = len(items)
    all_permutations = []
    for i in range(1, n + 1):
        all_permutations.extend(itertools.permutations(items, i))
    return all_permutations


def group_permutations_by_first_item(permutations):
    grouped = {}
    for perm in permutations:
        first_item = perm[0]
        if first_item not in grouped:
            grouped[first_item] = []
        grouped[first_item].append(perm)
    return grouped

def get_null_ballots(df):
    
    final_ballots = {}
    ballots_in_progress = {}
    ballots_list = []
    candidates = df['candidate'].values
    candidates = sorted(candidates)

    
    all_permutations = generate_permutations(candidates)
    grouped_permutations = group_permutations_by_first_item(all_permutations)

    for candidates 

    for candidate in candidates:
        first_place = df.loc[df['candidate']==candidate, 'first place count'].values[0]
        ballots_in_progress[(candidate,)] = first_place
        ballots_list += [(candidate,)] * first_place
    #print("after adding the first place choices: ")
    #print(ballots_in_progress)

    lengths = {}
    for i in range (len(candidates)):
        sum_i = df['len_' + str(i+1)].sum()
     #   print("sum of length ", i+1, " is ", sum_i)
        if (sum_i > 0):
            lengths[i+1] = sum_i
    
    #print("printing the lengths: ")
    #print(lengths)

    """for i in range(len(candidates)):
        #
        if  i+1 == 1:
            random_voters = random.sample(ballots_list, lengths[i+1])
            #print("sampled bullet voters: ")
            #print(random_voters)
            for b in random_voters:
                if b not in final_ballots:
                    final_ballots[b] = 0
                final_ballots[b] += 1
                ballots_list.remove(b)
            

        elif i+1 in lengths and lengths[i+1] > 0:
           
            len_i = lengths[i+1]
            random_voters = random.sample(ballots_list, len_i)

            for ranking in random_voters:
                new_ranking = ranking
                random_candidates = random.sample(candidates, i)
                for c in random_candidates:
                    new_ranking += (c,)
                if new_ranking not in final_ballots:
                    final_ballots[new_ranking] = 0
                final_ballots[new_ranking] += 1
                ballots_list.remove(ranking)
    """


           
   
    return final_ballots

        


def get_null_gamma(filename):

    directory = "null_elections"
    csv = os.path.join(directory, filename) 
    df = pd.read_csv(csv)  
    ballots = get_null_ballots(df)
    candidates = df['candidate'].values
    normalized_distances = {}
    for c in candidates:
        position = df.loc[df['candidate']==c, 'position']
        normalized_distances[c] = position.values[0]
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
