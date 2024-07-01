class voting_rules:

    def __init__(self, ballots, candidates):
        self.candidates = candidates 
        self.ballots = ballots
        
    #helper functions 

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
        for c1 in candidates:
            for c2 in candidates:
                if c1 != c2:
                    pairwise_preferences[(c1, c2)] = 0

        for b in ballots:
            n = ballots[b]
            for i in range(len(b)):
                c1 = b[i]
                for c2 in candidates:
                    if c2 not in b:
                        pairwise_preferences[(c1, c2)] += n
                    elif c2 != c1:
                        j = b.index(c2)
                        if j > i:
                            pairwise_preferences[(c1, c2)] += n

        return pairwise_preferences
    
    
    def get_first_place(self):
        candidates = self.candidates
        ballots = self.ballots
        first_place = {}
        for b in ballots:
            if len(b) > 0:
                candidate = b[0]
                if candidate not in first_place:
                    first_place[candidate] = 0
                first_place[candidate] += ballots[b]
        return first_place

    
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
        winner = self.condorcet()

        # If there is a Condorcet winner, return the winner
        if winner != -1:
            return winner

        # Calculate pairwise preferences
        pairwise_preferences = self.get_pairs()

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
        pairs = self.get_pairs()
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
                    if (pairs[(c2, c1)] >= pairs[(c1, c2)]):
                        flag = False
            if (flag):
                return c1
        return -1
    
    
    
    def irv(self):
        
        if len(self.candidates) == 0:
            return None 
        
        if len(self.candidates) == 1:
            return self.candidates[0]
        
        candidates_t = []
        for i in range(len(self.candidates)):
            candidates_t.append(self.candidates[i])
        ballots_t = {}
        for b in self.ballots:
            ballots_t[b] = self.ballots[b]
        
        round = 1
        summary = {}
        while len(candidates_t) > 1:
            new_election = voting_rules(ballots_t, candidates_t)
            if new_election.majority() != -1:
                return new_election.majority()
            else:
                first_place = new_election.get_first_place()
                summary["round_"+str(round)] = first_place
                loser = min(first_place, key=first_place.get)
                new_ballots = {}
                for b in ballots_t:
                    new_ranking = ()
                    for c in b:
                        if c != loser:
                            new_ranking += (c,)
                    if new_ranking not in new_ballots:
                        new_ballots[new_ranking] = 0
                    new_ballots[new_ranking] += ballots_t[b]
                ballots_t = new_ballots
                candidates_t.remove(loser)
                round += 1
        return candidates_t[0], summary
        

    def plurality(self):
        """
        returns the plurality winner
        """
        first_place = self.get_first_place()
        if len(first_place) == 0:
            return None 
        return max(first_place, key=first_place.get)
    
    
    def majority(self):
        """
        returns the candidate with the majority of the first place preferences if it exists, otherwise returns -1
        """
        candidates = self.candidates
        ballots = self.ballots

        first_place = self.get_first_place()
        V = 0
        for b in ballots:
            V += ballots[b]
        plurality = max(first_place, key=first_place.get)
        if first_place[plurality] > V/2:
            return plurality
        return -1 


    def approval(self):
        candidates = self.candidates
        ballots = self.ballots
        approved = {}
        if len(candidates) == 0:
            return None 
        if len(candidates) == 1:
            return candidates[0]
        if len(ballots) == 0:
            return None 
        
        for b in ballots:
            if len(b) > 0:
                l = len(b)
                n = ballots[b]
                for i in range(len(b)//2 + 1):
                    c = b[i]
                    if c in candidates:
                        if c not in approved:
                            approved[c] = 0
                        approved[c] += n

        if len(approved) == 0:
            return None 
                
        return max(approved, key=approved.get)
    
    def approval2(self):
            candidates = self.candidates
            ballots = self.ballots
            approved = {}
            for b in ballots:
                if len(b) > 0:
                    n = ballots[b]
                    for i in range(len(b)):
                        c = b[i]
                        if c in candidates:
                            if c not in approved:
                                approved[c] = 0
                            approved[c] += n
            return max(approved, key=approved.get)








