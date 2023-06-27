import pandas as pd 
import numpy as np 
import operator as op

from typing import Dict, List, Tuple, Union


def anti_plurality(ballots: Dict[Tuple, int], candidates: List[str]) -> str:
    """
    This function implements the Anti-plurality voting method.

    Parameters:
    ballots (dict): A dictionary where each key is a tuple representing a ballot (ordered candidate preferences) and the value is the number of such ballots.
    candidates (list): A list of candidates.

    Returns:
    candidate: The winner of the election.

    """
    # Initialize an empty dictionary to store candidate positions
    candidate_positions = {}

    # Count the total number of votes
    total_votes = sum(ballots.values())

    # Iterate over the ballots
    for ballot, count in ballots.items():
        # Add the count to each candidate's position
        for index, candidate in enumerate(ballot):
            candidate_positions.setdefault((index, candidate), 0)
            candidate_positions[(index, candidate)] += count

    # Reverse iterate over the range of the number of candidates
    for i in range(len(candidates) - 1, -1, -1):
        min_votes = total_votes  # Initialize the minimum votes as the total votes

        # Set the count to 0 for candidates that don't appear in the current position
        for candidate in candidates:
            candidate_positions.setdefault((i, candidate), 0)
            if candidate_positions[(i, candidate)] < min_votes:
                min_votes = candidate_positions[(i, candidate)]

        # Remove candidates with more than the minimum votes from the candidate list
        candidates = [candidate for candidate in candidates if candidate_positions[(i, candidate)] == min_votes]

        # If only one candidate is left, break the loop
        if len(candidates) == 1:
            break

    # Return the remaining candidate as the winner
    return candidates[0]


def black(ballots: Dict[Tuple, int], candidates: List[str]) -> str:
    """
    This function implements the Black voting method.

    Parameters:
    ballots (dict): A dictionary where each key is a tuple representing a ballot (ordered candidate preferences) 
                    and the value is the number of such ballots.
    candidates (list): A list of candidates.

    Returns:
    winner: The winner of the election.

    """
    # Try to find a Condorcet winner
    winner = condorcet(ballots, candidates)

    # If there is no Condorcet winner, fall back to the Borda Count method
    if winner == -1:
        winner = borda(ballots, candidates)

    return winner


def borda(ballots: Dict[Tuple, int], candidates: List[str]) -> str:
    """
    This function implements the Borda Count voting method.

    Parameters:
    ballots (dict): A dictionary where each key is a tuple representing a ballot (ordered candidate preferences) and the value is the number of such ballots.
    candidates (list): A list of candidates.

    Returns:
    winner: The winner of the election.

    """
    # Initialize an empty dictionary to store the scores of each candidate
    candidate_scores = {}

    # Iterate over the ballots
    for ballot, count in ballots.items():
        for rank, candidate in enumerate(reversed(ballot)):
            candidate_scores.setdefault(candidate, 0)
            candidate_scores[candidate] += rank * count

    # Find the candidate with the maximum score
    winner = max(candidate_scores, key=candidate_scores.get)

    # Check for a tie
    for candidate, score in candidate_scores.items():
        if candidate != winner and score == candidate_scores[winner]:
            print('Tie detected between candidates.')
            break

    # Return the winner
    return winner


def bucklin(ballots, candidates):

    def count(ballots, round, scores): #! is count really needed here?
        for b in ballots:
            n = ballots[b]
            ranking = ()
            for c in b:
                ranking += (c,)
            if round - 1 < len(ranking) and round - 1 >= 0:
                if ranking[round - 1] not in scores:
                    scores[ranking[round - 1]] = 0
                scores[ranking[round - 1]] += n
        return scores
    
    def main(ballots, candidates):
        C = len(candidates)
        tie = False 
        voters = 0
        for b in ballots:
            voters += ballots[b]
        round = 1
        scores = {}
        for c in candidates:
            scores[c] = 0
        majority = []
        while len(majority) == 0:
            scores = count(ballots, round, scores)
            for c in scores:
                if scores[c] > voters / 2:
                    majority.append(c)
            round += 1
        winner = max(majority)
        
        return winner
        
    return main(ballots, candidates)


