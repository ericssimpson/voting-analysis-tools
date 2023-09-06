import seaborn as sns

from scipy.stats import kurtosis, skew
import scipy.io
from rcv_distribution import *
from rcv_dimensionality import *
from voting_rules import *


def frequency(ballots, candidates):
    result_freq = {}
    result_first = {}

    frequency = {}
    first = {}
    empty = 0
    for c in candidates:
        frequency[c] = 0
        first[c] = 0
    
    for b in ballots:
        if len(b) > 0:
            first[b[0]] += ballots[b]
        else:
            empty += ballots[b]
        for c in b:
            frequency[c] += ballots[b]
    
    total = sum(ballots.values())
    total -= empty 
    for c in frequency:
        result_freq[c] = (frequency[c]/total) * 100
    for c in first:
        result_first[c] = (first[c]/total) * 100
    
    list_freq = sorted(result_freq.items(), key=lambda x:x[1])
    print(list_freq)
    print()
    freq = []
    for t in list_freq:
        freq.append(t[0])
        
    return list_freq


def pefrom_MDS(file, ignore):

    ballots, candidates = parse_election_data(file)
    list_freq = frequency(ballots, candidates)
    ignore_values = ['(WRITE-IN)', 'WRITE-IN', 'writein', 'Write-In', 'Write-in', 'skipped', 'overvote', 'Undeclared', 'undervote', 'Write in']
    if ignore:
        for (candidate, freq) in list_freq:
            if freq < 4:
                print("ignored: ", candidate, ": ", freq)
                ignore_values.append(candidate)

        ballots, candidates = parse_election_data(file, ignore_values=ignore_values)

    print("running MDS: ")
    test = perform_rcv_analysis(file, n_runs=1000)
    mds_1d_coordinates, mds_2d_coordinates, most_common_order, order_frequencies, candidate_names = test

    normalized_distances = get_distances_normalized(most_common_order, mds_1d_coordinates, candidate_names)
    
    return normalized_distances

def get_intervals(normalized_distances, ballots, candidates):

    n = len(candidates)
    print("getting intervals: ")
    normalized_names = []
    normalized_points = []
    for candidate in normalized_distances:
        normalized_names.append(candidate)
        normalized_points.append(normalized_distances[candidate])
    temp = {}
    i = 0
    for candidate in normalized_distances:
        temp[candidate] = i
        i += 1
    non_bullet = {}
    bullet = {}
    for ballot in ballots:
        if len(ballot) == 0:
            continue
        ballot_num = []
        for candidate in ballot:
            ballot_num.append(temp[candidate])
        
        consistency = evaluate_ballot_consistency(ballot_num)
        if consistency[0] is True:
            point = consistency[1]
            first_place = ballot[0]
            if len(ballot) == 1:
                if normalized_distances[ballot[0]] not in bullet:
                    bullet[normalized_distances[ballot[0]]] = 0
                bullet[normalized_distances[ballot[0]]] += ballots[ballot]

            elif normalized_distances[first_place] == 0:
                i = normalized_names.index(first_place)
                center = normalized_distances[first_place] + (normalized_distances[normalized_names[i + 1]] - normalized_distances[first_place])/4
                width = (normalized_distances[normalized_names[i + 1]] - normalized_distances[first_place])/2

            elif normalized_distances[first_place] == n - 1:
                i = normalized_names.index(first_place)
                center = normalized_distances[first_place] - (normalized_distances[first_place] - normalized_distances[normalized_names[i - 1]])/4
                width = (normalized_distances[first_place] - normalized_distances[normalized_names[i - 1]])/2
                
            else:
                if point < normalized_distances[first_place]:
                    i = normalized_names.index(first_place)
                    center = normalized_distances[first_place] - (normalized_distances[first_place] - normalized_distances[normalized_names[i - 1]])/4
                    width = (normalized_distances[first_place] - normalized_distances[normalized_names[i - 1]])/2
                else:
                    i = normalized_names.index(first_place)
                    center = normalized_distances[first_place] + (normalized_distances[normalized_names[i + 1]] - normalized_distances[first_place])/4
                    width = (normalized_distances[normalized_names[i + 1]] - normalized_distances[first_place])/2
            
            if len(ballot) > 1:
                if (center, width) not in non_bullet:
                    non_bullet[(center, width)] = 0
                non_bullet[(center, width)] += ballots[ballot]
            
    points = {}

    for t in non_bullet:
 
        if t[0] not in points:
            points[t[0]] = 0
        points[t[0]] += non_bullet[t]

    for p in bullet:
        if p not in points:
            points[p] = 0
        points[p] += bullet[p]
    
    data = []
    for t in non_bullet:
        center = t[0]
        width = t[1]
        low = center - (width/2)
        high = center + (width/2)
        y = non_bullet[t]
        print(center, " ", width, " ", low, " ", high)
        sample_size = y
        chunk_size = width/y
        for i in range(y):
            data.append(low+(i*chunk_size))
    for p in bullet:
        center = p
        width = 0.2
        low = center - (width/2)
        high = center + (width/2)
        y = bullet[p]
        print(center, " ", bullet[p])
        sample_size = y
        chunk_size = width/y
        for i in range(y):
            data.append(low+(i*chunk_size))

    data_frequency = Counter(data)
    data_with_y_values = {x: data_frequency[x] for x in set(data)}
    
    return data, data_with_y_values

def save_plots(data, normalized_distances, filename, ignore=False):

    print("saving the plots")
    normalized_names = []
    normalized_points = []
    for candidate in normalized_distances:
        normalized_names.append(candidate)
        normalized_points.append(normalized_distances[candidate])

    # Plot histogram
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=50, density=True, alpha=0.7)
    plt.title('Histogram of Data')
    plt.xticks(normalized_points, normalized_names, rotation=45)
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.grid(True)
    if (ignore):
        file_path = "team_arrow/clean/Histograms_ignored/" + filename[0:-4] + ".png"
    else:
        file_path = "team_arrow/clean/Histograms/" + filename[0:-4] + ".png"
    plt.savefig(file_path,  dpi=600, bbox_inches='tight')
    #plt.show()

    # Plot kernal density estimation
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data, fill=True)
    plt.title('Kernel Density Estimation of Data')
    plt.xticks(normalized_points, normalized_names, rotation=45)
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.grid(True)
    if (ignore):
        file_path = "team_arrow/clean/KDE_ignored/" + filename[0:-4] + ".png"  
    else:  
        file_path = "team_arrow/clean/KDE/" + filename[0:-4] + ".png"
    plt.savefig(file_path,  dpi=600, bbox_inches='tight')
    #plt.show()


def main():
    filename = "Alaska_08162022_HouseofRepresentativesSpecial.csv"
    file = "rcv_elections_database/classic/" + filename
    ballots, candidates = parse_election_data(file)
    normalized_distances = pefrom_MDS(file, True)
    data, data_with_y_values = get_intervals(normalized_distances, ballots, candidates)

    keys = np.array(list(data_with_y_values.keys()))
    values = np.array(list(data_with_y_values.values()))
    mat_data = np.column_stack((keys, values))
    mat_file = "team_arrow/clean/data/" + filename[0:-4]+".mat"
    scipy.io.savemat(mat_file, mdict={'my_data': mat_data})

    save_plots(data, normalized_distances, filename,ignore=True)

main()
