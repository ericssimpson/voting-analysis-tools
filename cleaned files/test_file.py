"""
Author          : Phousawanh
Last edited     : 2024-06-27
Description     : Simulation Experiments    
"""

import seaborn as sns
from scipy.stats import kurtosis, skew
from rcv_distribution import *
from MDS_analysis import *
from voting_rules import *
from consistency import *

from votekit.cvr_loaders import load_csv
from votekit.elections import IRV
from votekit.cleaning import remove_noncands
from votekit.pref_profile import PreferenceProfile

import votekit.ballot_generator as bg
from votekit import PreferenceInterval
from votekit.ballot import Ballot
from fractions import Fraction
import matplotlib.pyplot as plt


ballot = Ballot(ranking = [{"A"}, {"B"}, {"C"}], weight = 1)
print(ballot)

candidates = ["Moon", "Chris", "Duane"]

ballot1 = Ballot(ranking = [{"Duane"}, {"Chris"}, {"Moon"}], weight = 47)
ballot2 = Ballot(ranking = [{"Moon"}, {"Chris"}, {"Moon"}], weight = 22/7)
ballot3 = Ballot(ranking = [{"Moon","Duane"}, {"Chris"}], weight = 3)
print(ballot1)
print(ballot2)
print(ballot3)

candidates = ["A", "B", "C"]

# let's assume that the ballots come from voters, so they all have integer weight for now
ballots = [Ballot(ranking = [{"A"}, {"B"}, {"C"}],weight=3),
           Ballot(ranking = [{"B"}, {"A"}, {"C"}]),
           Ballot(ranking = [{"C"}, {"B"}, {"A"}]),
           Ballot(ranking = [{"A"}, {"B"}, {"C"}]),
           Ballot(ranking = [{"A"}, {"B"}, {"C"}]),
           Ballot(ranking = [{"B"}, {"A"}, {"C"}])]

# we give the profile a list of ballots and a list of candidates
profile = PreferenceProfile(ballots = ballots,
                            candidates = candidates)

print(profile)

profile.condense_ballots()
print(profile)

bloc_voter_prop = {"W": .8, "C": .2}

# the values of .9 indicate that these blocs are highly polarized;
# they prefer their own candidates much more than the opposing slate
cohesion_parameters = {"W": {"W":.9, "C":.1},
                        "C": {"C":.9, "W":.1}}

alphas = {"W": {"W":2, "C":1},
          "C": {"W":1, "C":.5}}

slate_to_candidates = {"W": ["W1", "W2", "W3"],
                        "C": ["C1", "C2"]}

cs = bg.CambridgeSampler.from_params(slate_to_candidates=slate_to_candidates,
          bloc_voter_prop=bloc_voter_prop,
          cohesion_parameters=cohesion_parameters,
          alphas=alphas)


profile = cs.generate_profile(number_of_ballots= 1000)
print(profile)

from votekit.plots import plot_MDS, compute_MDS
from votekit.metrics import earth_mover_dist, lp_dist
from votekit import PreferenceInterval

number_of_ballots = 100

slate_to_candidates = {"all_voters": ["A", "B", "C"]}

prefs1 = {"all_voters": {"all_voters": PreferenceInterval({"A": .8, "B":.15, "C":.05})}}
prefs2 = {"all_voters": {"all_voters": PreferenceInterval({"A": .1, "B":.5, "C":.4})}}

bloc_voter_prop = {"all_voters": 1}
cohesion_parameters = {"all_voters": {"all_voters": 1}}

pl1 = bg.name_PlackettLuce(slate_to_candidates = slate_to_candidates,
                      bloc_voter_prop = bloc_voter_prop,
                     pref_intervals_by_bloc = prefs1,
                     cohesion_parameters=cohesion_parameters)

pl2 = bg.name_PlackettLuce(slate_to_candidates = slate_to_candidates,
                      bloc_voter_prop = bloc_voter_prop,
                     pref_intervals_by_bloc = prefs2,
                     cohesion_parameters=cohesion_parameters)

bt1 = bg.name_BradleyTerry(slate_to_candidates = slate_to_candidates,
                      bloc_voter_prop = bloc_voter_prop,
                     pref_intervals_by_bloc = prefs1,
                     cohesion_parameters=cohesion_parameters)

bt2 = bg.name_BradleyTerry(slate_to_candidates = slate_to_candidates,
                      bloc_voter_prop = bloc_voter_prop,
                     pref_intervals_by_bloc = prefs2,
                     cohesion_parameters=cohesion_parameters)

# the data is a dictionary whose keys correspond to data labels
# and whose values are lists of PreferenceProfiles
coord_dict = compute_MDS(data =
                         {'pl1': [pl1.generate_profile(number_of_ballots)
                                         for i in range(10)],
                        'pl2': [pl2.generate_profile(number_of_ballots)
                                for i in range(10)],
                        'bt1': [bt1.generate_profile(number_of_ballots)
                                for i in range(10)],
                        'bt2': [bt2.generate_profile(number_of_ballots)
                                for i in range(10)],
                          },
            distance = lp_dist)


# we pass the computed coordinates, as well as a nested dictionary of plot parameters
# that will be passed to matplotlib scatter
ax = plot_MDS(coord_dict=coord_dict,
                plot_kwarg_dict={"pl1":{"c": "red", "s": 50, "marker": "x"},
                                 "pl2":{"c": "red", "s": 50, "marker": "o"},
                                 "bt1":{"c": "blue", "s": 50, "marker": "x"},
                                 "bt2":{"c": "blue", "s": 50, "marker": "o"}},
                legend = True, title = True)
plt.show()