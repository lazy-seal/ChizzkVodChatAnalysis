import json
import csv
from pprint import pprint
import pandas as pd
import httpx
import asyncio
from pathlib import Path
from Crawler import load_user_info, logger
from InfoDataObjects import UserInfo
import time
from functools import wraps

def drop_csv_column(path:str | Path, column_name: str):
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

async def example():
    async with httpx.AsyncClient() as client:
        uinfo = await load_user_info(client, "b2fcc309d14c98ee241be56a488eac32")
        pprint(uinfo.get_dict())

def print_func_when_called(show_args=False):
    """
    Prints the decorated function's name and arguments (if exists and show_args is set to True) when it's called
    """
    def decorator(func):
        @wraps(func)    # this makes sure that the wrapped function keeps its __name__ and __doc__
        def wrapper(*args, **kwargs):
            print(f"(CALLED): {func.__qualname__}")
            if show_args:
                if args:
                    pprint(f"\t(ARGS): {args!r}")
                if kwargs:
                    pprint(f"\t(KWARGS): {kwargs!r}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
        
            
if __name__ == "__main__":
    start = time.time()
    # asyncio.run(add_users_from_chat())
    asyncio.run(example())
    print(time.time() - start)