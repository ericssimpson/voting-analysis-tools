import parser 
import itertools
import numpy as np
def dim():

    ballots, candidates = parser.parser("team_arrow/cvr_class/dataverse_files/Alaska_11082022_HouseDistrict28.csv")
    perms = list(itertools.permutations(candidates))
    #most consistant permutation
    mcp = None
    c_mcp = 0
    for p in perms:
        c = 0
        for b in ballots:
            if (is_consistant(b, p)):
                c += ballots[b]
        if mcp is None or c > c_mcp:
            c_mcp = c
            mcp = p
    print("MCP: ", mcp)
    print ("Consistanty: ", c_mcp, "%: ", (100*(c_mcp/sum(ballots.values()))))


def is_consistant(ballot, perm):
    p = np.array(perm)
    for i in range(len(ballot)):
        c1 = ballot[i]
        for j in  range (len(ballot)):
            c2 = ballot[j]
            if i != j:
                d1 = abs(i - j)
                s1 = abs(np.where(p == c1)[0] - np.where(p == c2))
                for k in range(len(ballot)):
                    if i != k and k != j:
                        c3 = ballot[k]
                        d2 = abs(i - k)
                        s2 = abs((np.where(p == c1)[0] - np.where(p == c3)[0]))
                        if (d1 <= d2 and s1 <= s2) or (d2 <= d1 and s2 <= s1):
                            pass 
                        else:
                            return False 
    return True 


