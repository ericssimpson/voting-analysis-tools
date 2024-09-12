import numpy as np

def ballot_names_to_nums(ballots, candidate_names, order_frequencies):
    """
    Convert ballot names to numerical representation based on candidate order.

    Parameters
    ----------
    ballots : dict
        A dictionary containing ballot names as keys and associated order information.

    candidate_names : list
        A list of candidate names in the order they are to be represented numerically.

    order_frequencies : list
        A list containing order frequencies information, typically obtained from voting data.

    Returns
    -------
    tuple
        A tuple containing two elements:
        - ballot_nums : numpy.ndarray
            A 2D array representing numerical order of candidates for each ballot.
        - candidate_names_order : numpy.ndarray
            An array of candidate names in the order they are numerically represented.

    Notes
    -----
    This function takes a dictionary of ballots, a list of candidate names, and order frequencies
    to convert the ballot names to numerical representation based on the given candidate order.

    The resulting `ballot_nums` array has dimensions (number of ballots, number of candidates),
    where each row represents a ballot with numerical order of candidates.

    The `candidate_names_order` array represents the numerical order of candidate names as obtained
    from the order frequencies.
    """
    v_large_num = 100000
    candidate_names_order = np.array(candidate_names)[np.array(order_frequencies[0][0]).astype(int)]#[::-1]
    ballot_name_orders = list(ballots.keys())

    ballot_nums = v_large_num*np.ones((len(ballot_name_orders), len(candidate_names)), dtype=int)
    order_transform = np.array(order_frequencies[0][0]).astype(int)

    for i in range(len(ballot_name_orders)):
        ballot_names = np.array(ballot_name_orders[i])
        for j in range(len(candidate_names)):
            ballot_names[ballot_names == candidate_names_order[j]] = j
        ballot_names = ballot_names.astype(int)
        ballot_num = v_large_num*np.ones(len(candidate_names), dtype=int)
        ballot_num[0:len(ballot_names)] = ballot_names
        ballot_nums[i,:] = ballot_num

    return ballot_nums, candidate_names_order


def get_candidate_pair_intervals(ballot_nums, normalized_distances):
    """
    Calculate the intervals of possible points where the ballot could lie on the 1D axis
    treating each candidate pair separately in a given ballot ordering

    Parameters
    ----------
    ballot_nums : numpy.ndarray
        A 2D array representing the numerical order of candidates for each ballot.

    normalized_distances : dict
        A dictionary containing normalized distances between candidate coordinates.

    Returns
    -------
    tuple
        A tuple containing two elements:
        - intervals : numpy.ndarray
            A 3D array representing intervals between candidate pairs for each ballot order.
        - cand_coords : numpy.ndarray
            An array of candidate coordinates obtained from normalized distances.

    Notes
    -----
    The resulting `intervals` array has dimensions (2, number of ballot orders, number of pairs),
    where each slice along the first dimension represents the lower and upper bounds of the interval
    for a specific pair.

    The `cand_coords` array represents candidate coordinates obtained from the provided
    normalized distances.

    """
    n_pairs = ballot_nums.shape[1]-1 # number of pairs that need to be compared per ballot
    n_ballot_orders = ballot_nums.shape[0] # number of ballots

    cand_coords = np.array(list(normalized_distances.values()))
    intervals = np.empty((2, n_ballot_orders, n_pairs))

    large_num = 1000
    for i in range(n_pairs):
        ballot_nums_pairs = ballot_nums[:,i:i+2].astype(int) # the astype int turns the np.inf to a large negative number

        # if 2nd pair element is inf
        sing_inf_inds = np.where((ballot_nums_pairs[:, 0]<large_num) & 
                                 (ballot_nums_pairs[:, 1]>large_num))[0]
        if i==0:
            cand_inds_left = ballot_nums_pairs[sing_inf_inds, 0]-1
            cand_inds_left[cand_inds_left<0] = cand_inds_left[cand_inds_left<0] + 1
            cand_inds_right = ballot_nums_pairs[sing_inf_inds, 0] + 1
            cand_inds_right[cand_inds_right>n_pairs] = cand_inds_right[cand_inds_right>n_pairs] - 1
            mean_first = (cand_coords[cand_inds_left] + cand_coords[ballot_nums_pairs[sing_inf_inds, 0]])/2.
            mean_second =(cand_coords[cand_inds_right] + cand_coords[ballot_nums_pairs[sing_inf_inds, 0]])/2.
            #first_coord = cand_coords[ballot_nums_pairs[sing_inf_inds, 0]] - mean_first 
            #second_coord = cand_coords[ballot_nums_pairs[sing_inf_inds, 0]] + mean_second
            #intervals[:, sing_inf_inds, i] = [cand_coords[ballot_nums_pairs[sing_inf_inds, 0]],
            #                                   cand_coords[ballot_nums_pairs[sing_inf_inds, 0]]]
            intervals[:, sing_inf_inds, i] = np.vstack((mean_first, mean_second))
        else:
            intervals[:, sing_inf_inds, i] = np.reshape(np.array([-np.inf, np.inf]),(2,1))

        # if both pair elements are inf
        double_inf_inds = np.where((ballot_nums_pairs[:, 0]>large_num) 
                                 & (ballot_nums_pairs[:, 1]>large_num))[0]
        intervals[:, double_inf_inds, i] = np.reshape(np.array([-np.inf, np.inf]),(2,1))

        # if neither pair elements are inf and first is larger
        double_coord_inds = np.where((ballot_nums_pairs[:, 0]<large_num) & # 1st is not inf
                                     (ballot_nums_pairs[:, 1]<large_num) & # second is not inf
                                     (ballot_nums_pairs[:, 0]>ballot_nums_pairs[:, 1]))[0]
        first_coord = cand_coords[ballot_nums_pairs[double_coord_inds, 0]]
        second_coord = cand_coords[ballot_nums_pairs[double_coord_inds, 1]]
        mean_coord = (first_coord + second_coord)/2.
        intervals[:, double_coord_inds, i] = np.vstack((mean_coord, max(cand_coords)*np.ones(len(mean_coord))))

        # if neither pair elements are inf and first is smaller
        double_coord_inds = np.where((ballot_nums_pairs[:, 0]<large_num) &
                                     (ballot_nums_pairs[:, 1]<large_num) &
                                     (ballot_nums_pairs[:, 0]<ballot_nums_pairs[:, 1]))[0]
        first_coord = cand_coords[ballot_nums_pairs[double_coord_inds, 0]]
        second_coord = cand_coords[ballot_nums_pairs[double_coord_inds, 1]]
        mean_coord = (first_coord + second_coord)/2.
        intervals[:, double_coord_inds, i] = np.vstack((np.zeros(len(mean_coord)), mean_coord))

    return intervals, cand_coords

