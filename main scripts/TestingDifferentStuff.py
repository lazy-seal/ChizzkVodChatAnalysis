import json
from pprint import pprint
import pandas as pd
import httpx
import asyncio
from pathlib import Path
from Crawler import update_user_info
import time

def drop_column(path:str | Path, column_name: str):
    df = pd.read_csv(path, encoding="utf-8")
    df = df.drop(columns=["column_name"])
    df.to_csv(path, index=False, encoding="utf-8")

def print_data_structure(data, indent=0):
    """Recursively prints only the keys of a nested dictionary."""
    if not isinstance(data, dict) and not isinstance(data, list):
        print("  " * indent + str(type(data)))
    elif isinstance(data, dict):
        for key, value in data.items():
            print("  " * indent + str(key))
            print_data_structure(value, indent + 1)
    else:
        print("  " * (indent + 1) + f"[list]")
        if len(data) > 0:
            print_data_structure(data[0], indent + 2)

            
if __name__ == "__main__":
    start = time.time()
    asyncio.run(update_user_info(True))
    print(time.time() - start)

    # df = pd.read_csv("Raw Data\\users.csv", encoding="utf-8")
    # df = df.drop(columns=["abc"])
    # df.to_csv("Raw Data\\users.csv", index=False, encoding="utf-8")