import json
import pickle

import os

with open("projects/SantaClauseIsComingToTown.pkl", 'rb') as file:
    project_dict = pickle.load(file)

for a in project_dict["tape"]:
    for uuid, value in a.items():
        print(uuid, value)


        



