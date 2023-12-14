import pickle

with open("projects/EdoTest.pkl", 'rb') as file:
    project_dict = pickle.load(file)

for k, v in project_dict["tracks"].items():
    
    for kk, vv in v.items():
        print(kk, vv)

    print("\n")