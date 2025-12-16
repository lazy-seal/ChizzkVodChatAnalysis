import json
import csv
from pprint import pprint
import pandas as pd
import httpx
import asyncio
from pathlib import Path
from Crawler import update_user_info, load_user_info, save_user_info_to_csv, logger
from InfoDataObjects import UserInfo
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

async def add_users_from_chat():
    limit_max = 500
    limit_left = limit_max
    videos = []
    with open(f"Raw Data\\videos.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            videos.append((row["video_streamer_name"], row["video_number"]))
        
        # ok this might be the worst code I've ever written
        async with httpx.AsyncClient() as client:
            all_users = {}
            to_store = {}
            for videotuple in videos:
                print(f"Looking at: Raw Data\\Chats\\{videotuple[0]}_{videotuple[1]}_chats.csv")
                logger.info(f"Looking at: Raw Data\\Chats\\{videotuple[0]}_{videotuple[1]}_chats.csv")
                
                with open(f"Raw Data\\Chats\\{videotuple[0]}_{videotuple[1]}_chats.csv", "r", encoding="utf-8") as chatfile:
                    reader = csv.DictReader(chatfile)
                    for row in reader:
                        try:
                            if not row["chat_user_channel_id"] or row["chat_user_channel_id"] in all_users:
                                continue
                            
                            limit_left -= 1
                            if limit_left <= 0:
                                limit_left = limit_max
                                print(f"limit reached: saving {len(to_store)} users and sleeps for 30 sec")
                                save_user_info_to_csv(to_store.values()) # type: ignore
                                to_store = {}
                                time.sleep(30)
                                
                            user_info = await load_user_info(client, row["chat_user_channel_id"])
                            to_store[user_info.user_channel_id] = user_info
                            all_users[user_info.user_channel_id] = user_info
                            
                        except Exception as e:
                            print(f"Exception Occured: {e}")
                            print(f"Saving {len(to_store)} users and and sleeps for 10 minutes")
                            save_user_info_to_csv(to_store.values()) # type: ignore
                            to_store = {}
                            time.sleep(600)
                            
            print(f'All Chat Iterated: saving rest of the users: {len(to_store)}')
            save_user_info_to_csv(to_store.values()) # type: ignore
            
                                
            
if __name__ == "__main__":
    start = time.time()
    asyncio.run(add_users_from_chat())
    print(time.time() - start)

    # df = pd.read_csv("Raw Data\\users.csv", encoding="utf-8")
    # df = df.drop(columns=["abc"])
    # df.to_csv("Raw Data\\users.csv", index=False, encoding="utf-8")