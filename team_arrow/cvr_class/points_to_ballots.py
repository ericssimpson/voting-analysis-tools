def ballot_generator(points: dict, rcv_dimensionality: dict) -> dict[tuple, int]:
    '''
    points: positions of differnet voters on a single axis 
    rcv_dimensionality: the output of rcv_dimensionality.perform_rcv_and_normalize
    
    '''
    ballots = {}

    for x in points:
        l = {}
        flag = False 
        for candidate in rcv_dimensionality:
            if flag:
                continue 
            position = rcv_dimensionality[candidate]
            if position == x:
                flag = True 
                if (candidate) not in ballots:
                    ballots[(candidate)] = 0
                ballots[(candidate)] += points[x]
                continue
            else:
                l[candidate] = abs(rcv_dimensionality[candidate] - x)
        if flag is False:
            ranking = ()
            for t in sorted(l.items(), key=lambda item: item[1]):
                candidate = t[0]
                ranking += (candidate,)
            
            if ranking not in ballots:
                ballots[ranking] = 0
            ballots[ranking] += points[x] 
    
    return ballots 
