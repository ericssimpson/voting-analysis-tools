import pandas as pd 
import numpy as np 

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


def black(ballots, candidates):

    def condorcet(pairs, candidates):
        flag = True
        for c1 in candidates:
            flag = True
            for c2 in candidates:
                if (c1 != c2):
                    if (pairs[(c2, c1)] >= pairs[(c1, c2)]):
                        flag = False
            if (flag):
                return c1
        return -1

    def get_pairs(ballots, candidates):
        pairs = {}
        C = len(candidates)
        for i in range (C):
            for j in range(C):
                if (i != j):
                    t = (candidates[i], candidates[j])
                    pairs[t] = 0
        for b in ballots:
            n = ballots[b]
            ranking = ()
            for c in b:
                ranking += (c,)

            for i in range (len(ranking)):
                c1 = ranking[i]
                for j in range (i + 1, len(ranking)):
                    c2 = ranking[j]
                    t = (c1, c2)
                    if t not in pairs:
                        pairs[t] = 0
                    pairs[t] += n
        #print(pairs)
        return pairs 

    def main(ballots, candidates):
        pairs = get_pairs(ballots, candidates)
        return_val = condorcet(pairs, candidates)
        if return_val == -1:
            return borda(ballots, candidates)
        return return_val

    return main(ballots, candidates)


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

    def count(ballots, round, scores):
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


def irv(ballots, candidates):

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


def ranked_pairs(ballots, candidates):
    con = condorcet(ballots, candidates)
    if con != -1:
        return con
    pairs = {}
    tie = False 
    C = len(candidates)
    for b in ballots:
        n = ballots[b]
        ranking = ()
        for c in b:
            ranking += (c,)

        for i in range (len(ranking)):
            c1 = ranking[i]
            for j in range (i + 1, len(ranking)):
                c2 = ranking[j]
                t = (c1, c2)
                if t not in pairs:
                    pairs[t] = 0
                pairs[t] += n
    sorted_majorities = []
    for t in pairs:
        c1 = t[0]
        c2 = t[1]
        if pairs[t] >= pairs[(c2, c1)] and (pairs[t] - pairs[(c2, c1)], t) not in sorted_majorities:
            if pairs[t] == pairs[(c2, c1)]:
                tie = True
            sorted_majorities.append((pairs[t] - pairs[(c2, c1)], t))
    sorted_majorities.sort()
    sorted_majorities.reverse()
    lock = {}
    for p in sorted_majorities:
        c1 = p[1][0]
        c2 = p[1][1]
        if c1 not in lock:
            lock[c1] = set()
        if c2 not in lock:
            lock [c2] = set()
        if c1 not in lock[c2]:
            lock[c1].add(c2)
            for c in lock[c2]:
                lock[c1].add(c)
    #winner 
    winner = None  
    for c in lock:
        if len(lock[c]) == C - 1:
            winner = c
            break
    for c in lock:
        if c != winner and len(lock[c]) == C - 1:
            tie = True
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
    pairs = {}
    tie = False
    for i in range (len(candidates)):
        for j in range(len(candidates)):
            if (i != j):
                t = (candidates[i], candidates[j])
                pairs[t] = 0
    
    for b in ballots:
        n = ballots[b]
        ranking = ()
        for c in b:
            ranking += (c,)

        for i in range (len(ranking)):
            c1 = ranking[i]
            for j in range (i + 1, len(ranking)):
                c2 = ranking[j]
                t = (c1, c2)
                if t not in pairs:
                    pairs[t] = 0
                pairs[t] += n
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


def get_pairs(ballots: Dict[Tuple, int], candidates: List[str]) -> Dict[Tuple[str, str], int]:
    """
    This function calculates pairwise preferences of candidates based on the ballots.

    Parameters:
    ballots (dict): A dictionary where each key is a tuple representing a ballot (ordered candidate preferences) and the value is the number of such ballots.
    candidates (list): A list of candidates.

    Returns:
    pairs (dict): A dictionary where each key is a pair of candidates (candidate1, candidate2) and the value is the number of times candidate1 is preferred over candidate2.

    """
    # Initialize an empty dictionary to store pairwise preferences
    pairwise_preferences = {}

    # Iterate over the list of candidates and create all possible pairs
    for candidate1 in candidates:
        for candidate2 in candidates:
            if candidate1 != candidate2:
                pairwise_preferences[(candidate1, candidate2)] = 0

    # Iterate over the ballots
    for ballot, count in ballots.items():
        # For each candidate in the ballot
        for candidate1 in candidates:
            # If candidate1 is present in the ballot
            if candidate1 in ballot:
                # For each other candidate
                for candidate2 in candidates:
                    # If candidate2 is not present in the ballot or candidate1 is ranked higher than candidate2
                    if candidate1 != candidate2 and ((candidate2 not in ballot) or ballot.index(candidate1) < ballot.index(candidate2)):
                        # Increment the pairwise preference of candidate1 over candidate2
                        pairwise_preferences[(candidate1, candidate2)] += count

    return pairwise_preferences


def condorcet(ballots: Dict[Tuple, int], candidates: List[str]) -> Union[str, int]:
    """
    This function implements the Condorcet voting method.

    Parameters:
    ballots (dict): A dictionary where each key is a tuple representing a ballot (ordered candidate preferences) and the value is the number of such ballots.
    candidates (list): A list of candidates.

    Returns:
    winner (str): The winner of the election if a Condorcet winner exists.
    -1 (int): If no Condorcet winner exists.

    """
    # Calculate pairwise preferences of candidates based on the ballots
    pairwise_preferences = get_pairs(ballots, candidates)

    # Iterate over the list of candidates
    for candidate1 in candidates:
        is_condorcet_winner = True  # Assume the candidate is a Condorcet winner

        # Compare the candidate with every other candidate
        for candidate2 in candidates:
            if candidate1 != candidate2 and pairwise_preferences[(candidate2, candidate1)] > pairwise_preferences[(candidate1, candidate2)]:
                # If any other candidate is preferred over the current candidate, it cannot be a Condorcet winner
                is_condorcet_winner = False
                break

        # If the candidate is a Condorcet winner, return it as the winner
        if is_condorcet_winner:
            return candidate1

    # If no Condorcet winner exists, return -1
    return -1


def read_file(file, candidates):
    data = pd.read_csv(str(file))
    C = len(candidates) 
    
    #number of voters
    n = len(data)

    ballots = {}
    for i in range(1,n):
        ranking = ()
        for j in range(1,C+1):
            c =data.at[i, "rank"+str(j)]
            if c != "skipped" and c != "Write-in"  and c != "Write-Ins" and c != "overvote" and c != "undervote":
                ranking += (c,)
       
        if ranking not in ballots:
            ballots[ranking] = 0
        ballots[ranking] += 1
    return ballots


def main():

    file = input("Enter Files Name: ")
    candidates = input("Canddiates Names: ").split("/")
    ballots = read_file(file, candidates)

    methods = input("Methods: ").split()
    for m in methods:
        print(m, ": " , eval(m)(ballots, candidates))


main()