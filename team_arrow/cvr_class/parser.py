import pandas as pd 
import numpy as np

def read_file(file):
    data = pd.read_csv(str(file))
    candidates = []
    
    #number of voters
    n = len(data)

    ballots = {}
    for i in range(1, n):
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
