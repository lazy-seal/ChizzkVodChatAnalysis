import json
from pprint import pprint
import pandas as pd

if __name__ == "__main__":

    with open("Private//private.json", encoding="utf-8") as f:
        private = json.load(f)
        pprint(private)
    
    df = pd.read_csv("Raw Data\\streamers.csv", encoding="utf-8")
    df = df.drop(columns=["Unnamed: 0"])
    df.to_csv("Raw Data\\streamers.csv", index=False, encoding="utf-8")
    
    
        
