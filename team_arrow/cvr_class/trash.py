import parser 
import pandas as pd
import itertools
import numpy as np
import os 
import matplotlib.pyplot as plt
import seaborn as sns
from voting_rules import voting_rules as vr
import rcv_dimensionality
from sklearn.linear_model import LinearRegression

no_condorcet = 0
ballots, candidates = parser.parser("team_arrow/dataverse_files/Alaska_11082022_HouseDistrict11.csv")
election = vr(ballots, candidates)
print(election.condorcet())