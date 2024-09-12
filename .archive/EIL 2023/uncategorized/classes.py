import operator as op
import pandas as pd 
import numpy as np 

from typing import Dict, List, Tuple, Union

class Eelection:

    def __init__(self, ballots, candidates):
        self.candidates =  candidates
        self.ballots = ballots
    
    
    def irv_condorcet(self):
        if (self.condorcet() != self.irv()):
            return False
        return True
    #ballots that never appeared 
    #midean ballots to be added here 

    def most_common_ballot(self):
        ballots = self.ballots
        return max(ballots, key=ballots.get)
    
    #distance
    def mcb_distance(self, m):
        """
        calculates the distance of the elected candidate using "m" as RCV method 
        with the most common ballot.
        returns -1 if that candidate doesn't exist in the most common ballot.
        """

        mcb = self.most_common_ballot()
        elected_candidate = eval(m(self))
        p = -1
        for i in range(len(mcb)):
            if mcb[i] == elected_candidate:
                p = i
        return p 
    
    #distance to the median ballot

    #getters
    def get_candidates(self):
        return self.candidates
    

    def get_number_of_candidates(self):
        return len(self.candidates)
    

    





    #RCV variations
    def black(self):
        candidates = self.candidates
        ballots = self.ballots
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
        winner = self.condorcet()

        # If there is no Condorcet winner, fall back to the Borda Count method
        if winner == -1:
            winner = self.borda()

        return winner


    def borda(self):
        candidates = self.candidates
        ballots = self.ballots
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
                #print('Tie detected between candidates.')
                break

        # Return the winner
        return winner


    def bucklin(self):
        candidates = self.candidates
        ballots = self.ballots
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


    def irv(self): #! are the helper functions needed here?
        candidates = self.candidates
        ballots = self.ballots
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


    def ranked_pairs(self):
        candidates = self.candidates
        ballots = self.ballots
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


    def copeland(self):
        candidates = self.candidates
        ballots = self.ballots
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


    def mini_max(self):
        candidates = self.candidates
        ballots = self.ballots
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


    def condorcet(self):
        candidates = self.candidates
        ballots = self.ballots 
        pairs = self.get_pairs()
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
    def get_pairs(self):
        candidates = self.candidates
        ballots = self.ballots
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
    
    def majority(self):
        """
        returns the candidate with the majority of the first place preferences if it exists, otherwise returns -1
        """
        candidates = self.candidates
        ballots = self.ballots

        first_place = {}
        V = 0
        for b in ballots:
            V += ballots[b]
            if len(b) > 0:
                candidate = b[0]
                if candidate not in first_place:
                    first_place[candidate] = 0
                first_place[candidate] += ballots[b]
        for candidate in first_place:
            if first_place[candidate] >= V//2:
                return candidate
        return -1 

    
    def plurality(self):
        """
        returns the plurality winner
        """
        candidates = self.candidates
        ballots = self.ballots

        first_place = {}
        for b in ballots:
            if len(b) > 0:
                candidate = b[0]
                if candidate not in first_place:
                    first_place[candidate] = 0
                first_place[candidate] += ballots[b]
        return max(first_place, key=first_place.get)

    def approval(self):
        candidates = self.candidates
        ballots = self.ballots
        approved = {}
        for b in ballots:
            n = ballots[b]
            for c in b:
                if c in candidates:
                    if c not in approved:
                        approved[c] = 0
                    approved[c] += n
        return max(approved, key=approved.get)




