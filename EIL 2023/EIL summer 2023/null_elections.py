import argparse
import seaborn as sns
from scipy.optimize import linprog
from scipy.stats import kurtosis, skew
import os 
from rcv_distribution import *
from rcv_dimensionality import *
from voting_rules import *
from interval_consistency import *
import random


def get_null_ballots(df):

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
    consistent_ballots, gamma = get_interval_consistent_ballots(ballots, normalized_distances)
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
