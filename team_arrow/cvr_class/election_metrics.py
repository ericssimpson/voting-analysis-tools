import pandas as pd 
import numpy as np 
from voting_rules import voting_rules
import os 
import parser
import matplotlib.pyplot as plt
import itertools 


class election_metric(voting_rules):

    def __init__(self, ballots, candidates):
        self.candidates = candidates
        self.ballots = ballots

    def condorcet_n(self, n):
        candidates = self.candidates
        ballots = self.ballots
        if n == -1:
            return None
        if n == 1:
            return self.condorcet()
        i = 1
        can_t = []
        for c in candidates:
            can_t.append(c)
        ballots_t = {}
        for b in ballots:
            ballots_t[b] = ballots[b]
        new_election = voting_rules(ballots_t, can_t)
        while i != n and len(can_t) > 0:
            condorcet = new_election.condorcet()
            if condorcet == -1:
                return None 
            can_t.remove(condorcet)
            for b in ballots_t.copy():
                if condorcet in b:
                    del ballots_t[b]
            new_election = voting_rules(ballots_t, can_t)
            i += 1
            if i == n:
                return new_election.condorcet()
        
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
def main():
    directory = os.fsencode("team_arrow/cvr_class/dataverse_files")
    total = 0
    nc = 0
    i = 0
    d = {}
    #df = pd.DataFrame()
    rules = ["irv", "plurality", "majority", "condorcet", "approval", "borda"]
    criterion = ["Condorcet", "Condorcet_2", "NA"]
    df = pd.DataFrame(index=rules, columns=criterion)
    for col in df.columns:
        df[col].values[:] = 0
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        total += 1
        ballots, candidates = parser.parser("team_arrow/cvr_class/dataverse_files"+"/"+filename)
        e = election_metric(ballots, candidates)
        n = len(candidates)
        for r in rules:
            func = getattr(e, r)
            if func() == -1:
                df.loc[[r],["NA"]] += 1
            else:
                if func() == e.condorcet():
                    df.loc[[r],["Condorcet"]] += 1
                if func() == e.condorcet_n(2):
                    df.loc[[r],["Condorcet_2"]] += 1
        if total % 50 == 0:
            print(df)
    print(df)
            
#main()      




'''def test():
    ballots, candidates = parser.parser("team_arrow/cvr_class/dataverse_files"+"/"+"NewYorkCity_06222021_DEMMayorCitywide.csv")
    print(candidates)
     print(len(ballots))
    s = np.array(['Eric L. Adams','Maya D. Wiley', 'Kathryn A. Garcia', 'Andrew Yang', 'Scott M. Stringer','Raymond J. McGuire'
                  ,'Dianne Morales', 'Art Chang', 'Shaun Donovan', 'Isaac Wright Jr.', 'Aaron S. Foldenauer', 'Joycelyn Taylor', 'Paperboy Love Prince'])
    
    t = 0
    bad_ballots = 0
    for b  in ballots:
        t += ballots[b]
        flag = False
        for i in range(len(b)):
            c1 = b[i]
            for j in range(len(b)):
                c2 = b[j]
                if c1 != c2:
                    d1 = abs(i - j)
                    s1 = abs(np.where(s == c1)[0] - np.where(s == c2)[0])
                    for k in range(len(candidates)):
                        c3 = candidates[k]
                        if c3 != c1 and c3 != c2:
                            if c3 in b:
                                d2 = abs(i - b.index(c3))
                            else:
                                d2 = abs(len(b)-i-1)
                            s2 = abs(np.where(s == c1)[0] - np.where(s == c3)[0])
                            if ((d1 < d2) and (s1 < s2)) or ((d1 > d2) and (s1 > s2)):
                                continue
                            else:
                                flag = True 
        if flag:
            bad_ballots += ballots[b]

    e = election_metric(ballots, candidates)
    print(e.irv())
    
    
test()


'''
