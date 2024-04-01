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
    print(normalized_distances)
    consistent_ballots, gamma = get_interval_consistent_ballots(ballots, normalized_distances)
    return consistent_ballots, gamma
