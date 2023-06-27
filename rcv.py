import pandas as pd 
import numpy as np 
import operator as op

def anti_plurality(ballots, candidates):
    can = []
    for c in candidates:
        can.append(c)
    positions = {}
    tie = False 
    C = len(can)
    V = 0
    for b in ballots:
        n = ballots[b]
        V += n
        ranking = ()
        for c in b:
            ranking += (c,)
        for i in range(len(ranking) - 1, -1, -1):
            if (i,ranking[i]) not in positions:
                positions[(i, ranking[i])] = 1
            else:
                positions[(i, ranking[i])] += 1
    for i in range(C - 1, -1, -1):
        mini = V 
        for c in can:
            if (i, c) not in positions:
                positions[(i, c)] = 0
            if positions[(i, c)] < mini:
                mini = positions[(i , c)]
        for c in can:
            if positions[(i, c)] != mini:
                can.remove(c)
        if len(can) == 1:
            break
    return can[0]

def black(ballots, candidates):
    return_val = condorcet(ballots, candidates)
    if return_val == -1:
        return borda(ballots, candidates)
    return return_val

def borda(ballots, candidates):
    scores = {}
    tie = False
    for b in ballots:
        n = ballots[b]
        ranking = ()
        for c in b:
            ranking += (c,)
        score = len(candidates) - 1
        for c in ranking:
            if c not in scores:
                scores[c] = 0
            scores[c] += score * n
            score -= 1
    
    winner = max(scores, key=scores.get)
    for c in scores:
        if c != winner and scores[c] == scores[winner]:
            tie = True
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

def ranked_pairs(ballots, candidates):
    con = condorcet(ballots, candidates)
    if con != -1:
        return con
    sorted_majorities = []
    pairs = get_pairs(ballots, candidates)
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

        for c1 in candidates:
            if c1 in b:
                for c2 in candidates:
                    if c1 != c2 and ((c2 not in b) or b.index(c1) > b.index(c2)):
                        t = (c1, c2)
                        if t not in pairs:
                            pairs[t] = n
                        else:
                            pairs[t] += n
    return pairs

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

