import parser 
import itertools
import numpy as np
import os 
import matplotlib.pyplot as plt
def dim():

    directory = "team_arrow/cvr_class/dataverse_files"
    d = {}
    for filename in os.listdir(directory):

        ballots, candidates = parser.parser(os.path.join(directory, filename))
        x = len(candidates)
        if x <=6:
            if x not in d:
                d[x] = []
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
            d[x].append(c_mcp/sum(ballots.values()))
            '''print(filename)
        print("MCP: ", mcp)
        print ("Consistanty: ", c_mcp, "%: ", (100*(c_mcp/sum(ballots.values()))))
        print()'''
    #print(d)
    
    plt.figure(figsize=(10, 6))
    i = 0
    for x, y_values in d.items():
        for y in y_values:
            plt.scatter(x, y)
    plt.show()

def is_consistant(ballot, perm):

    if len(ballot) == 0:
        return True
    c = ballot[0]
    index = 0
    for i in range(len(perm)):
        if (c == perm[i]):
            index = i
            break
    def dfs(i, j, p):
        '''
        i: index in the ballot
        j: index in the permutation
        p = parent 
        '''
        if j < 0 or j > len(perm):
            return False
        
        print(i, " ", j, " ", p)
        if (i == len(ballot) - 1):
            return True
        
        if (i == 0):
            if (j + 1 >= len(perm)):
                if ballot[i + 1] != perm[j - 1]:
                    return False 
            if j - 1 < 0:
                if ballot[i + 1] != perm[j + 1]:
                    return False
            if ballot[i + 1] != perm[j - 1] and ballot[i + 1] != perm[j + 1]:
                return False

        if p != j + 1 and j + 1 < len(perm) and ballot[i + 1] == perm[j + 1]:
            return dfs(i + 1, j + 1, j)
        elif p != j - 1 and ballot[i + 1] == perm[j - 1]:
            return dfs(i + 1, j - 1, j)
        else:
            if p != j:
                return dfs(i, p, p)
            else:
                return False
    return dfs(0, index, -1)

def is_consistant2(ballot, perm):
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

#print(is_consistant(('d', 'b', 'a'), ['a','b','c', 'd']))

dim()
