class election_metric:

    def __init__(self, ballots, candidates):
        self.candidates = candidates
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