def irv(ballots, candidates): #! are the helper functions needed here?

    number_of_candidates = len(candidates)
    def find_last_candidate(rankings, tie):
        '''Finds and returns the candidate we should eliminate at this point
        '''
        minimum = None
        candidate = None
        for key in rankings:
            if key[1] == 1:
                if minimum is None or rankings[key] < minimum:
                    minimum = rankings[key]
                    candidate = key[0]
        
    

        for key in rankings:
            if key[1] == 1 and rankings[key] == minimum and key[0] != candidate:
                
                tie = True
        
    
        return candidate, tie 

    def reorder(rankings, candidate, stacks):
        for i in range (len(stacks)):
            
            if len(stacks[i]) > 0 and stacks[i][len(stacks[i]) - 1][0] == candidate:
                n = stacks[i][len(stacks[i]) - 1][1]
                stacks[i].pop()
                if(len(stacks[i]) > 0):
                    rankings[(stacks[i][len(stacks[i]) - 1][0], 1)] += n
    
            j = 0
            while j < len(stacks[i]):
                t = stacks[i][j]
                if t[0] == candidate:
                    del stacks[i][j]
                else:
                    j += 1

        for i in range(number_of_candidates):
            del rankings[(candidate, i + 1)]
        return rankings, stacks

            
    def main(ballots, candidates):
        rankings = {}
        tie = False 
        candidates_set = set([])
        for name in candidates:
            for i in range (number_of_candidates):
                    rankings[(name, i + 1)] = 0
            candidates_set.add(name)
        stacks = []
        i = 0
        for b in ballots:
            stacks.append([])
            ranking = ()
            for c in b:
                if c in candidates:
                    ranking += (c,)
            for j in range(len(ranking) - 1, -1, -1):
                if (ranking[j], j + 1) not in rankings:
                    rankings[(ranking[j], j + 1)] = 0
                rankings[(ranking[j], j + 1)] += ballots[b]
                stacks[i].append((ranking[j], ballots[b]))
            i += 1
        while len(candidates_set) > 1:
            candidate_to_be_eliminated, tie = find_last_candidate(rankings, tie)
            candidates_set.remove(candidate_to_be_eliminated)
            rankings, stacks = reorder(rankings, candidate_to_be_eliminated, stacks)
        #print(candidates_set)
        for i in candidates_set:
           return candidates_set.pop()
    return main(ballots, candidates)


def ranked_pairs(ballots: Dict[Tuple, int], candidates: List[str]) -> str:
    """
    This function implements the Ranked Pairs (Tideman method) voting method.

    Parameters:
    ballots (dict): A dictionary where each key is a tuple representing a ballot (ordered candidate preferences) and the value is the number of such ballots.
    candidates (list): A list of candidates.

    Returns:
    winner: The winner of the election.

    Note:
    The function assumes that `condorcet` and `get_pairs` functions are defined and they have the same signature 
    as this function.
    """
    # Try to find a Condorcet winner
    winner = condorcet(ballots, candidates)

    # If there is a Condorcet winner, return the winner
    if winner != -1:
        return winner

    # Calculate pairwise preferences
    pairwise_preferences = get_pairs(ballots, candidates)

    # Order the pairs by the strength of the win
    ordered_pairs = sorted([(pairwise_preferences[pair] - pairwise_preferences[pair[::-1]], pair) 
                            for pair in pairwise_preferences 
                            if pairwise_preferences[pair] >= pairwise_preferences[pair[::-1]]], reverse=True)

    # Initialize the lock dictionary
    lock = {}

    # Lock in pairs from strongest to weakest, skipping any pair that would create a cycle
    for margin, pair in ordered_pairs:
        candidate1, candidate2 = pair
        if candidate1 not in lock:
            lock[candidate1] = set()
        if candidate2 not in lock:
            lock[candidate2] = set()
        if candidate1 not in lock[candidate2]:
            lock[candidate1].add(candidate2)
            for candidate in lock[candidate2]:
                lock[candidate1].add(candidate)

    # Find the candidate who beats all other candidates
    winner = None
    num_candidates = len(candidates)
    for candidate, opponents in lock.items():
        if len(opponents) == num_candidates - 1:
            winner = candidate
            break

    # Check for a tie
    for candidate, opponents in lock.items():
        if candidate != winner and len(opponents) == num_candidates - 1:
            print('Tie detected between candidates.')
            break

    return winner


def copeland(ballots, candidates):
    pairs = {}
    scores = {}
    tie = False
    for c1 in candidates:
        scores[c1] = 0
        for c2 in candidates:
            if (c1 != c2):
                pairs[(c1, c2)] = 0
    for b in ballots:
        n = ballots[b]
        ranking = ()
        for c in b:
            ranking += (c,)

        for i in range (len(ranking)):
            c1 = ranking[i]
            for j in range (i + 1, len(ranking)):
                c2 = ranking[j]
                if (c1, c2) not in pairs:
                    pairs[(c1, c2)] = 0
                pairs[(c1, c2)] += n
    for c1 in candidates:
        for c2 in candidates:
            if c1 != c2:
                if pairs[(c1, c2)] > pairs[(c2, c1)]:
                    scores[c1] += 1
                elif pairs[(c2, c1)] > pairs[(c1, c2)]:
                    scores[c2] += 1
                else:
                    scores[c1] += 0.5
                    scores[c2] += 0.5
    winner = max(scores, key=scores.get)
    for c in scores:
        if c != winner and scores[c] == scores[winner]:
            tie = True
    
    return winner