def get_ballot_coords(ballots, intervals, cand_coords, n_points=500):
    """
    Generate coordinates and weights for ballot distributions.

    Parameters
    ----------
    ballots : dict
        A dictionary containing ballot names as keys and associated order information.

    intervals : numpy.ndarray
        A 3D array representing intervals between candidate pairs for each ballot order.

    cand_coords : numpy.ndarray
        An array of candidate coordinates obtained from normalized distances.

    n_points : int, optional
        The number of points to generate along the coordinate axis. Default is 500.

    Returns
    -------
    tuple
        A tuple containing two elements:
        - points_all : numpy.ndarray
            An array of coordinate points representing the smooth distribution.
        - weights_all : numpy.ndarray
            An array of weights corresponding to each coordinate point.

    Notes
    -----
    This function generates ballot distributions by considering
    intervals between candidate pairs for each ballot order. It uses a specified number of
    points along the coordinate axis to create a smooth distribution.

    The resulting `points_all` array contains coordinate points, and the `weights_all` array
    contains weights corresponding to each coordinate point. The weights are calculated based
    on the number of ballot orders and the density of points in the intervals.
    """

    axis = np.linspace(min(cand_coords), max(cand_coords), n_points)

    points_all = np.array([])
    weights_all = np.array([])
    for i in range(len(ballots)):
        intervals_seq = np.reshape(intervals[:,i,:].T, (len(cand_coords)-1,2))
        intersect = find_interval_intersection(intervals_seq)

        if intersect is not None:
            if min(intersect) != max(intersect):
                inds_ax_pts = np.where((axis >= min(intersect)) & (axis <= (max(intersect))))[0]
            else:
                inds_ax_pts =  np.argmin(np.abs(axis - min(intersect)))
            points = np.atleast_1d(axis[inds_ax_pts])
            num_ballot_order = list(ballots.values())[i]
            weights = num_ballot_order*np.ones(len(points))/len(points)
            points_all = np.concatenate((points_all, points))
            weights_all = np.concatenate((weights_all, weights))
    weights_all = weights_all/np.sum(weights_all)

    return points_all, weights_all


def find_interval_intersection(intervs):
    """
    Find the intersection of a list of intervals.

    Parameters
    ----------
    intervs : list of tuples
        A list of intervals represented as tuples (start, end).

    Returns
    -------
    tuple or None
        If there is an intersection, returns a tuple representing the intersection interval (start, end).
        If there is no intersection or the input list has less than two intervals, returns None.

    Notes
    -----
    This function takes a list of intervals and finds their intersection. The intervals are represented as
    tuples of start and end points.

    The input list `intervs` is sorted based on the start points of the intervals. The function iterates
    through the sorted intervals, updating the intersection interval accordingly.

    If there is no intersection or the input list has less than two intervals, the function returns None.
    """

    if len(intervs) < 2:
        return None  # Cannot find intersection with less than two intervals

    # Sort intervals based on their start points
    sorted_intervals = sorted(intervs, key=lambda x: x[0])

    # Initialize the intersection with the first interval
    intersection = sorted_intervals[0]

    # Iterate over the sorted intervals and update the intersection
    for interval in sorted_intervals[1:]:
        if intersection[1] >= interval[0]:
            # Update the start and end points of the intersection
            intersection = (max(intersection[0], interval[0]), min(intersection[1], interval[1]))
        else:
            return None  # No intersection

    return intersection