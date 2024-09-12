import seaborn as sns

from scipy.stats import kurtosis, skew

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


def perform_MDS(csv, ignore=True):
    # Test the function with a custom CSV file
    ballots, candidates = parse_election_data(csv)
    list_freq = frequency(ballots, candidates)
    ignore_values = ['(WRITE-IN)', 'WRITE-IN', 'writein', 'Write-In', 'Write-in', 'skipped', 'overvote', 'Undeclared', 'undervote', 'Write in']
    if ignore:
        for (candidate, freq) in list_freq:
            if freq < 4:
                print("ignored: ", candidate, ": ", freq)
                ignore_values.append(candidate)

        ballots, candidates = parse_election_data(csv, ignore_values=ignore_values)

    # Perform the RCV analysis
    test = perform_rcv_analysis(csv, n_runs=1000, ignore_values=ignore_values)
    mds_1d_coordinates, mds_2d_coordinates, most_common_order, order_frequencies, candidate_names = test

    # Print the normalized distances between candidates and plot the MDS analysis
    normalized_distances = get_distances_normalized(most_common_order, mds_1d_coordinates, candidate_names)
    print("Normalized distances:", normalized_distances)
    plot_rcv_analysis(mds_1d_coordinates, mds_2d_coordinates, most_common_order, order_frequencies, candidate_names)

    # Get the consistency points for the bimodality analysis
    points = get_consistency_points(ballots, candidates, normalized_distances)

    # Create a list of data points
    data_points = []
    for key, value in points.items():
        data_points.extend([key] * value)

    # Convert to numpy array
    data_points = np.array(data_points)

    # Prepare data for histogram
    data_list = [x for x, count in points.items() for _ in range(count)]
   

    normalized_points = []
    normalized_names = []
    for name in normalized_distances:
        normalized_names.append(name)
        normalized_points.append(normalized_distances[name])

    # Plot histogram
    plt.figure(figsize=(10, 6))
    plt.hist(data_list, bins=50, density=True, alpha=0.7)
    plt.title('Histogram of Data')
    plt.xticks(normalized_points, normalized_names, rotation=45)
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.grid(True)
    plt.show()

    # Plot kernal density estimation
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data_list, fill=True)
    plt.title('Kernel Density Estimation of Data')
    plt.xticks(normalized_points, normalized_names, rotation=45)
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.grid(True)
    plt.show()

    #ballots, candidates = parse_election_data(csv)

    # Calculate skewness and kurtosis
    g = skew(data_points)
    k = kurtosis(data_points)

    # Calculate bimodality coefficient
    n = len(data_points)
    bimodality = (g**2 + 1) / (k + 3 * (n-1)**2 / ((n-2) * (n-3)))
    print("Bimodality coefficient:", bimodality)
    print("Gamma coefficiet:", get_gamma(normalized_distances, ballots))
    print("data list: ", data_list)