def mini_max(ballots, candidates):
    pairs = get_pairs(ballots, candidates)
    tie = False
    scores = {}
    for c1 in candidates:
        scores[c1] = 0
        for c2 in candidates:
            if (c1 != c2):
                if pairs[(c2, c1)] > scores[c1]:
                    scores[c1] = pairs[(c2, c1)]
    #winner 
    winner = min(scores, key=scores.get)
    for c in scores:
        if c != winner and scores[c] == scores[winner]:
            tie = True 
    return winner


def condorcet(ballots, candidates): 
    pairs = get_pairs(ballots, candidates)
    flag = True
    for c1 in candidates:
        flag = True
        for c2 in candidates:
            if (c1 != c2):
                if (pairs[(c2, c1)] > pairs[(c1, c2)]):
                    flag = False
        if (flag):
            return c1
    return -1


def get_pairs(ballots: Dict[Tuple, int], candidates: List[str]) -> Dict[Tuple[str, str], int]:
    """
    This function calculates pairwise preferences between all pairs of candidates based on the given ballots.

    Parameters:
    ballots (dict): A dictionary where each key is a tuple representing a ballot (ordered candidate preferences) and the value is the number of such ballots.
    candidates (list): A list of candidates.

    Returns:
    pairs: A dictionary where each key is a tuple representing a pair of candidates and the value is the number of 
           times the first candidate is preferred over the second one in the ballots.
    """
    # Initialize an empty dictionary to store the pairs
    pairwise_preferences = {}

    # Iterate over all pairs of candidates
    for i in range(len(candidates)):
        for j in range(len(candidates)):
            if i != j:
                pair = (candidates[i], candidates[j])
                pairwise_preferences[pair] = 0

    # Iterate over the ballots
    for ballot, count in ballots.items():
        # For each ballot, check each candidate against every other candidate
        for candidate1 in candidates:
            if candidate1 in ballot:
                for candidate2 in candidates:
                    if candidate1 != candidate2 and ((candidate2 not in ballot) or ballot.index(candidate1) > ballot.index(candidate2)):
                        pair = (candidate1, candidate2)
                        pairwise_preferences[pair] += count

    return pairwise_preferences


def read_file(file):
    data = pd.read_csv(str(file))
    candidates = []
    
    #number of voters
    n = len(data)

    ballots = {}
    for i in range(1,n):
        ranking = ()
        j = 1
        flag = True
        while flag:
            try:

                c =data.at[i, "rank"+str(j)]
                if c != "skipped" and c != "Write-in"  and c != "Write-Ins" and c != "overvote" and c != "undervote":
                    ranking += (c,)
                    if c not in candidates:
                        candidates.append(c)
                j += 1
            except:
                flag = False
       
        if ranking not in ballots:
            ballots[ranking] = 0
        ballots[ranking] += 1
    return ballots, candidates


def top_n(ballots, candidates, n):

    first_place = {}
    for b in ballots:
        if (len(b) > 0):
            candidate = b[0]
            if candidate not in first_place:
                first_place[candidate] = 0
            first_place[candidate] += ballots[b]
    first_place = dict( sorted(first_place.items(), key=op.itemgetter(1),reverse=True))

    #getting top n
    top_candidates = []
    for i, c in enumerate(first_place.keys()):
        if i == n:
            break
        top_candidates.append(c)

    return top_candidates


def main():

    file = input("Enter Files Name: ")
    ballots, candidates = read_file(file)
    #will add ant_plurality later, its not working correctly now  
    methods = ["irv", "condorcet", "copeland", "black", "bucklin", "borda", "mini_max", "ranked_pairs"]
    print("Original candidates: ")
    for m in methods:
        print(m, ": " , eval(m)(ballots, candidates))
    print()
    candidates_t = []
    for c in candidates:
        candidates_t.append(c)
    for i in range(2, len(candidates)):
        candidates_t = top_n(ballots, candidates, i)
        print("runnig for top_", i, " candidates: ", candidates_t)
        for m in methods:
            print(m, ": " , eval(m)(ballots, candidates_t))
        print()


main()